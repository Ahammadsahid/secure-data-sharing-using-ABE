import base64
from cryptography.fernet import Fernet


def generate_master_key():
    """
    Simulated CP-ABE master key
    """
    return Fernet.generate_key()


def generate_user_key(master_key, attributes):
    """
    Simulated attribute-based private key
    """
    return {
        "master_key": master_key,
        "attributes": set(attributes)
    }


def policy_satisfied(attributes, policy):
    """
    Simple policy evaluator
    Example policy: 'role:admin AND dept:IT'
    """
    policy_parts = policy.replace("(", "").replace(")", "").split("AND")
    policy_parts = [p.strip() for p in policy_parts]

    return all(p in attributes for p in policy_parts)


def encrypt_aes_key(aes_key: bytes, policy: str):
    """
    Encrypt AES key with policy
    """
    fernet_key = Fernet.generate_key()
    fernet = Fernet(fernet_key)

    encrypted_key = fernet.encrypt(aes_key)

    return {
        "encrypted_key": encrypted_key,
        "policy": policy,
        "fernet_key": fernet_key
    }


def decrypt_aes_key(ciphertext, user_key):
    """
    Decrypt AES key only if attributes satisfy policy
    """
    if not policy_satisfied(user_key["attributes"], ciphertext["policy"]):
        raise Exception("Access Denied: Attributes do not satisfy policy")

    fernet = Fernet(ciphertext["fernet_key"])
    return fernet.decrypt(ciphertext["encrypted_key"])
