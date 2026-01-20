import os
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives import padding
from cryptography.hazmat.backends import default_backend


def generate_aes_key():
    """
    Generates a 256-bit (32-byte) AES key
    """
    return os.urandom(32)


def encrypt_blob(file_bytes: bytes, key: bytes) -> bytes:
    """Encrypt file bytes into a single storable blob.

    Format (AES-CBC): iv(16) + ciphertext
    """
    iv, ciphertext = encrypt_file(file_bytes, key)
    return iv + ciphertext


def decrypt_blob(encrypted_blob: bytes, key: bytes) -> bytes:
    """Decrypt a storable blob produced by encrypt_blob.

    Format (AES-CBC): iv(16) + ciphertext
    """
    if len(encrypted_blob) < 16:
        raise ValueError("Invalid AES-CBC blob")
    iv = encrypted_blob[:16]
    ciphertext = encrypted_blob[16:]
    return decrypt_file(ciphertext, key, iv)


def encrypt_file(file_bytes: bytes, key: bytes):
    """
    Encrypts file data using AES-256-CBC
    Returns (iv, ciphertext)
    """
    iv = os.urandom(16)

    padder = padding.PKCS7(128).padder()
    padded_data = padder.update(file_bytes) + padder.finalize()

    cipher = Cipher(
        algorithms.AES(key),
        modes.CBC(iv),
        backend=default_backend()
    )

    encryptor = cipher.encryptor()
    ciphertext = encryptor.update(padded_data) + encryptor.finalize()

    return iv, ciphertext


def decrypt_file(ciphertext: bytes, key: bytes, iv: bytes):
    """
    Decrypts AES-256 encrypted data (CBC)
    """
    cipher = Cipher(
        algorithms.AES(key),
        modes.CBC(iv),
        backend=default_backend()
    )

    decryptor = cipher.decryptor()
    padded_plaintext = decryptor.update(ciphertext) + decryptor.finalize()

    unpadder = padding.PKCS7(128).unpadder()
    plaintext = unpadder.update(padded_plaintext) + unpadder.finalize()

    return plaintext
