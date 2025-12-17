"""
Custom DNS resolver for g-dns.net domains.

g-dns.net domains encode IP addresses in base32 format, allowing direct
resolution without actual DNS queries.
"""

import base64
import socket
from typing import Tuple


# RFC 4648 base32 alphabet (no padding)
B32_ALPHABET = "ABCDEFGHIJKLMNOPQRSTUVWXYZ234567"


def decode_base32_ip(encoded: str) -> str | None:
    """
    Decode a base32-encoded IP address.

    Args:
        encoded: Base32-encoded IP (7 chars for IPv4, 26 chars for IPv6)

    Returns:
        IP address string, or None if invalid
    """
    encoded = encoded.upper()

    # Add padding if needed for base32 decoding
    padding = (8 - len(encoded) % 8) % 8
    encoded_padded = encoded + "=" * padding

    try:
        data = base64.b32decode(encoded_padded)
    except Exception:
        return None

    if len(data) == 4:
        # IPv4
        return socket.inet_ntop(socket.AF_INET, data)
    elif len(data) == 16:
        # IPv6
        return socket.inet_ntop(socket.AF_INET6, data)
    else:
        return None


def resolve_gdns(host: str) -> list[str] | None:
    """
    Resolve a g-dns.net hostname to IP addresses.

    Format: <base32-ipv4>.g-dns.net
            <base32-ipv4>-<base32-ipv6>.g-dns.net
            <base32-ipv6>.g-dns.net

    Args:
        host: Hostname to resolve

    Returns:
        List of IP addresses, or None to fall back to regular DNS
    """
    host_lower = host.lower()

    if not host_lower.endswith(".g-dns.net"):
        return None

    # Remove the .g-dns.net suffix
    encoded = host_lower[:-10]  # len(".g-dns.net") = 10

    results = []

    # Split on hyphen for multiple IPs
    parts = encoded.split("-")

    for part in parts:
        if not part:
            continue

        ip = decode_base32_ip(part)
        if ip is None:
            # Invalid encoding, fall back to regular DNS
            return None
        results.append(ip)

    if not results:
        return None

    return results


def resolve_host(host: str) -> list[str]:
    """
    Resolve a hostname, handling g-dns.net specially.

    Args:
        host: Hostname to resolve

    Returns:
        List of IP addresses
    """
    # Try g-dns.net resolution first
    gdns_result = resolve_gdns(host)
    if gdns_result is not None:
        return gdns_result

    # Fall back to regular DNS
    try:
        info = socket.getaddrinfo(host, None, socket.AF_UNSPEC, socket.SOCK_STREAM)
        return list(set(addr[4][0] for addr in info))
    except socket.gaierror:
        return []


def get_websocket_uri(host: str) -> Tuple[str, list[str]]:
    """
    Get WebSocket URI and resolved IPs for a host.

    Args:
        host: Server hostname

    Returns:
        Tuple of (wss URI, list of resolved IPs)
    """
    ips = resolve_host(host)
    uri = f"wss://{host}/_websocket"
    return uri, ips
