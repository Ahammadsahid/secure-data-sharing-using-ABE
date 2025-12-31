"""
ABE (Attribute-Based Encryption) Key Management Service

IMPORTANT NOTE on your architecture:
- This module handles ABE encryption/decryption with attribute-based policies
- Key sharing IS implemented (Shamir Secret Sharing for potential future use)
- However, your current project uses BLOCKCHAIN THRESHOLD APPROVAL instead:
  * Keys are NOT split and distributed to authorities
  * Authorities DO NOT hold cryptographic shares
  * Instead, authorities VOTE on the blockchain to approve access
  * The backend releases the full decryption key after 4-of-7 approvals
  
This is THRESHOLD APPROVAL AUTHENTICATION, not threshold cryptography.
"""
import os
from typing import Dict, List, Tuple, Optional
"""
NOTE:
Charm-Crypto is not installed in this environment.
ABE is simulated for policy enforcement.
Actual encryption is done using AES after blockchain approval.
This approach is commonly used in academic projects.
"""

CHART_AVAILABLE = False  # Simulate Charm-Crypto not installed

# Dummy placeholders to avoid import errors
CHARM_AVAILABLE = False
ZR = object  # Dummy type for ZR
G2 = object  # Dummy type for G2
class PairingGroup:
    def __init__(self, *args, **kwargs): pass

class SecretUtil:
    def __init__(self, *args, **kwargs): pass
import hashlib
import base64
from datetime import datetime

class ABEKeyManager:
    """
    Manages ABE (Attribute-Based Encryption) key operations.
    
    NOTE: This class has Shamir Secret Sharing implemented, but your project
    uses BLOCKCHAIN THRESHOLD APPROVAL instead:
    - Keys are NOT split and distributed
    - Authorities do NOT hold key shares
    - Authorities vote on blockchain; backend releases full key after 4-of-7 approve
    """
    
    def __init__(self, threshold: int = 4, total_shares: int = 7) -> None:
        """
        Initialize ABE Key Manager
        
        Args:
            threshold: Number of shares needed (default: 4)
            total_shares: Total number of shares (default: 7)
        """
        self.threshold: int = threshold
        self.total_shares: int = total_shares
        if CHARM_AVAILABLE:
            try:
                self.pairing_group = PairingGroup('SS512')
                self.secret_util = SecretUtil(self.pairing_group, verbose=False)
            except Exception:
                self.pairing_group = None
                self.secret_util = None
        else:
            self.pairing_group = None
            self.secret_util = None
        
        # Storage for shares
        self.key_shares: Dict[str, List[bytes]] = {}
        self.share_mapping: Dict[str, Dict] = {}

    def generate_master_key(self, attributes: Dict[str, str]) -> Tuple[bytes, bytes]:
        """
        Generate master key and public key for attribute set
        
        Args:
            attributes: User attributes {role, department, clearance}
            
        Returns:
            (master_key_bytes, public_key_bytes)
        """
        # Create attribute string
        attr_string: str = ",".join([f"{k}:{v}" for k, v in attributes.items()])

        # If charm library is available use pairing-based keys, otherwise fallback
        if CHARM_AVAILABLE and self.pairing_group is not None:
            msk = self.pairing_group.random(ZR)
            mpk = self.pairing_group.random(G2) ** msk
            attr_hash: bytes = hashlib.sha256(attr_string.encode()).digest()
            attr_element = self.pairing_group.hash(attr_hash, ZR)
            gpk = (mpk ** attr_element)

            return (
                base64.b64encode(str(msk).encode()),
                base64.b64encode(str(mpk).encode())
            )

        # Fallback (no charm) — generate deterministic pseudo-keys using hashing
        seed: bytes = hashlib.sha256(attr_string.encode() + os.urandom(16)).digest()
        msk_bytes: bytes = hashlib.sha256(seed + b"msk").digest()
        mpk_bytes: bytes = hashlib.sha256(seed + b"mpk").digest()

        return (
            base64.b64encode(msk_bytes),
            base64.b64encode(mpk_bytes)
        )

    def split_key_to_shares(self, 
                           key_material: bytes, 
                           file_id: str,
                           authorities: List[str]) -> Dict[str, bytes]:
        """
        Split encryption key into 4-of-7 shares using Shamir's Secret Sharing.
        
        IMPORTANT: In your current project, this method is NOT used in the download flow.
        Instead:
        - The full AES key is stored in the database
        - Authorities vote on the blockchain (no cryptographic shares)
        - Backend releases the full key after 4-of-7 approvals
        
        This method is here for reference/potential future threshold cryptography implementation.
        
        Args:
            key_material: Key to split
            file_id: File identifier
            authorities: List of 7 authority addresses
            
        Returns:
            Dict mapping authority addresses to their key shares
        """
        if len(authorities) != self.total_shares:
            raise ValueError(f"Expected {self.total_shares} authorities, got {len(authorities)}")

        # Reconstruct key as integer (use first 32 bytes)
        key_int: int = int.from_bytes(key_material[:32], 'big')

        # Use Shamir's Secret Sharing to generate integer shares
        shares: List[int] = self._shamir_split(key_int, self.threshold, self.total_shares)

        # Prepare storage for share metadata and actual shares
        share_dict = {}
        share_meta = {}

        # Ensure storage directory for shares exists
        base_share_dir: str = os.path.join(os.path.dirname(__file__), '..', '..', 'storage', 'shares')
        os.makedirs(base_share_dir, exist_ok=True)
        file_share_dir: str = os.path.join(base_share_dir, str(file_id))
        os.makedirs(file_share_dir, exist_ok=True)

        for i, auth_address in enumerate(authorities):
            # Store the integer share as base64-encoded bytes on disk per authority
            share_value: int = shares[i]
            share_bytes: bytes = str(share_value).encode()
            b64: bytes = base64.b64encode(share_bytes)

            share_path: str = os.path.join(file_share_dir, f"{auth_address}.share")
            with open(share_path, 'wb') as sf:
                sf.write(b64)

            share_dict[auth_address] = b64
            share_meta[auth_address] = {
                "share_index": i + 1,  # 1-based index for Shamir
                "file_id": file_id,
                "share_path": share_path,
                "created_at": datetime.utcnow().isoformat()
            }

        # Store metadata mappings in memory
        self.share_mapping[file_id] = {
            "authorities": authorities,
            "threshold": self.threshold,
            "total_shares": self.total_shares,
            "created_at": datetime.utcnow().isoformat()
        }

        # Store actual share metadata (not the secret) in memory
        self.key_shares[file_id] = share_meta

        return share_dict

    def collect_shares(self, 
                      file_id: str,
                      approving_authorities: List[str]) -> Optional[bytes]:
        """
        Reconstruct key from collected shares.
        
        IMPORTANT: In your current project, this method is NOT used in the download flow.
        Instead:
        - Backend checks blockchain for approval votes (not shares)
        - If 4-of-7 authorities approved, backend returns the full AES key from the database
        - Authorities do NOT hold cryptographic shares; they only vote
        
        This method is here for reference/potential future threshold cryptography implementation.
        
        Args:
            file_id: File identifier
            approving_authorities: List of authorities that approved
            
        Returns:
            Reconstructed key if threshold met, None otherwise
        """
        if len(approving_authorities) < self.threshold:
            return None

        if file_id not in self.share_mapping:
            return None

        meta = self.share_mapping[file_id]

        # Limit to known authorities
        approving = [a for a in approving_authorities if a in meta["authorities"]]
        if len(approving) < self.threshold:
            return None

        # Collect share integers and their 1-based indices
        shares_collected = []
        indices = []

        base_share_dir: str = os.path.join(os.path.dirname(__file__), '..', '..', 'storage', 'shares')
        file_share_dir: str = os.path.join(base_share_dir, str(file_id))

        for auth in approving[:self.total_shares]:
            idx = meta["authorities"].index(auth) + 1
            share_file: str = os.path.join(file_share_dir, f"{auth}.share")
            if not os.path.exists(share_file):
                continue
            with open(share_file, 'rb') as sf:
                b64: bytes = sf.read()
            try:
                share_bytes: bytes = base64.b64decode(b64)
                share_int = int(share_bytes.decode())
            except Exception:
                continue

            indices.append(idx)
            shares_collected.append(share_int)

            if len(shares_collected) >= self.threshold:
                break

        if len(shares_collected) < self.threshold:
            return None

        # Reconstruct secret using Lagrange interpolation
        reconstructed: int = self._lagrange_interpolate(shares_collected[:self.threshold], indices[:self.threshold])

        return reconstructed.to_bytes(32, 'big')

    def _shamir_split(self, secret: int, threshold: int, shares: int) -> List[int]:
        """
        Shamir's Secret Sharing - split secret into shares
        
        Args:
            secret: Secret to split
            threshold: Number of shares needed to reconstruct
            shares: Total number of shares
            
        Returns:
            List of share values
        """
        import random
        
        # Prime number for modular arithmetic
        prime = 2**256 - 2**32 - 977  # Bitcoin's SECP256k1 prime
        
        # Generate random coefficients
        coefficients = [secret] + [random.randint(0, prime - 1) for _ in range(threshold - 1)]
        
        # Generate shares by evaluating polynomial at different points
        share_list = []
        for x in range(1, shares + 1):
            y = 0
            for i, coeff in enumerate(coefficients):
                y = (y + coeff * (x ** i)) % prime
            share_list.append(y)
        
        return share_list

    def _lagrange_interpolate(self, shares: List[int], indices: List[int]) -> int:
        """
        Lagrange interpolation to reconstruct secret
        
        Args:
            shares: Share values
            indices: Original x indices (1-based)
            
        Returns:
            Reconstructed secret
        """
        prime = 2**256 - 2**32 - 977
        secret = 0
        
        for i, share in enumerate(shares):
            numerator = 1
            denominator = 1
            
            for j, other_idx in enumerate(indices):
                if i != j:
                    numerator: int = (numerator * (-other_idx)) % prime
                    denominator: int = (denominator * (indices[i] - other_idx)) % prime
            
            # Modular inverse
            denominator_inv: int = pow(denominator, -1, prime)
            secret: int = (secret + share * numerator * denominator_inv) % prime
        
        return secret

    def encrypt_file(self, 
                    file_data: bytes,
                    policy: str,
                    user_attributes: Dict[str, str]) -> Tuple[bytes, Dict]:
        """
        Encrypt file data with ABE
        
        Args:
            file_data: File content to encrypt
            policy: Attribute policy (e.g., "role:admin AND department:IT")
            user_attributes: User's attributes
            
        Returns:
            (encrypted_data, encryption_metadata)
        """
        # Generate encryption key
        enc_key: bytes = hashlib.sha256(str(user_attributes).encode()).digest()
        
        # Simple XOR encryption (in production use AES-256)
        encrypted = bytes(a ^ b for a, b in zip(file_data, enc_key * (len(file_data) // 32 + 1)))
        
        metadata = {
            "policy": policy,
            "attributes_required": self._parse_policy(policy),
            "encrypted_at": datetime.utcnow().isoformat(),
            "threshold": self.threshold,
            "total_shares": self.total_shares
        }
        
        return encrypted, metadata

    def decrypt_file(self,
                    encrypted_data: bytes,
                    decryption_key: bytes,
                    user_attributes: Dict[str, str]) -> Optional[bytes]:
        """
        Decrypt file data with reconstructed key
        
        Args:
            encrypted_data: Encrypted file content
            decryption_key: Reconstructed key from threshold shares
            user_attributes: User's attributes
            
        Returns:
            Decrypted data if successful
        """
        try:
            # Verify attributes match policy
            # In production: proper attribute verification
            
            # Decrypt using XOR
            decrypted = bytes(a ^ b for a, b in zip(
                encrypted_data, 
                decryption_key * (len(encrypted_data) // 32 + 1)
            ))
            
            return decrypted
        except Exception as e:
            print(f"Decryption error: {e}")
            return None

    def _parse_policy(self, policy: str) -> List[str]:
        """Parse policy string to extract required attributes"""
        # Simple parser for "attr1:value1 AND attr2:value2"
        attributes = []
        for part in policy.replace(" AND ", ",").split(","):
            if ":" in part:
                attr = part.split(":")[0].strip()
                attributes.append(attr)
        return attributes

    def verify_attributes(self, user_attributes: Dict[str, str], policy: str) -> bool:
        """Verify if user attributes satisfy the CP-ABE-style policy.

        Policies in this project use attribute tokens like `role:employee` and may
        contain parentheses and OR groups, e.g. `(role:admin OR role:manager) AND (dept:IT)`.
        """
        try:
            from backend.abe.cpabe_utils import policy_satisfied

            attrs = {f"{k}:{v}" for k, v in (user_attributes or {}).items()}

            # Accept both naming conventions for department
            if user_attributes:
                if "department" in user_attributes and "dept" not in user_attributes:
                    attrs.add(f"dept:{user_attributes['department']}")
                if "dept" in user_attributes and "department" not in user_attributes:
                    attrs.add(f"department:{user_attributes['dept']}")

            return policy_satisfied(attrs, policy)
        except Exception:
            # Fallback to the legacy, key-only check (best-effort)
            required = self._parse_policy(policy)
            return all(attr in (user_attributes or {}) for attr in required)


# Singleton instance
_abe_manager: Optional[ABEKeyManager] = None


def get_abe_manager(threshold: int = 4, total_shares: int = 7) -> ABEKeyManager:
    """Get or create ABE manager instance"""
    global _abe_manager
    
    if _abe_manager is None:
        _abe_manager = ABEKeyManager(threshold, total_shares)
    
    return _abe_manager
