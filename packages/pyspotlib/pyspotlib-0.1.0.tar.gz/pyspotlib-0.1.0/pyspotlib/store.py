"""
Disk-based key storage for Spot client.
"""

import os
from pathlib import Path
from typing import Union

from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import ec, rsa, ed25519
from cryptography.hazmat.backends import default_backend


PrivateKey = Union[ec.EllipticCurvePrivateKey, rsa.RSAPrivateKey, ed25519.Ed25519PrivateKey]


class DiskStore:
    """
    Persistent key storage on disk.

    Stores keys in PEM format at a configurable path.
    Default path is ~/.config/spot/
    """

    DEFAULT_PATH = Path.home() / ".config" / "spot"

    def __init__(self, path: Path | str | None = None):
        """
        Initialize disk store.

        Args:
            path: Directory path for key storage. Uses ~/.config/spot/ if not specified.
        """
        if path is None:
            self.path = self.DEFAULT_PATH
        else:
            self.path = Path(path)

        self._keys: list[PrivateKey] = []
        self._ensure_directory()
        self._load_keys()

    def _ensure_directory(self) -> None:
        """Ensure the storage directory exists with proper permissions."""
        if not self.path.exists():
            self.path.mkdir(parents=True, mode=0o700)

    def _load_keys(self) -> None:
        """Load all keys from the storage directory."""
        if not self.path.exists():
            return

        for key_file in self.path.glob("id_*.key"):
            try:
                key = self._load_key_file(key_file)
                if key is not None:
                    self._keys.append(key)
            except Exception:
                # Skip invalid key files
                pass

    def _load_key_file(self, path: Path) -> PrivateKey | None:
        """Load a single key file."""
        with open(path, "rb") as f:
            pem_data = f.read()

        try:
            return serialization.load_pem_private_key(
                pem_data,
                password=None,
                backend=default_backend()
            )
        except Exception:
            return None

    def _save_key(self, key: PrivateKey, name: str) -> None:
        """Save a key to disk."""
        pem_data = key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.PKCS8,
            encryption_algorithm=serialization.NoEncryption()
        )

        # Find unique filename
        key_path = self.path / f"id_{name}.key"
        if key_path.exists():
            i = 1
            while True:
                key_path = self.path / f"id_{name}_{i}.key"
                if not key_path.exists():
                    break
                i += 1

        with open(key_path, "wb") as f:
            f.write(pem_data)

        # Set restrictive permissions
        os.chmod(key_path, 0o600)

    def get_or_create_key(self) -> PrivateKey:
        """
        Get existing key or create a new one.

        Returns the first available key, or generates a new ECDSA P-256 key
        if no keys exist.
        """
        if self._keys:
            return self._keys[0]

        # Generate new ECDSA P-256 key
        key = ec.generate_private_key(ec.SECP256R1(), default_backend())
        self._keys.append(key)
        self._save_key(key, "ecdsa")

        return key

    def add_key(self, key: PrivateKey, name: str | None = None) -> None:
        """
        Add a key to the store.

        Args:
            key: Private key to add
            name: Optional name for the key file (without id_ prefix and .key suffix)
        """
        self._keys.append(key)

        if name is None:
            if isinstance(key, ec.EllipticCurvePrivateKey):
                name = "ecdsa"
            elif isinstance(key, rsa.RSAPrivateKey):
                name = "rsa"
            elif isinstance(key, ed25519.Ed25519PrivateKey):
                name = "ed25519"
            else:
                name = "unknown"

        self._save_key(key, name)

    def get_keys(self) -> list[PrivateKey]:
        """Get all stored keys."""
        return self._keys.copy()

    def has_keys(self) -> bool:
        """Check if any keys are stored."""
        return len(self._keys) > 0

    def keychain(self) -> "Keychain":
        """
        Get a Keychain containing all stored keys.

        Returns:
            Keychain with all keys from this store
        """
        from pybottle import Keychain
        kc = Keychain()
        for key in self._keys:
            kc.add_key(key)
        return kc

    def first_signer(self) -> PrivateKey | None:
        """Get the first available signing key."""
        return self._keys[0] if self._keys else None
