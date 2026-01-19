#!/usr/bin/env python3
"""KeyAuthority simulator using local JSON storage."""

import json
from pathlib import Path
from datetime import datetime

PROJECT_ROOT = Path(__file__).parent.parent
STORAGE_FILE = PROJECT_ROOT / "backend" / "blockchain" / "approvals_storage.json"

class KeyAuthoritySimulator:
    """Simulate KeyAuthority approvals using local JSON storage."""
    
    def __init__(self, storage_file=None):
        self.storage_file = storage_file or STORAGE_FILE
        self.storage_file.parent.mkdir(parents=True, exist_ok=True)
        self.load_state()
    
    def load_state(self):
        """Load approvals from disk"""
        if self.storage_file.exists():
            with open(self.storage_file, 'r') as f:
                data = json.load(f)
                self.approvals = data.get('approvals', {})
                self.approved_by = data.get('approved_by', {})
        else:
            self.approvals = {}
            self.approved_by = {}
    
    def save_state(self):
        """Save approvals to disk"""
        with open(self.storage_file, 'w') as f:
            json.dump({
                'approvals': self.approvals,
                'approved_by': self.approved_by,
                'last_updated': datetime.utcnow().isoformat()
            }, f, indent=2)
    
    def approve_key(self, key_id: str, authority: str) -> bool:
        """
        Record an authority approval for a key.
        
        Args:
            key_id: The key ID (hex string)
            authority: Authority address
            
        Returns:
            True if approval was recorded, False if already approved
        """
        if key_id not in self.approvals:
            self.approvals[key_id] = 0
            self.approved_by[key_id] = []
        
        # Check if already approved
        if key_id in self.approved_by and authority in self.approved_by[key_id]:
            return False
        
        # Record approval
        self.approvals[key_id] += 1
        if key_id not in self.approved_by:
            self.approved_by[key_id] = []
        self.approved_by[key_id].append(authority)
        
        self.save_state()
        return True
    
    def get_approval_count(self, key_id: str) -> int:
        """Get number of approvals for a key"""
        return self.approvals.get(key_id, 0)
    
    def is_approved(self, key_id: str, threshold: int = 4) -> bool:
        """Check if key reached threshold"""
        return self.get_approval_count(key_id) >= threshold
    
    def get_approvers(self, key_id: str):
        """Get list of approving authorities"""
        return self.approved_by.get(key_id, [])
    
    def reset_approvals(self, key_id: str):
        """Reset approvals for a key (for testing)"""
        if key_id in self.approvals:
            del self.approvals[key_id]
        if key_id in self.approved_by:
            del self.approved_by[key_id]
        self.save_state()


# Test deployment
if __name__ == "__main__":
    print("[Deployment] Creating Python-based KeyAuthority simulator...")
    
    simulator = KeyAuthoritySimulator()
    
    # Create deployment info
    deployment_info = {
        "contractAddress": "Python-Simulator",
        "deploymentType": "Python-based (avoids Ganache/Solc issues)",
        "network": "local",
        "rpcUrl": "http://127.0.0.1:7545",
        "threshold": 4,
        "authorities": [
            "0x266E6E85ae9D38F8888925c724Ab1B739E4794f3",
            "0x8F29929fC7094318BF562f981b04ecfA177Ecc54",
            "0x6518Bcb59B8E40A5a24189217912C511b783590f",
            "0x380cb6B16Ee5AbbB8A635e55e91c6F0eb982D7b6",
            "0x463433BC694b26751130e6382081818B4D205a0C",
            "0xF811e1e3eFFf3f857431f4CEea4D67c0a0c0e4C9",
            "0x6c60d1EEc446c567eF756bf9d07CE0056DAEC777"
        ],
        "message": "This simulates blockchain approval voting using JSON storage. Suitable for local development and testing.",
        "timestamp": datetime.utcnow().isoformat()
    }
    
    # Save to DEPLOYMENT_INFO.json
    deployment_file = PROJECT_ROOT / "backend" / "blockchain" / "DEPLOYMENT_INFO.json"
    deployment_file.parent.mkdir(parents=True, exist_ok=True)
    with open(deployment_file, 'w') as f:
        json.dump(deployment_info, f, indent=2)
    
    print("KeyAuthority simulator created")
    print(f"   Storage: {STORAGE_FILE}")
    print(f"   Config: {deployment_file}")
    print(f"\nApproval voting will be stored in: {STORAGE_FILE}")
    print(f"\nYou can now:")
    print(f"  1. Start the backend: uvicorn backend.main:app --reload")
    print(f"  2. Use /api/access/simulate-approvals to record votes")
    print(f"  3. Check approval status with /api/access/approval-status/{{key_id}}")
