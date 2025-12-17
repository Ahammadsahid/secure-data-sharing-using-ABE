from backend.abe.cpabe_utils import encrypt_aes_key, decrypt_aes_key

def test_cpabe():
    print("🔐 CP-ABE TEST STARTED")

    # Fake AES key (32 bytes)
    aes_key = b"0123456789abcdef0123456789abcdef"

    # Access policy
    policy = "role:admin AND dept:IT"

    # Encrypt AES key using CP-ABE
    encrypted_key = encrypt_aes_key(aes_key, policy)

    # ✅ VALID user attributes
    valid_user = {
        "attributes": {
            "role:admin",
            "dept:IT",
            "clearance:high"
        }
    }

    # ❌ INVALID user attributes
    invalid_user = {
        "attributes": {
            "role:user",
            "dept:HR"
        }
    }

    # ---- VALID ACCESS TEST ----
    try:
        decrypted_key = decrypt_aes_key(encrypted_key, valid_user)
        assert decrypted_key == aes_key
        print("✅ PASS: Access granted with valid attributes")
    except Exception:
        print("❌ FAIL: Valid user was denied")

    # ---- INVALID ACCESS TEST ----
    try:
        decrypt_aes_key(encrypted_key, invalid_user)
        print("❌ FAIL: Invalid user got access")
    except Exception:
        print("✅ PASS: Access denied for invalid attributes")

if __name__ == "__main__":
    test_cpabe()
