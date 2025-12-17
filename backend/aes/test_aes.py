from aes_utils import generate_aes_key, encrypt_file, decrypt_file


def test_correct_key():
    data = b"Sensitive File Data"
    key = generate_aes_key()

    iv, encrypted = encrypt_file(data, key)
    decrypted = decrypt_file(encrypted, key, iv)

    assert decrypted == data
    print("PASS: Correct key decryption successful")


def test_wrong_key():
    data = b"Sensitive File Data"
    key = generate_aes_key()
    wrong_key = generate_aes_key()

    iv, encrypted = encrypt_file(data, key)

    try:
        decrypt_file(encrypted, wrong_key, iv)
        print("FAIL: Decryption should not succeed with wrong key")
    except Exception:
        print("PASS: Decryption failed with wrong key")


if __name__ == "__main__":
    test_correct_key()
    test_wrong_key()
