"""
PacketConn - asyncio-based packet connection for Spot messaging.

Provides a simple interface for exchanging encrypted packets with peers.
"""

import asyncio
from dataclasses import dataclass
from typing import TYPE_CHECKING, Tuple

from .proto import Message, MsgFlag

if TYPE_CHECKING:
    from .client import Client


@dataclass
class SpotAddr:
    """
    Address type for Spot protocol.

    Represents a spot address (typically k.<hash>/endpoint).
    """
    address: str

    def __str__(self) -> str:
        return self.address


@dataclass
class PacketInfo:
    """Information about a received packet."""
    body: bytes
    addr: SpotAddr


class PacketConn:
    """
    Asyncio-based packet connection for Spot messaging.

    Provides ReadFrom/WriteTo style interface for exchanging encrypted
    packets with peers without managing the underlying protocol details.

    Usage:
        conn = await client.listen_packet("my_endpoint")

        # Receive packets
        data, addr = await conn.read_from()

        # Send packets
        await conn.write_to(b"response", addr)

        # Clean up
        await conn.close()
    """

    def __init__(self, client: "Client", endpoint: str):
        """
        Initialize PacketConn.

        Args:
            client: Parent client instance
            endpoint: Endpoint name for receiving messages
        """
        self._client = client
        self._endpoint = endpoint
        self._buffer: asyncio.Queue[PacketInfo] = asyncio.Queue(maxsize=16)
        self._closed = False

        # Register handler
        self._client.set_handler(endpoint, self._handle_message)

    async def _handle_message(self, msg: Message) -> Tuple[bytes | None, Exception | None]:
        """Handle incoming messages."""
        if not msg.is_encrypted():
            return None, Exception("invalid message: must be encrypted")

        await self._buffer.put(PacketInfo(
            body=msg.body,
            addr=SpotAddr(msg.sender)
        ))
        return None, None

    async def read_from(self, timeout: float | None = None) -> Tuple[bytes, SpotAddr]:
        """
        Read a packet from the connection.

        Args:
            timeout: Optional timeout in seconds

        Returns:
            Tuple of (data, source_address)

        Raises:
            asyncio.TimeoutError: If timeout expires
            RuntimeError: If connection is closed
        """
        if self._closed:
            raise RuntimeError("PacketConn is closed")

        if timeout is not None:
            pkt = await asyncio.wait_for(self._buffer.get(), timeout=timeout)
        else:
            pkt = await self._buffer.get()

        return pkt.body, pkt.addr

    async def write_to(self, data: bytes, addr: SpotAddr | str) -> int:
        """
        Write a packet to the connection.

        Args:
            data: Data to send
            addr: Destination address (SpotAddr or string)

        Returns:
            Number of bytes sent

        Raises:
            RuntimeError: If connection is closed
        """
        if self._closed:
            raise RuntimeError("PacketConn is closed")

        if isinstance(addr, SpotAddr):
            target = addr.address
        else:
            target = addr

        await self._client.send_to(target, data, sender=f"/{self._endpoint}")
        return len(data)

    def local_addr(self) -> SpotAddr:
        """Get the local endpoint address."""
        return SpotAddr(f"{self._client.target_id}/{self._endpoint}")

    async def close(self) -> None:
        """Close the connection."""
        if self._closed:
            return

        self._closed = True
        self._client.set_handler(self._endpoint, None)

    @property
    def closed(self) -> bool:
        """Check if connection is closed."""
        return self._closed
