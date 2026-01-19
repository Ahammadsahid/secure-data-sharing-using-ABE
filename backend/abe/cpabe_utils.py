import base64
from cryptography.fernet import Fernet


def generate_master_key():
    """Return a master key (demo)."""
    return Fernet.generate_key()


def generate_user_key(master_key, attributes):
    """Create a demo user key from a master key + attributes."""
    return {
        "master_key": master_key,
        "attributes": set(attributes)
    }


def policy_satisfied(attributes, policy):
    """Return True if attribute tokens satisfy the policy (supports AND/OR)."""
    def _normalize_token(token: str) -> str:
        return (token or "").strip().lower()

    def _variants(token: str):
        t = _normalize_token(token)
        if t.startswith("department:"):
            return {t, "dept:" + t.split(":", 1)[1]}
        if t.startswith("dept:"):
            return {t, "department:" + t.split(":", 1)[1]}
        return {t}

    # Normalize attribute set (case-insensitive)
    normalized_attrs = {_normalize_token(a) for a in (attributes or set())}

    # Remove extra spaces
    policy = (policy or "").replace("  ", " ")
    
    # Split by AND first (AND has lower precedence)
    and_parts = policy.split(" AND ")
    
    for and_part in and_parts:
        and_part = and_part.strip()
        
        # Remove parentheses if present
        if and_part.startswith("(") and and_part.endswith(")"):
            and_part = and_part[1:-1]
        
        # Split by OR (each OR part is an alternative)
        or_parts = and_part.split(" OR ")
        or_parts = [p.strip() for p in or_parts]
        
        # For this AND group, at least one OR part must match
        group_ok = False
        for part in or_parts:
            if _variants(part) & normalized_attrs:
                group_ok = True
                break
        if not group_ok:
            return False
    
    return True


def encrypt_aes_key(aes_key: bytes, policy: str):
    """Encrypt an AES key (gated by a policy string)."""
    fernet_key = Fernet.generate_key()
    fernet = Fernet(fernet_key)

    encrypted_key = fernet.encrypt(aes_key)

    return {
        "encrypted_key": encrypted_key,
        "policy": policy,
        "fernet_key": fernet_key
    }


def decrypt_aes_key(ciphertext, user_key):
    """Decrypt an AES key if the user's attributes satisfy the policy."""
    if not policy_satisfied(user_key["attributes"], ciphertext["policy"]):
        raise Exception("Access Denied: Attributes do not satisfy policy")

    fernet = Fernet(ciphertext["fernet_key"])
    return fernet.decrypt(ciphertext["encrypted_key"])
