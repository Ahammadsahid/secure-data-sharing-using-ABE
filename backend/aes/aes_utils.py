import os
from typing import Tuple
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.hazmat.primitives import padding
from cryptography.hazmat.backends import default_backend


_GCM_MAGIC = b"GCM1"
_GCM_NONCE_SIZE = 12  # 96-bit nonce is the recommended size for AES-GCM


def _encrypt_cbc(file_bytes: bytes, key: bytes) -> Tuple[bytes, bytes]:
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


def _decrypt_cbc(ciphertext: bytes, key: bytes, iv: bytes) -> bytes:
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


def generate_aes_key():
    """
    Generates a 256-bit (32-byte) AES key
    """
    return os.urandom(32)


def encrypt_blob(file_bytes: bytes, key: bytes) -> bytes:
    """Encrypt file bytes into a single storable blob.

    New format (AES-GCM): b"GCM1" + nonce(12) + ciphertext||tag
    Legacy format (AES-CBC): iv(16) + ciphertext  (handled only for decryption)
    """
    nonce = os.urandom(_GCM_NONCE_SIZE)
    aesgcm = AESGCM(key)
    ciphertext = aesgcm.encrypt(nonce, file_bytes, None)
    return _GCM_MAGIC + nonce + ciphertext


def decrypt_blob(encrypted_blob: bytes, key: bytes) -> bytes:
    """Decrypt a storable blob produced by encrypt_blob.

    Backward compatible: if the blob does not start with the GCM magic header,
    we treat it as the legacy AES-CBC format iv(16) + ciphertext.
    """
    if encrypted_blob.startswith(_GCM_MAGIC):
        if len(encrypted_blob) < len(_GCM_MAGIC) + _GCM_NONCE_SIZE + 16:
            raise ValueError("Invalid AES-GCM blob")
        nonce = encrypted_blob[len(_GCM_MAGIC):len(_GCM_MAGIC) + _GCM_NONCE_SIZE]
        ciphertext = encrypted_blob[len(_GCM_MAGIC) + _GCM_NONCE_SIZE:]
        return AESGCM(key).decrypt(nonce, ciphertext, None)

    # Legacy AES-CBC (iv + ciphertext)
    if len(encrypted_blob) < 16:
        raise ValueError("Invalid legacy AES-CBC blob")
    iv = encrypted_blob[:16]
    ciphertext = encrypted_blob[16:]
    return _decrypt_cbc(ciphertext, key, iv)


def encrypt_file(file_bytes: bytes, key: bytes):
    """
    Encrypts file data using AES-256-GCM (AEAD)
    Returns (nonce, ciphertext_with_tag)
    """
    nonce = os.urandom(_GCM_NONCE_SIZE)
    ciphertext = AESGCM(key).encrypt(nonce, file_bytes, None)
    return nonce, ciphertext


def decrypt_file(ciphertext: bytes, key: bytes, iv: bytes):
    """
    Decrypts AES-encrypted data.

    Prefer AES-GCM (AEAD). For compatibility with older call sites, if the
    parameters look like legacy AES-CBC (16-byte IV and block-aligned
    ciphertext), we attempt CBC first.
    """
    if isinstance(iv, (bytes, bytearray)) and len(iv) == 16 and (len(ciphertext) % 16 == 0):
        try:
            return _decrypt_cbc(ciphertext, key, iv)
        except Exception:
            pass

    return AESGCM(key).decrypt(iv, ciphertext, None)
