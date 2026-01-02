from backend.abe.cpabe_utils import encrypt_aes_key, decrypt_aes_key
import pytest

def test_cpabe():
    # Fake AES key (32 bytes)
    aes_key = b"0123456789abcdef0123456789abcdef"

    # Access policy
    policy = "role:admin AND dept:IT"

    # Encrypt AES key using CP-ABE
    encrypted_key = encrypt_aes_key(aes_key, policy)

    # Valid user attributes
    valid_user = {
        "attributes": {
            "role:admin",
            "dept:IT",
            "clearance:high"
        }
    }

    # Invalid user attributes
    invalid_user = {
        "attributes": {
            "role:user",
            "dept:HR"
        }
    }

    decrypted_key = decrypt_aes_key(encrypted_key, valid_user)
    assert decrypted_key == aes_key

    with pytest.raises(Exception):
        decrypt_aes_key(encrypted_key, invalid_user)

if __name__ == "__main__":
    test_cpabe()
