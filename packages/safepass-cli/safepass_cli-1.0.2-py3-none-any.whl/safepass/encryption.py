"""Encryption utilities for SafePass"""

import os
import hashlib
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC


def generate_salt():
    """Generate a random salt"""
    return os.urandom(32)


def derive_key_from_master_password(master_password: str, salt: bytes) -> bytes:
    """Derive encryption key from master password using PBKDF2"""
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=100000,
    )
    return kdf.derive(master_password.encode())


def hash_master_password(master_password: str, salt: bytes) -> str:
    """Hash master password for storage"""
    key = derive_key_from_master_password(master_password, salt)
    return hashlib.sha256(key).hexdigest()


def encrypt_data(data: str, key: bytes) -> bytes:
    """Encrypt data using AES-256-GCM"""
    aesgcm = AESGCM(key)
    nonce = os.urandom(12)
    ciphertext = aesgcm.encrypt(nonce, data.encode(), None)
    return nonce + ciphertext


def decrypt_data(encrypted_data: bytes, key: bytes) -> str:
    """Decrypt data using AES-256-GCM"""
    aesgcm = AESGCM(key)
    nonce = encrypted_data[:12]
    ciphertext = encrypted_data[12:]
    plaintext = aesgcm.decrypt(nonce, ciphertext, None)
    return plaintext.decode()


def verify_master_password(master_password: str, salt: bytes, stored_hash: str) -> bool:
    """Verify master password against stored hash"""
    computed_hash = hash_master_password(master_password, salt)
    return computed_hash == stored_hash
