"""
Spot protocol message types - equivalent to spotproto in Go
"""

from dataclasses import dataclass, field
from enum import IntEnum
from uuid import UUID, uuid4
import io


class PacketType(IntEnum):
    """Packet type identifiers (lower 4 bits of first byte)"""
    PING_PONG = 0x0
    HANDSHAKE = 0x1
    INSTANT_MSG = 0x2


class MsgFlag(IntEnum):
    """Message flags for Spot protocol messages"""
    RESPONSE = 1 << 0    # This is a response that must not trigger further responses
    ERROR = 1 << 1       # Message body contains an error string
    NOT_BOTTLE = 1 << 2  # Bypasses E2E encryption


def encode_uvarint(value: int) -> bytes:
    """Encode an unsigned integer as a variable-length integer (uvarint)."""
    result = []
    while value >= 0x80:
        result.append((value & 0x7f) | 0x80)
        value >>= 7
    result.append(value)
    return bytes(result)


def decode_uvarint(reader: io.BufferedReader) -> int:
    """Decode a variable-length unsigned integer from a reader."""
    result = 0
    shift = 0
    while True:
        byte_data = reader.read(1)
        if not byte_data:
            raise ValueError("Unexpected end of data while reading uvarint")
        byte = byte_data[0]
        result |= (byte & 0x7f) << shift
        if byte < 0x80:
            break
        shift += 7
        if shift >= 64:
            raise ValueError("uvarint overflow")
    return result


@dataclass
class Message:
    """
    Spot protocol message structure.

    Corresponds to spotproto.Message in Go.
    Wire format:
    - 16 bytes: message ID (UUID bytes)
    - uvarint: flags
    - uvarint: recipient length
    - N bytes: recipient string (UTF-8)
    - uvarint: sender length
    - N bytes: sender string (UTF-8)
    - remaining: body
    """
    message_id: UUID = field(default_factory=uuid4)
    flags: int = 0
    recipient: str = ""
    sender: str = ""
    body: bytes = b""

    def is_encrypted(self) -> bool:
        """Check if message is encrypted (NOT_BOTTLE flag is not set)"""
        return (self.flags & MsgFlag.NOT_BOTTLE) == 0

    def is_response(self) -> bool:
        """Check if this is a response message"""
        return bool(self.flags & MsgFlag.RESPONSE)

    def is_error(self) -> bool:
        """Check if this is an error response"""
        return bool(self.flags & MsgFlag.ERROR)

    def to_bytes(self) -> bytes:
        """Serialize message to binary format."""
        recipient_bytes = self.recipient.encode("utf-8")
        sender_bytes = self.sender.encode("utf-8")

        return (
            self.message_id.bytes +
            encode_uvarint(self.flags) +
            encode_uvarint(len(recipient_bytes)) +
            recipient_bytes +
            encode_uvarint(len(sender_bytes)) +
            sender_bytes +
            self.body
        )

    @classmethod
    def from_bytes(cls, data: bytes) -> "Message":
        """Deserialize message from binary format."""
        if len(data) < 16:
            raise ValueError("Message data too short")

        reader = io.BytesIO(data)

        # Message ID (16 bytes)
        message_id = UUID(bytes=reader.read(16))

        # Flags (uvarint)
        flags = decode_uvarint(reader)

        # Recipient
        recipient_len = decode_uvarint(reader)
        if recipient_len > 256:
            raise ValueError("Recipient name too long")
        recipient = reader.read(recipient_len).decode("utf-8")

        # Sender
        sender_len = decode_uvarint(reader)
        if sender_len > 256:
            raise ValueError("Sender name too long")
        sender = reader.read(sender_len).decode("utf-8")

        # Body (remaining bytes)
        body = reader.read()

        return cls(
            message_id=message_id,
            flags=flags,
            recipient=recipient,
            sender=sender,
            body=body,
        )

    def get_endpoint(self) -> str:
        """
        Extract endpoint name from recipient address.

        For example, "k.abc123/endpoint" returns "endpoint"
        """
        if "/" not in self.recipient:
            return ""
        parts = self.recipient.split("/", 1)
        if len(parts) > 1:
            # Handle nested slashes - only get first part after first slash
            endpoint = parts[1]
            if "/" in endpoint:
                endpoint = endpoint.split("/", 1)[0]
            return endpoint
        return ""

    def create_response(self, body: bytes, error: bool = False) -> "Message":
        """Create a response message for this query."""
        flags = MsgFlag.RESPONSE
        if error:
            flags |= MsgFlag.ERROR

        return Message(
            message_id=self.message_id,
            flags=flags,
            recipient=self.sender,
            sender="/noreply",
            body=body,
        )


@dataclass
class HandshakeRequest:
    """
    Handshake request from server (CBOR encoded).

    Fields:
    - ready: bool - indicates handshake completion
    - server_code: str - short name of server
    - client_id: str - assigned connection identifier
    - nonce: bytes - random blob for authentication
    - groups: list[bytes] - groups the client belongs to
    """
    ready: bool = False
    server_code: str = ""
    client_id: str = ""
    nonce: bytes = b""
    groups: list[bytes] = field(default_factory=list)
    raw: bytes = b""  # Original CBOR data for signing

    @classmethod
    def from_cbor(cls, data: bytes) -> "HandshakeRequest":
        """Parse handshake request from CBOR data"""
        import cbor2
        obj = cbor2.loads(data)
        return cls(
            ready=obj.get("rdy", False),
            server_code=obj.get("srv", ""),
            client_id=obj.get("cid", ""),
            nonce=obj.get("rnd", b""),
            groups=obj.get("grp", []),
            raw=data,
        )


@dataclass
class HandshakeResponse:
    """
    Handshake response from client (CBOR encoded).

    Fields:
    - id: bytes - signed identity card
    - key: bytes - PKIX-encoded public key
    - sig: bytes - signature over the request
    """
    id: bytes = b""
    key: bytes = b""
    sig: bytes = b""

    def to_cbor(self) -> bytes:
        """Serialize to CBOR format"""
        import cbor2
        obj = {}
        if self.id:
            obj["id"] = self.id
        if self.key:
            obj["key"] = self.key
        if self.sig:
            obj["sig"] = self.sig
        return cbor2.dumps(obj)


def parse_packet(data: bytes, is_client: bool = True) -> tuple:
    """
    Parse a raw packet into the appropriate type.

    Returns (packet_type, packet_data) tuple.
    """
    if len(data) == 0:
        raise ValueError("Empty packet")

    version = (data[0] >> 4) & 0xf
    packet_type = data[0] & 0xf

    if version != 0:
        raise ValueError(f"Invalid protocol version: {version}")

    payload = data[1:]

    if packet_type == PacketType.PING_PONG:
        return (PacketType.PING_PONG, payload)
    elif packet_type == PacketType.HANDSHAKE:
        if is_client:
            return (PacketType.HANDSHAKE, HandshakeRequest.from_cbor(payload))
        else:
            raise NotImplementedError("Server-side handshake parsing not implemented")
    elif packet_type == PacketType.INSTANT_MSG:
        return (PacketType.INSTANT_MSG, Message.from_bytes(payload))
    else:
        raise ValueError(f"Unknown packet type: {packet_type}")


def make_packet(packet_type: PacketType, data: bytes) -> bytes:
    """Create a raw packet with the appropriate header byte."""
    header = packet_type & 0xf  # version 0, packet type in lower 4 bits
    return bytes([header]) + data
