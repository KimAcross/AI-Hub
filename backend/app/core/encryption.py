"""Encryption utilities for sensitive data at rest."""

import base64
import hashlib
from typing import Optional

from cryptography.fernet import Fernet, InvalidToken

# Prefix to identify encrypted values
ENCRYPTED_PREFIX = "enc:"


def derive_key(secret_key: str) -> bytes:
    """Derive a Fernet-compatible key from the application secret key.

    Uses SHA256 to derive a 32-byte key, then base64 encodes it for Fernet.
    """
    key_bytes = hashlib.sha256(secret_key.encode()).digest()
    return base64.urlsafe_b64encode(key_bytes)


def encrypt_value(plaintext: str, secret_key: str) -> str:
    """Encrypt a plaintext value.

    Args:
        plaintext: The value to encrypt
        secret_key: The application secret key

    Returns:
        Encrypted value with 'enc:' prefix
    """
    key = derive_key(secret_key)
    fernet = Fernet(key)
    encrypted = fernet.encrypt(plaintext.encode())
    return f"{ENCRYPTED_PREFIX}{encrypted.decode()}"


def decrypt_value(ciphertext: str, secret_key: str) -> str:
    """Decrypt an encrypted value.

    Args:
        ciphertext: The encrypted value (with or without 'enc:' prefix)
        secret_key: The application secret key

    Returns:
        Decrypted plaintext value

    Raises:
        InvalidToken: If decryption fails (wrong key or corrupted data)
    """
    if ciphertext.startswith(ENCRYPTED_PREFIX):
        ciphertext = ciphertext[len(ENCRYPTED_PREFIX):]

    key = derive_key(secret_key)
    fernet = Fernet(key)
    decrypted = fernet.decrypt(ciphertext.encode())
    return decrypted.decode()


def is_encrypted(value: str) -> bool:
    """Check if a value is encrypted (has the enc: prefix)."""
    return value.startswith(ENCRYPTED_PREFIX)


def encrypt_if_needed(value: Optional[str], secret_key: str) -> Optional[str]:
    """Encrypt a value only if it's not already encrypted.

    Args:
        value: The value to encrypt (may be None or already encrypted)
        secret_key: The application secret key

    Returns:
        Encrypted value or None if input was None
    """
    if value is None:
        return None
    if is_encrypted(value):
        return value
    return encrypt_value(value, secret_key)


def decrypt_if_needed(value: Optional[str], secret_key: str) -> Optional[str]:
    """Decrypt a value only if it's encrypted.

    Args:
        value: The value to decrypt (may be None, encrypted, or plaintext)
        secret_key: The application secret key

    Returns:
        Decrypted value, original plaintext, or None if input was None
    """
    if value is None:
        return None
    if not is_encrypted(value):
        return value
    return decrypt_value(value, secret_key)
