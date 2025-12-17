from cpabe_utils import (
    generate_master_key,
    generate_user_key,
    encrypt_aes_key,
    decrypt_aes_key
)


def test_valid_attributes():
    master_key = generate_master_key()
    attributes = ["role:admin", "dept:IT", "clearance:high"]

    user_key = generate_user_key(master_key, attributes)

    aes_key = b"MY_AES_SECRET_KEY"
    policy = "role:admin AND dept:IT"

    ciphertext = encrypt_aes_key(aes_key, policy)
    decrypted = decrypt_aes_key(ciphertext, user_key)

    assert decrypted == aes_key
    print("PASS: Access granted with valid attributes")


def test_invalid_attributes():
    master_key = generate_master_key()
    attributes = ["role:user", "dept:HR"]

    user_key = generate_user_key(master_key, attributes)

    aes_key = b"MY_AES_SECRET_KEY"
    policy = "role:admin AND dept:IT"

    ciphertext = encrypt_aes_key(aes_key, policy)

    try:
        decrypt_aes_key(ciphertext, user_key)
        print("FAIL: Access should not be granted")
    except Exception:
        print("PASS: Access denied for invalid attributes")


if __name__ == "__main__":
    test_valid_attributes()
    test_invalid_attributes()
