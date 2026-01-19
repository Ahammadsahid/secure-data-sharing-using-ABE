#!/usr/bin/env python3
"""Update DEPLOYMENT_INFO.json with a contract address from Remix."""

import json
import sys
from pathlib import Path

if len(sys.argv) < 2:
    print("Usage: python update_deployment_address.py 0xContractAddress")
    print("\nExample:")
    print("  python update_deployment_address.py 0x85F05208B6C3613f42366dE27BAFBd4df40a8ceb")
    sys.exit(1)

contract_address = sys.argv[1]

# Validate format
if not contract_address.startswith("0x") or len(contract_address) != 42:
    print(f"Invalid address format: {contract_address}")
    print("   Address must be 0x followed by 40 hex characters")
    sys.exit(1)

# Load current DEPLOYMENT_INFO
deployment_file = Path(__file__).parent.parent / "backend" / "blockchain" / "DEPLOYMENT_INFO.json"

with open(deployment_file, "r") as f:
    deployment_info = json.load(f)

# Update contract address
deployment_info["contractAddress"] = contract_address
deployment_info["deploymentMethod"] = "Remix IDE + MetaMask"
deployment_info["status"] = "Deployed"

# Save
with open(deployment_file, "w") as f:
    json.dump(deployment_info, f, indent=2)

print("Contract address updated")
print(f"   Address: {contract_address}")
print(f"   File: {deployment_file}")
print("\nNext steps:")
print("   1. Restart backend: uvicorn backend.main:app --reload")
print("   2. Test approval endpoint: /api/access/simulate-approvals")
