"""
Spot client - main API for the Spot messaging protocol.
"""

import asyncio
import base64
import hashlib
import logging
import struct
import sys
import traceback
from datetime import datetime
from typing import Callable, Awaitable, Any, Union
from uuid import uuid4

import cbor2
import httpx
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.hazmat.backends import default_backend

from pybottle import (
    new_bottle, new_opener, new_idcard, Keychain, IDCard,
    sign as pybottle_sign, encode_public_key,
)
from pybottle.pkix import key_to_bytes

from .proto import (
    Message, MsgFlag, HandshakeRequest, HandshakeResponse,
    PacketType, make_packet
)
from .connection import Connection
from .store import DiskStore, PrivateKey

logger = logging.getLogger(__name__)

# Type alias for message handlers
MessageHandler = Callable[[Message], Awaitable[tuple[bytes | None, Exception | None]]]


class Client:
    """
    Spot client for connecting to and communicating through the Spot network.

    This is the main API for the library, providing methods to:
    - Connect to Spot servers
    - Send and receive encrypted messages
    - Query remote endpoints
    - Manage identity cards
    - Store and retrieve encrypted blobs
    """

    def __init__(
        self,
        private_key: PrivateKey | None = None,
        keychain: Keychain | None = None,
        metadata: dict[str, str] | None = None,
        store: DiskStore | None = None,
    ):
        """
        Initialize the Spot client.

        Args:
            private_key: Private key for signing/encryption. If not provided,
                        will attempt to load from store or generate ephemeral key.
            keychain: Keychain with multiple keys. If provided, first signer is used.
            metadata: Optional metadata to include in identity card.
            store: DiskStore for persistent key storage.
        """
        self._keychain = keychain or Keychain()
        self._metadata = metadata or {}
        self._store = store
        self._ephemeral = False

        # Determine the signing key
        if private_key is not None:
            self._keychain.add_key(private_key)
            self._signer = private_key
        elif self._keychain.first_signer() is not None:
            self._signer = self._keychain.first_signer()
        elif store is not None and store.has_keys():
            key = store.get_or_create_key()
            self._keychain.add_key(key)
            self._signer = key
        else:
            # Generate ephemeral key
            self._signer = ec.generate_private_key(ec.SECP256R1(), default_backend())
            self._keychain.add_key(self._signer)
            self._ephemeral = True

        # Create identity card
        self._idcard = new_idcard(self._signer.public_key())
        # Add decrypt purpose so server can encrypt responses to us
        self._idcard.add_key_purpose(self._signer.public_key(), "decrypt")
        if self._ephemeral:
            self._idcard.add_key_purpose(self._signer.public_key(), "ephemeral")

        # Sign the ID card (returns bytes directly)
        self._idcard_bin = self._idcard.sign(self._signer)

        # Connection management
        self._connections: dict[str, Connection] = {}
        self._connections_lock = asyncio.Lock()
        self._min_conn = 1
        self._online_count = 0
        self._online_event = asyncio.Event()

        # Message handling
        self._write_queue: asyncio.Queue[Message] = asyncio.Queue(maxsize=16)
        self._pending_responses: dict[str, asyncio.Future] = {}
        self._pending_lock = asyncio.Lock()
        self._handlers: dict[str, MessageHandler] = {}
        self._handlers_lock = asyncio.Lock()

        # ID card cache
        self._idcard_cache: dict[bytes, tuple[IDCard, float]] = {}
        self._idcard_cache_lock = asyncio.Lock()

        # Control
        self._running = False
        self._closed = False
        self._main_task: asyncio.Task | None = None
        self._write_task: asyncio.Task | None = None

        # Set up default handlers
        self._setup_default_handlers()

    def _setup_default_handlers(self) -> None:
        """Set up default message handlers."""
        async def ping_handler(msg: Message) -> tuple[bytes | None, Exception | None]:
            body = msg.body
            if len(body) > 128:
                body = body[:128]
            return body, None

        async def version_handler(msg: Message) -> tuple[bytes | None, Exception | None]:
            version = f"pyspotlib, Python {sys.version_info.major}.{sys.version_info.minor}"
            return version.encode("utf-8"), None

        async def finger_handler(msg: Message) -> tuple[bytes | None, Exception | None]:
            return self._idcard_bin, None

        async def check_update_handler(msg: Message) -> tuple[bytes | None, Exception | None]:
            # Emit check_update event - applications can listen for this
            logger.info("Received check_update request")
            return None, None

        async def idcard_update_handler(msg: Message) -> tuple[bytes | None, Exception | None]:
            # Process ID card update notifications from server
            if len(msg.body) == 0:
                return None, Exception("empty ID card data received")

            try:
                idc = IDCard.load(msg.body)
                # Get hash of the ID card's self key
                id_hash = hashlib.sha256(idc.self_key).digest()
                # Update cache
                self.set_idcard_cache(id_hash, idc)
                logger.info(f"Updated ID card in cache: k.{base64.urlsafe_b64encode(id_hash).rstrip(b'=').decode()}")
            except Exception as e:
                logger.error(f"Failed to parse ID card update: {e}")
                return None, Exception(f"invalid ID card format: {e}")

            return None, None

        self._handlers["ping"] = ping_handler
        self._handlers["version"] = version_handler
        self._handlers["finger"] = finger_handler
        self._handlers["check_update"] = check_update_handler
        self._handlers["idcard_update"] = idcard_update_handler

    @property
    def target_id(self) -> str:
        """
        Get the client's target ID in format 'k.<base64hash>'.

        This ID can be used by other clients to send messages to this client.
        """
        public_key_bytes = key_to_bytes(self._signer)
        hash_bytes = hashlib.sha256(public_key_bytes).digest()
        return "k." + base64.urlsafe_b64encode(hash_bytes).rstrip(b"=").decode("ascii")

    @property
    def idcard(self) -> IDCard:
        """Get the client's identity card."""
        return self._idcard

    @property
    def idcard_bin(self) -> bytes:
        """Get the client's signed identity card as bytes."""
        return self._idcard_bin

    def connection_count(self) -> tuple[int, int]:
        """
        Get connection counts.

        Returns:
            Tuple of (total_connections, online_connections)
        """
        return len(self._connections), self._online_count

    async def start(self) -> None:
        """Start the client and connect to Spot servers."""
        if self._running:
            return

        self._running = True
        self._closed = False

        # Start main connection thread
        self._main_task = asyncio.create_task(self._main_loop())
        self._write_task = asyncio.create_task(self._write_loop())

    async def close(self) -> None:
        """Close the client and all connections."""
        if self._closed:
            return

        self._closed = True
        self._running = False

        # Cancel tasks
        if self._main_task:
            self._main_task.cancel()
        if self._write_task:
            self._write_task.cancel()

        # Close all connections
        async with self._connections_lock:
            for conn in self._connections.values():
                await conn.close()
            self._connections.clear()

    async def wait_online(self, timeout: float | None = None) -> bool:
        """
        Wait until at least one connection is online.

        Args:
            timeout: Maximum time to wait in seconds, or None for no timeout.

        Returns:
            True if online, False if timeout occurred.
        """
        if self._online_count > 0:
            return True

        try:
            await asyncio.wait_for(self._online_event.wait(), timeout=timeout)
            return True
        except asyncio.TimeoutError:
            return False

    async def query(
        self,
        target: str,
        body: bytes,
        timeout: float = 30.0
    ) -> bytes:
        """
        Send a query and wait for response.

        Args:
            target: Target address (e.g., "k.<hash>/endpoint" or "@/system_endpoint")
            body: Message body
            timeout: Timeout in seconds

        Returns:
            Response body

        Raises:
            asyncio.TimeoutError: If timeout occurs
            Exception: If error response received
        """
        # Get recipient ID card if this is encrypted (k. targets)
        # All messages are signed, but only k. targets are encrypted
        rid: IDCard | None = None
        if target.startswith("k."):
            rid = await self.get_idcard_for_recipient(target)

        # Always sign the message, encrypt if rid is provided
        body = self._prepare_message(rid, body)

        # Create message
        msg_id = uuid4()
        msg = Message(
            message_id=msg_id,
            flags=0,
            sender=f"/{msg_id}",
            recipient=target,
            body=body,
        )

        # Create future for response
        future: asyncio.Future[Message] = asyncio.get_event_loop().create_future()
        async with self._pending_lock:
            self._pending_responses[str(msg_id)] = future

        try:
            # Send message
            await self._write_queue.put(msg)

            # Wait for response
            response = await asyncio.wait_for(future, timeout=timeout)

            # Decode response if encrypted
            if (response.flags & MsgFlag.NOT_BOTTLE) == 0:
                response.body = self._decode_message(rid, response.body)

            # Check for error
            if response.flags & MsgFlag.ERROR:
                raise Exception(response.body.decode("utf-8"))

            return response.body

        finally:
            async with self._pending_lock:
                self._pending_responses.pop(str(msg_id), None)

    async def send_to(
        self,
        target: str,
        payload: bytes,
        sender: str | None = None
    ) -> None:
        """
        Send a message without waiting for response.

        Args:
            target: Target address
            payload: Message payload
            sender: Optional custom sender address
        """
        rid = await self.get_idcard_for_recipient(target)
        body = self._prepare_message(rid, payload)

        msg_id = uuid4()
        if sender is None:
            sender = f"/{msg_id}"
        elif not sender.startswith("/"):
            raise ValueError("Sender address must start with /")

        msg = Message(
            message_id=msg_id,
            flags=0,
            sender=sender,
            recipient=target,
            body=body,
        )

        await self._write_queue.put(msg)

    def set_handler(self, endpoint: str, handler: MessageHandler | None) -> None:
        """
        Set a message handler for an endpoint.

        Args:
            endpoint: Endpoint name
            handler: Handler function, or None to remove handler
        """
        if handler is None:
            self._handlers.pop(endpoint, None)
        else:
            self._handlers[endpoint] = handler

    async def get_idcard(self, hash_bytes: bytes) -> IDCard:
        """
        Get ID card for a given hash.

        Args:
            hash_bytes: SHA-256 hash of the public key

        Returns:
            IDCard for the target
        """
        # Check cache
        async with self._idcard_cache_lock:
            if hash_bytes in self._idcard_cache:
                return self._idcard_cache[hash_bytes][0]

        # Fetch from server
        data = await self.query("@/idcard_find", hash_bytes)
        idc = IDCard.load(data)

        # Cache it
        async with self._idcard_cache_lock:
            if len(self._idcard_cache) > 1024:
                self._idcard_cache.clear()
            self._idcard_cache[hash_bytes] = (idc, asyncio.get_event_loop().time())

        return idc

    async def get_idcard_for_recipient(self, recipient: str) -> IDCard:
        """
        Get ID card for a recipient address.

        Args:
            recipient: Recipient in format "k.<base64hash>/endpoint"

        Returns:
            IDCard for the recipient
        """
        # Parse recipient
        rcv = recipient
        if "/" in rcv:
            rcv = rcv.split("/", 1)[0]

        parts = rcv.split(".")
        if len(parts) < 2 or parts[0] != "k":
            raise ValueError(f"Invalid recipient format: {recipient}")

        # Decode hash (last part after k.)
        hash_b64 = parts[-1]
        # Add padding if needed
        padding = 4 - (len(hash_b64) % 4)
        if padding != 4:
            hash_b64 += "=" * padding
        hash_bytes = base64.urlsafe_b64decode(hash_b64)

        return await self.get_idcard(hash_bytes)

    async def get_time(self) -> datetime:
        """
        Get server time.

        Returns:
            Server timestamp
        """
        data = await self.query("@/time", b"")
        if len(data) < 12:
            raise ValueError("Invalid time response")

        unix_sec = struct.unpack(">Q", data[:8])[0]
        nanos = struct.unpack(">I", data[8:12])[0]

        return datetime.fromtimestamp(unix_sec + nanos / 1e9)

    async def store_blob(self, key: str, value: bytes) -> None:
        """
        Store an encrypted blob.

        Args:
            key: Blob key
            value: Blob value (will be encrypted)
        """
        if len(value) == 0:
            # Delete
            await self.query("@/store_blob", (key + "\x00").encode("utf-8"))
            return

        # Create bottle and encrypt
        bottle = new_bottle(value)
        bottle.encrypt(self._idcard)
        bottle.bottle_up()
        bottle.sign(self._signer)

        # Serialize
        buf = bottle.to_cbor()

        # Store
        await self.query("@/store_blob", (key + "\x00").encode("utf-8") + buf)

    async def fetch_blob(self, key: str) -> bytes:
        """
        Fetch an encrypted blob.

        Args:
            key: Blob key

        Returns:
            Decrypted blob value
        """
        buf = await self.query("@/fetch_blob", key.encode("utf-8"))

        # Open bottle
        opener = new_opener(self._signer)
        data, result = opener.open_cbor(buf)

        # Verify signature
        if not result.signed_by(self._idcard):
            raise ValueError("Blob was not signed by us")
        if result.decryption_count == 0:
            raise ValueError("Blob was not encrypted")

        return data

    async def get_group_members(self, group_key: bytes) -> list[str]:
        """
        Get list of members in a group.

        Args:
            group_key: Group key bytes

        Returns:
            List of member target IDs
        """
        buf = await self.query("@/group_list", group_key)
        members = []
        for i in range(0, len(buf), 32):
            h = buf[i:i+32]
            members.append("k." + base64.urlsafe_b64encode(h).rstrip(b"=").decode("ascii"))
        return members

    async def get_idcard_bin(self, hash_bytes: bytes) -> bytes:
        """
        Get raw ID card bytes for a given hash.

        Args:
            hash_bytes: SHA-256 hash of the public key

        Returns:
            Raw ID card bytes (signed bottle)
        """
        return await self.query("@/idcard_find", hash_bytes)

    async def query_timeout(
        self,
        timeout: float,
        target: str,
        body: bytes,
    ) -> bytes:
        """
        Send a query with explicit timeout.

        Args:
            timeout: Timeout in seconds
            target: Target address
            body: Message body

        Returns:
            Response body
        """
        return await self.query(target, body, timeout=timeout)

    def listen_packet(self, endpoint: str) -> "PacketConn":
        """
        Create a packet connection for easy packet-based messaging.

        Args:
            endpoint: Endpoint name for receiving messages

        Returns:
            PacketConn instance

        Usage:
            conn = client.listen_packet("my_endpoint")
            data, addr = await conn.read_from()
            await conn.write_to(b"response", addr)
            await conn.close()
        """
        from .packetconn import PacketConn
        return PacketConn(self, endpoint)

    def set_idcard_cache(self, hash_bytes: bytes, idcard: IDCard) -> None:
        """
        Manually set an ID card in the cache.

        Args:
            hash_bytes: SHA-256 hash of the public key
            idcard: The ID card to cache
        """
        asyncio.create_task(self._set_cache_async(hash_bytes, idcard))

    async def _set_cache_async(self, hash_bytes: bytes, idcard: IDCard) -> None:
        async with self._idcard_cache_lock:
            self._idcard_cache[hash_bytes] = (idcard, asyncio.get_event_loop().time())

    # Internal methods

    def _prepare_message(self, rid: IDCard | None, payload: bytes) -> bytes:
        """Encrypt and sign a message for sending."""
        bottle = new_bottle(payload)
        if rid is not None:
            bottle.encrypt(rid)
            bottle.bottle_up()
        bottle.sign(self._signer)
        return bottle.to_cbor()

    def _decode_message(self, rid: IDCard | None, payload: bytes) -> bytes:
        """Decrypt and verify a received message."""
        opener = new_opener(self._signer)
        data, result = opener.open_cbor(payload)

        if rid is not None:
            if result.decryption_count == 0:
                raise ValueError("Expected encrypted message")
            if not result.signed_by(rid):
                self._clear_idcard_cache()
                raise ValueError("Message not signed by expected sender")

        return data

    def _clear_idcard_cache(self) -> None:
        """Clear the ID card cache (called when signature verification fails)."""
        asyncio.create_task(self._clear_cache_async())

    async def _clear_cache_async(self) -> None:
        async with self._idcard_cache_lock:
            self._idcard_cache.clear()

    def _create_handshake_response(self, req: HandshakeRequest) -> HandshakeResponse:
        """Create handshake response by signing the request."""
        # Get public key in PKIX format
        public_key_bytes = self._signer.public_key().public_bytes(
            encoding=serialization.Encoding.DER,
            format=serialization.PublicFormat.SubjectPublicKeyInfo
        )

        # Sign the raw request data
        signature = pybottle_sign(self._signer, req.raw)

        return HandshakeResponse(
            id=self._idcard_bin,
            key=public_key_bytes,
            sig=signature,
        )

    def _handle_groups(self, groups: list[bytes]) -> None:
        """Handle group membership updates from server."""
        # Re-sign ID card with updated groups
        # Note: pybottle IDCard doesn't have direct group support like Go version
        # For now, just re-sign the ID card
        self._idcard_bin = self._idcard.sign(self._signer)

    def _on_connection_online(self, conn: Connection) -> None:
        """Called when a connection completes handshake."""
        self._online_count += 1
        if self._online_count == 1:
            self._online_event.set()
        logger.info(f"Connection online: {conn.hostname} (total: {self._online_count})")

    def _on_connection_offline(self, conn: Connection) -> None:
        """Called when a connection goes offline."""
        self._online_count = max(0, self._online_count - 1)
        if self._online_count == 0:
            self._online_event.clear()
        logger.info(f"Connection offline: {conn.hostname} (total: {self._online_count})")

    async def _main_loop(self) -> None:
        """Main loop for connection management."""
        logger.debug("Client main loop started")

        # Initial connection
        try:
            await self._run_connect()
        except Exception as e:
            logger.error(f"Initial connection failed: {e}")

        # Periodic maintenance
        while self._running:
            try:
                await asyncio.sleep(30)

                # Check connection count
                if len(self._connections) < self._min_conn:
                    await self._run_connect()

            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in main loop: {e}")

    async def _write_loop(self) -> None:
        """Loop for sending outgoing messages."""
        while self._running:
            try:
                msg = await asyncio.wait_for(
                    self._write_queue.get(),
                    timeout=1.0
                )

                # Find an online connection to send through
                conn = self._get_online_connection()
                if conn:
                    await conn.send_message(msg)
                else:
                    logger.warning("No online connection available to send message")

            except asyncio.TimeoutError:
                continue
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in write loop: {e}")

    def _get_online_connection(self) -> Connection | None:
        """Get an online connection for sending."""
        for conn in self._connections.values():
            if conn.online:
                return conn
        return None

    async def _run_connect(self) -> None:
        """Establish connections to Spot servers."""
        hosts, min_conn = await self._get_hosts()

        if min_conn == 0:
            min_conn = len(hosts)
        self._min_conn = min_conn

        # Limit to 10 hosts
        if len(hosts) > 10:
            hosts = hosts[:10]

        for host in hosts:
            async with self._connections_lock:
                if host in self._connections:
                    continue

                logger.debug(f"Connecting to {host}")
                conn = Connection(self, host, self._handle_message)
                self._connections[host] = conn

            # Connect in background
            asyncio.create_task(self._connect_host(conn))

            # Small delay between connections
            await asyncio.sleep(2)

    async def _connect_host(self, conn: Connection) -> None:
        """Connect to a single host with retry logic."""
        max_failures = 10

        while self._running and conn.fail_count < max_failures:
            if await conn.connect():
                return

            await asyncio.sleep(2)

        # Give up on this host
        async with self._connections_lock:
            self._connections.pop(conn.hostname, None)

    async def _get_hosts(self) -> tuple[list[str], int]:
        """Get list of available Spot servers."""
        async with httpx.AsyncClient() as client:
            response = await client.get(
                "https://ws.atonline.com/_special/rest/Spot:connect",
                timeout=30.0
            )
            response.raise_for_status()
            data = response.json()

            if "data" in data:
                data = data["data"]

            hosts = data.get("hosts", [])
            min_conn = data.get("min_conn", 0)

            return hosts, min_conn

    async def _handle_message(self, msg: Message) -> None:
        """Handle an incoming message."""
        # Extract endpoint from recipient
        endpoint = msg.get_endpoint()

        # Check if this is a response to a pending query
        async with self._pending_lock:
            future = self._pending_responses.get(endpoint)
            if future is not None and not future.done():
                future.set_result(msg)
                return

        # Look for handler
        handler = self._handlers.get(endpoint)
        if handler is not None:
            asyncio.create_task(self._run_handler(msg, handler))
        else:
            logger.warning(f"No handler for endpoint: {endpoint}")

    async def _run_handler(self, msg: Message, handler: MessageHandler) -> None:
        """Run a message handler with error handling."""
        try:
            # Decrypt message if needed
            rid: IDCard | None = None
            if msg.is_encrypted():
                try:
                    rid = await self.get_idcard_for_recipient(msg.sender)
                    msg.body = self._decode_message(rid, msg.body)
                except Exception as e:
                    logger.error(f"Failed to decode message: {e}")
                    return

            # Run handler
            try:
                result, error = await handler(msg)
            except Exception as e:
                logger.error(f"Handler error: {e}\n{traceback.format_exc()}")
                result = str(e).encode("utf-8")
                error = e

            # Don't respond to responses
            if msg.is_response():
                return

            # Prepare response
            if result is None and error is None:
                return

            flags = MsgFlag.RESPONSE
            if error is not None:
                flags |= MsgFlag.ERROR
                result = str(error).encode("utf-8")

            # Encrypt response if original was encrypted
            if msg.is_encrypted() and rid is not None:
                result = self._prepare_message(rid, result)

            response = Message(
                message_id=msg.message_id,
                flags=flags,
                recipient=msg.sender,
                sender="/noreply",
                body=result,
            )

            await self._write_queue.put(response)

        except Exception as e:
            logger.error(f"Error running handler: {e}\n{traceback.format_exc()}")


async def new_client(
    private_key: PrivateKey | None = None,
    keychain: Keychain | None = None,
    metadata: dict[str, str] | None = None,
    store: DiskStore | None = None,
    auto_start: bool = True,
) -> Client:
    """
    Create and optionally start a new Spot client.

    Args:
        private_key: Private key for signing/encryption
        keychain: Keychain with multiple keys
        metadata: Optional metadata for identity card
        store: DiskStore for persistent key storage
        auto_start: Whether to automatically start the client

    Returns:
        Configured Client instance
    """
    client = Client(
        private_key=private_key,
        keychain=keychain,
        metadata=metadata,
        store=store,
    )

    if auto_start:
        await client.start()

    return client
