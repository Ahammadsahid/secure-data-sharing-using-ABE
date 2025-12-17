import os
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives import padding
from cryptography.hazmat.backends import default_backend


def generate_aes_key():
    """
    Generates a 256-bit (32-byte) AES key
    """
    return os.urandom(32)


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
    Decrypts AES-256 encrypted data
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
