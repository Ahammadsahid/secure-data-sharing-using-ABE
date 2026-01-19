import time
from backend.aes.aes_utils import generate_aes_key, encrypt_file, decrypt_file, encrypt_blob, decrypt_blob

def test_aes():
    data = b"This is a test file"
    key = generate_aes_key()

    start = time.time()
    iv, encrypted = encrypt_file(data, key)
    decrypted = decrypt_file(encrypted, key, iv)
    end = time.time()

    assert decrypted == data

    assert (end - start) >= 0


def test_blob_roundtrip_and_legacy_compat():
    data = b"blob test"
    key = generate_aes_key()

    blob = encrypt_blob(data, key)
    assert decrypt_blob(blob, key) == data

    # Legacy CBC format: iv(16) + ciphertext (produced by internal CBC helper)
    # We generate it through the public encrypt_file/decrypt_file compatibility
    # path by calling the internal CBC encrypt via a known pattern.
    from backend.aes import aes_utils as au
    iv, cbc_ct = au._encrypt_cbc(data, key)
    legacy_blob = iv + cbc_ct
    assert decrypt_blob(legacy_blob, key) == data

if __name__ == "__main__":
    test_aes()
