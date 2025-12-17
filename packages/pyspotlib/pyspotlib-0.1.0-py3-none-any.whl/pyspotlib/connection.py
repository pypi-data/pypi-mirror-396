"""
WebSocket connection management for Spot client.
"""

import asyncio
import logging
from typing import TYPE_CHECKING, Callable, Awaitable

import websockets
from websockets.asyncio.client import ClientConnection

from .proto import (
    Message, HandshakeRequest, HandshakeResponse,
    PacketType, parse_packet, make_packet
)

if TYPE_CHECKING:
    from .client import Client

logger = logging.getLogger(__name__)


class Connection:
    """
    Manages a single WebSocket connection to a Spot server.
    """

    def __init__(
        self,
        client: "Client",
        hostname: str,
        on_message: Callable[[Message], Awaitable[None]],
    ):
        """
        Initialize connection.

        Args:
            client: Parent client instance
            hostname: Server hostname to connect to
            on_message: Callback for received messages
        """
        self.client = client
        self.hostname = hostname
        self.on_message = on_message
        self._ws: ClientConnection | None = None
        self._online = False
        self._running = False
        self._write_queue: asyncio.Queue[bytes] = asyncio.Queue(maxsize=16)
        self._tasks: list[asyncio.Task] = []
        self._fail_count = 0
        self._client_id = ""

    @property
    def online(self) -> bool:
        """Check if connection has completed handshake."""
        return self._online

    @property
    def connected(self) -> bool:
        """Check if WebSocket is connected."""
        return self._ws is not None

    async def connect(self) -> bool:
        """
        Establish WebSocket connection and perform handshake.

        Returns:
            True if connection and handshake succeeded
        """
        url = f"wss://{self.hostname}/_websocket"

        try:
            self._ws = await asyncio.wait_for(
                websockets.connect(
                    url,
                    max_size=1024 * 1024,  # 1MB max message size
                ),
                timeout=30.0
            )
            self._running = True
            self._fail_count = 0

            # Perform handshake before starting normal operations
            if not await self._perform_handshake():
                await self.close()
                return False

            # Start read/write tasks
            self._tasks = [
                asyncio.create_task(self._read_loop()),
                asyncio.create_task(self._write_loop()),
            ]

            return True

        except Exception as e:
            logger.warning(f"Failed to connect to {self.hostname}: {e}")
            self._fail_count += 1
            return False

    async def close(self) -> None:
        """Close the connection."""
        self._running = False
        was_online = self._online
        self._online = False

        for task in self._tasks:
            task.cancel()

        if self._ws is not None:
            try:
                await self._ws.close()
            except Exception:
                pass
            self._ws = None

        self._tasks = []

        if was_online:
            self.client._on_connection_offline(self)

    async def send(self, data: bytes) -> None:
        """
        Queue data for sending.

        Args:
            data: Raw binary data to send
        """
        await self._write_queue.put(data)

    async def send_message(self, msg: Message) -> None:
        """
        Send a protocol message.

        Args:
            msg: Message to send
        """
        packet = make_packet(PacketType.INSTANT_MSG, msg.to_bytes())
        await self.send(packet)

    async def _read_loop(self) -> None:
        """Read incoming messages from WebSocket."""
        try:
            while self._running and self._ws is not None:
                try:
                    data = await self._ws.recv()

                    if isinstance(data, str):
                        data = data.encode("utf-8")

                    await self._handle_packet(data)

                except websockets.ConnectionClosed:
                    logger.info(f"Connection to {self.hostname} closed")
                    break
                except Exception as e:
                    logger.error(f"Error reading from {self.hostname}: {e}")
                    break

        finally:
            self._running = False
            if self._online:
                self._online = False
                self.client._on_connection_offline(self)

    async def _write_loop(self) -> None:
        """Write outgoing messages to WebSocket."""
        try:
            while self._running and self._ws is not None:
                try:
                    data = await asyncio.wait_for(
                        self._write_queue.get(),
                        timeout=1.0
                    )
                    await self._ws.send(data)
                except asyncio.TimeoutError:
                    continue
                except websockets.ConnectionClosed:
                    break
                except Exception as e:
                    logger.error(f"Error writing to {self.hostname}: {e}")
                    break

        finally:
            self._running = False

    async def _handle_packet(self, data: bytes) -> None:
        """Handle incoming packet after handshake is complete."""
        try:
            packet_type, packet = parse_packet(data, is_client=True)

            if packet_type == PacketType.HANDSHAKE:
                # Handle re-handshake (group updates)
                await self._handle_rehandshake(packet)
            elif packet_type == PacketType.INSTANT_MSG:
                await self.on_message(packet)
            elif packet_type == PacketType.PING_PONG:
                # Respond to ping with pong
                await self.send(make_packet(PacketType.PING_PONG, packet))

        except Exception as e:
            logger.error(f"Error handling packet: {e}")

    async def _perform_handshake(self) -> bool:
        """
        Perform initial handshake with server.

        Returns:
            True if handshake succeeded
        """
        try:
            while True:
                data = await asyncio.wait_for(
                    self._ws.recv(),
                    timeout=300.0  # 5 minute timeout for handshake
                )

                if isinstance(data, str):
                    data = data.encode("utf-8")

                packet_type, packet = parse_packet(data, is_client=True)

                if packet_type != PacketType.HANDSHAKE:
                    logger.warning(f"Expected handshake packet, got {packet_type}")
                    continue

                if packet.ready:
                    # Handshake complete
                    self._client_id = packet.client_id
                    self._online = True
                    logger.info(f"Handshake completed with {self.hostname}, client_id={self._client_id}")
                    self.client._on_connection_online(self)
                    return True

                # Handle groups if present
                if packet.groups:
                    self.client._handle_groups(packet.groups)

                # Generate response
                response = self.client._create_handshake_response(packet)

                # Send response
                response_packet = make_packet(PacketType.HANDSHAKE, response.to_cbor())
                await self._ws.send(response_packet)

        except asyncio.TimeoutError:
            logger.error(f"Handshake timeout with {self.hostname}")
            return False
        except Exception as e:
            logger.error(f"Handshake error with {self.hostname}: {e}")
            return False

    async def _handle_rehandshake(self, req: HandshakeRequest) -> None:
        """Handle re-handshake request (usually for group updates)."""
        if req.ready:
            return

        if req.groups:
            self.client._handle_groups(req.groups)

        response = self.client._create_handshake_response(req)
        response_packet = make_packet(PacketType.HANDSHAKE, response.to_cbor())
        await self.send(response_packet)

    @property
    def fail_count(self) -> int:
        """Get number of consecutive connection failures."""
        return self._fail_count
