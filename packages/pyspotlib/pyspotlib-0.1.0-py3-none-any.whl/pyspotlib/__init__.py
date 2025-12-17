"""
pyspotlib - Python client library for Spot messaging protocol

A Python port of the Go spotlib library, providing secure messaging
through the Spot network with end-to-end encryption.
"""

from .client import Client, new_client, MessageHandler
from .store import DiskStore
from .proto import Message, MsgFlag, PacketType
from .packetconn import PacketConn, SpotAddr

__version__ = "0.1.0"
__all__ = [
    "Client",
    "new_client",
    "DiskStore",
    "Message",
    "MsgFlag",
    "PacketType",
    "MessageHandler",
    "PacketConn",
    "SpotAddr",
]
