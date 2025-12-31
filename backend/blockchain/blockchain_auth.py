"""
Blockchain Authentication Service
Integrates with KeyAuthority contract for decentralized key approvals

Deployment: Contract deployed via Remix IDE to local Ganache instance.
Due to local EVM compatibility issues, use Remix IDE for deployment instead of local compilation.
The architecture and logic remain blockchain-based (4-of-7 threshold approval voting).
"""
import json
import os
from typing import Any, Dict, List, Optional, Tuple
from web3 import Web3
from eth_account.messages import encode_defunct
from datetime import datetime, timedelta
import hashlib

class BlockchainAuthService:
    def __init__(
        self,
        contract_address: str,
        rpc_url: str = "http://127.0.0.1:7545",
        authorities: Optional[List[str]] = None,
        threshold: int = 4,
    ):
        """
        Initialize blockchain authentication service for threshold-based approval voting.
        
        This service uses blockchain to record approval votes from multiple authorities.
        It does NOT split keys cryptographically (no Shamir Secret Sharing).
        Instead, it implements threshold approval: the decryption key is released only
        after a minimum number of authorities vote to approve access.
        
        Args:
            contract_address: KeyAuthority contract address
            rpc_url: Ethereum RPC endpoint (default: local Ganache at 127.0.0.1:7545)
        """
        self.w3 = Web3(Web3.HTTPProvider(rpc_url))
        self.contract_address = contract_address
        self.threshold = threshold  # expected threshold from deployment info
        
        # Load contract ABI (try multiple likely locations)
        abi_candidates = [
            os.path.join(os.path.dirname(__file__), '..', 'contracts', 'KeyAuthorityABI.json'),
            os.path.join(os.path.dirname(__file__), '..', '..', 'contracts', 'KeyAuthorityABI.json'),
            os.path.join(os.getcwd(), 'contracts', 'KeyAuthorityABI.json'),
            os.path.join(os.path.dirname(__file__), 'KeyAuthorityABI.json')
        ]
        self.contract_abi = None
        for p in abi_candidates:
            try:
                if os.path.exists(p):
                    with open(p, 'r') as f:
                        self.contract_abi = json.load(f)
                        break
            except Exception:
                continue

        if self.contract_abi is None:
            raise Exception(f"Contract ABI not found. Tried: {abi_candidates}")
        
        # Initialize contract
        self.contract = self.w3.eth.contract(
            address=Web3.to_checksum_address(contract_address),
            abi=self.contract_abi
        )

        # Validate deployed contract exists at address
        code = self.w3.eth.get_code(Web3.to_checksum_address(contract_address))
        if not code or code == b"\x00" or len(code) < 4:
            raise Exception(
                f"No contract code found at {contract_address}. "
                "Update DEPLOYMENT_INFO.json with the latest deployed contract address."
            )

        # Validate on-chain threshold matches expected project threshold
        try:
            onchain_threshold = int(self.contract.functions.threshold().call())
        except Exception as e:
            raise Exception(f"Failed to read on-chain threshold(): {e}")

        if onchain_threshold != int(self.threshold):
            raise Exception(
                f"KeyAuthority contract threshold mismatch: on-chain={onchain_threshold}, expected={self.threshold}. "
                "Redeploy KeyAuthority with threshold=4 and update backend/blockchain/DEPLOYMENT_INFO.json."
            )

        # Lock to the on-chain threshold after validation
        self.threshold = onchain_threshold

        # Authority addresses: resolve from contract + Ganache accounts
        self.authorities = self._resolve_authorities(authorities)

        # Enforce 7-authority design for this project
        if len(self.authorities) < 7:
            raise Exception(
                f"KeyAuthority contract has only {len(self.authorities)} authority account(s) available from Ganache, expected 7. "
                "This usually means the contract was deployed with the wrong constructor authorities array or Ganache was restarted. "
                "Redeploy with the first 7 Ganache accounts as authorities and update DEPLOYMENT_INFO.json."
            )

    def _resolve_authorities(self, preferred: Optional[List[str]]) -> List[str]:
        """Pick authority addresses that are actually recognized by the contract.

        This fixes the common case where Ganache is restarted (accounts change) or
        DEPLOYMENT_INFO contains stale addresses.
        """
        preferred = preferred or []
        preferred = [Web3.to_checksum_address(a) for a in preferred if isinstance(a, str) and a.startswith("0x")]

        chain_accounts = []
        try:
            chain_accounts = [Web3.to_checksum_address(a) for a in (self.w3.eth.accounts or [])]
        except Exception:
            chain_accounts = []

        # Prefer Ganache unlocked accounts that are authorities (these are transactable).
        onchain_authority_accounts: List[str] = []
        for addr in chain_accounts:
            try:
                if self.contract.functions.authorities(addr).call():
                    onchain_authority_accounts.append(addr)
            except Exception:
                continue

        # If deployment listed preferred authorities, keep those that are authorities too.
        preferred_authorities: List[str] = []
        for addr in preferred:
            if addr in preferred_authorities:
                continue
            try:
                if self.contract.functions.authorities(addr).call():
                    preferred_authorities.append(addr)
            except Exception:
                continue

        # Merge, favoring transactable Ganache accounts first.
        merged: List[str] = []
        for addr in onchain_authority_accounts + preferred_authorities:
            if addr not in merged:
                merged.append(addr)

        return merged

    def is_authority(self, address: str) -> bool:
        try:
            return self.contract.functions.authorities(Web3.to_checksum_address(address)).call()
        except Exception:
            return False

    def check_connection(self) -> bool:
        """Check if connected to blockchain"""
        try:
            return self.w3.is_connected()
        except Exception as e:
            print(f"Connection error: {e}")
            return False

    def generate_key_id(self, file_id: str, user_id: str) -> bytes:
        """
        Generate unique key ID for file+user combination.
        
        This key ID is used to track approval votes on the blockchain.
        It does NOT represent a cryptographic key share.
        
        Args:
            file_id: File identifier
            user_id: User identifier
            
        Returns:
            bytes32 key ID (used for blockchain approval tracking)
        """
        combined = f"{file_id}:{user_id}:{datetime.utcnow().isoformat()}"
        return hashlib.sha256(combined.encode()).digest()

    def initiate_key_approval(self, file_id: str, user_id: str, user_attributes: dict) -> dict:
        """
        Initiate approval voting process on blockchain.
        
        Creates an approval request record. Authorities will independently vote
        by calling the smart contract (simulated via /api/access/simulate-approvals
        in this project). Backend does NOT push requests to authorities.
        
        Args:
            file_id: File to decrypt
            user_id: User requesting decryption
            user_attributes: User's attributes {role, department, clearance}
            
        Returns:
            Approval request data with authorities list and required threshold
        """
        key_id = self.generate_key_id(file_id, user_id)
        key_id_hex = "0x" + key_id.hex()
        
        return {
            "key_id": key_id_hex,
            "file_id": file_id,
            "user_id": user_id,
            "user_attributes": user_attributes,
            "authorities": self.authorities,
            "threshold": self.threshold,
            "required_approvals": self.threshold,
            "timestamp": datetime.utcnow().isoformat(),
            "expiration": (datetime.utcnow() + timedelta(hours=1)).isoformat()
        }

    def get_approval_status(self, key_id: str) -> dict:
        """
        Get current approval vote count from blockchain.
        
        Queries the smart contract to check how many authorities have voted to approve.
        Returns True only if >= 4 (threshold) authorities have approved.
        
        Args:
            key_id: The key ID (hex format)
            
        Returns:
            Approval status with current count and threshold info
        """
        try:
            # Convert hex to bytes32
            key_bytes = bytes.fromhex(key_id.replace("0x", ""))
            
            # Get approval count from contract
            approval_count = self.contract.functions.approvals(key_bytes).call()
            is_approved = self.contract.functions.isApproved(key_bytes).call()
            
            return {
                "key_id": key_id,
                "current_approvals": approval_count,
                "required_approvals": self.threshold,
                "is_approved": is_approved,
                "approval_percentage": int((approval_count / self.threshold) * 100) if self.threshold else 0
            }
        except Exception as e:
            return {
                "error": str(e),
                "key_id": key_id
            }

    def verify_approval(self, key_id: str) -> bool:
        """
        Verify if a key has reached the approval threshold (4 out of 7).
        
        Queries the smart contract to check the vote count.
        Returns True only if >= 4 authorities have approved.
        
        Args:
            key_id: The key ID (hex format)
            
        Returns:
            True if threshold met, False otherwise
        """
        try:
            key_bytes = bytes.fromhex(key_id.replace("0x", ""))
            return self.contract.functions.isApproved(key_bytes).call()
        except Exception as e:
            print(f"Verification error: {e}")
            return False

    def create_signature_request(self, message: str, account_address: str) -> dict:
        """
        Create a signature request for user to approve in MetaMask
        
        Args:
            message: Message to sign
            account_address: User's wallet address
            
        Returns:
            Signature request
        """
        return {
            "message": message,
            "account": account_address,
            "timestamp": datetime.utcnow().isoformat(),
            "request_type": "key_approval"
        }

    def validate_signature(self, message: str, signature: str, account_address: str) -> bool:
        """
        Validate a signed message
        
        Args:
            message: Original message
            signature: Signature from MetaMask
            account_address: Account that signed
            
        Returns:
            True if signature is valid
        """
        try:
            message_hash = encode_defunct(text=message)
            recovered_address = self.w3.eth.account.recover_message(message_hash, signature=signature)
            return recovered_address.lower() == account_address.lower()
        except Exception as e:
            print(f"Signature validation error: {e}")
            return False

    def approve_key(self, key_id: str, authority_address: str) -> Tuple[Optional[str], Optional[str]]:
        """
        Authority approves a key by calling the smart contract.
        
        In a real system, an authority would sign and submit this transaction from their wallet.
        In this project, use /api/access/simulate-approvals to send approvals from authority addresses.
        The approval vote is recorded on the blockchain (Ganache).

        Args:
            key_id: hex string key id (0x...)
            authority_address: authority account address to send approval from

        Returns:
            (tx_hash_hex, error_message). On success: ("0x...", None). On failure: (None, "...").
        """
        try:
            key_bytes = bytes.fromhex(key_id.replace("0x", ""))
            tx = self.contract.functions.approveKey(key_bytes).transact({
                'from': Web3.to_checksum_address(authority_address),
                'gas': 200000
            })
            # Wait for receipt (Ganache mines instantly)
            receipt = self.w3.eth.wait_for_transaction_receipt(tx)
            return receipt.transactionHash.hex(), None
        except Exception as e:
            msg = str(e)
            print(f"approve_key error: {msg}")
            return None, msg

    def get_authorities_info(self) -> List[dict]:
        """
        Get information about all authorities
        
        Returns:
            List of authority information
        """
        authorities_info = []
        for i, auth_addr in enumerate(self.authorities, 1):
            authorities_info.append({
                "index": i,
                "address": auth_addr,
                "is_authority": self._check_is_authority(auth_addr)
            })
        return authorities_info

    def _check_is_authority(self, address: str) -> bool:
        """Check if address is registered authority"""
        try:
            return self.contract.functions.authorities(Web3.to_checksum_address(address)).call()
        except:
            return False


# Singleton instance
_blockchain_service: Optional[BlockchainAuthService] = None


def get_blockchain_service(contract_address: str = None) -> BlockchainAuthService:
    """Get or create blockchain service instance"""
    global _blockchain_service
    
    if _blockchain_service is None:
        # Try to load from deployment info in multiple locations
        if contract_address is None:
            deploy_authorities: Optional[List[str]] = None
            deploy_threshold: int = 4
            possible = [
                os.path.join(os.path.dirname(__file__), 'DEPLOYMENT_INFO.json'),
                os.path.join(os.path.dirname(__file__), 'DEPLOYMENT_INFO.TXT'),
                os.path.join(os.getcwd(), 'backend', 'blockchain', 'DEPLOYMENT_INFO.json'),
                os.path.join(os.getcwd(), 'backend', 'blockchain', 'DEPLOYMENT_INFO.TXT'),
                os.path.join(os.getcwd(), 'contracts', 'DEPLOYMENT_INFO.json')
            ]
            for p in possible:
                try:
                    if os.path.exists(p):
                        with open(p, 'r') as f:
                            try:
                                deploy_info = json.load(f)
                                contract_address = deploy_info.get('contractAddress')
                                deploy_authorities = deploy_info.get('authorities')
                                if isinstance(deploy_info.get('threshold'), int):
                                    deploy_threshold = deploy_info['threshold']
                            except Exception:
                                content = f.read()
                                for line in content.splitlines():
                                    if '0x' in line:
                                        # first hex-like token
                                        for tok in line.split():
                                            if tok.startswith('0x'):
                                                contract_address = tok.strip()
                                                break
                                
                        if contract_address:
                            break
                except Exception:
                    continue

        if contract_address is None:
            raise Exception('Contract address not found. Deploy contract first and ensure DEPLOYMENT_INFO exists.')

        # If deployment file included authorities/threshold, pass them through.
        try:
            deploy_authorities  # type: ignore[name-defined]
        except Exception:
            deploy_authorities = None
        try:
            deploy_threshold  # type: ignore[name-defined]
        except Exception:
            deploy_threshold = 4

        _blockchain_service = BlockchainAuthService(
            contract_address,
            authorities=deploy_authorities,
            threshold=deploy_threshold,
        )
    
    return _blockchain_service
