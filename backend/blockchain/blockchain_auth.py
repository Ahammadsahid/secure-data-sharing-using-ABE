"""
Blockchain Authentication Service
Integrates with KeyAuthority contract for decentralized key approvals

Deployment: Contract deployed via Remix IDE to local Ganache instance.
Due to local EVM compatibility issues, use Remix IDE for deployment instead of local compilation.
The architecture and logic remain blockchain-based (4-of-7 threshold approval voting).
"""
import json
import os
from typing import List, Optional
from web3 import Web3
from eth_account.messages import encode_defunct
from datetime import datetime, timedelta
import hashlib

class BlockchainAuthService:
    def __init__(self, contract_address: str, rpc_url: str = "http://127.0.0.1:7545"):
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
        self.threshold = 4  # 4 out of 7 required
        
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
        
        # Authority addresses (same as deployed)
        self.authorities = [
            "0x8d4d6c34EDEA4E1eb2fc2423D6A091cdCB34DB48",
            "0xfbe684383F81045249eB1E5974415f484E6F9f21",
            "0xd2A2E096ef8313db712DFaB39F40229F17Fd3f94",
            "0x57D14fF746d33127a90d4B888D378487e2C69f1f",
            "0x0e852C955e5DBF7187Ec6ed7A3B131165C63cf9a",
            "0x211Db7b2b475E9282B31Bd0fF39220805505Ff71",
            "0x7FAdEAa4442bc60678ee16E401Ed80342aC24d16"
        ]

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
                "approval_percentage": int((approval_count / self.threshold) * 100)
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

    def approve_key(self, key_id: str, authority_address: str) -> Optional[str]:
        """
        Authority approves a key by calling the smart contract.
        
        In a real system, an authority would sign and submit this transaction from their wallet.
        In this project, use /api/access/simulate-approvals to send approvals from authority addresses.
        The approval vote is recorded on the blockchain (Ganache).

        Args:
            key_id: hex string key id (0x...)
            authority_address: authority account address to send approval from

        Returns:
            Transaction hash hex string on success, None on failure
        """
        try:
            key_bytes = bytes.fromhex(key_id.replace("0x", ""))
            tx = self.contract.functions.approveKey(key_bytes).transact({
                'from': Web3.to_checksum_address(authority_address),
                'gas': 200000
            })
            # Wait for receipt (Ganache mines instantly)
            receipt = self.w3.eth.wait_for_transaction_receipt(tx)
            return receipt.transactionHash.hex()
        except Exception as e:
            print(f"approve_key error: {e}")
            return None

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

        _blockchain_service = BlockchainAuthService(contract_address)
    
    return _blockchain_service
