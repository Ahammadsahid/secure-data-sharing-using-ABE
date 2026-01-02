import time
from backend.aes.aes_utils import generate_aes_key, encrypt_file, decrypt_file

def test_aes():
    data = b"This is a test file"
    key = generate_aes_key()

    start = time.time()
    iv, encrypted = encrypt_file(data, key)
    decrypted = decrypt_file(encrypted, key, iv)
    end = time.time()

    assert decrypted == data

    assert (end - start) >= 0

if __name__ == "__main__":
    test_aes()
