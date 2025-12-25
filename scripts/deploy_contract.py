#!/usr/bin/env python3
"""
Deploy KeyAuthority contract to local Ganache

This script:
1. Compiles KeyAuthority.sol locally using solcx
2. Deploys to Ganache at http://127.0.0.1:7545
3. Updates DEPLOYMENT_INFO.json with contract address and ABI
"""

import json
import os
import sys
from pathlib import Path

# Add parent directories to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from web3 import Web3
from eth_account import Account

# ============ CONFIGURATION ============
GANACHE_URL = "http://127.0.0.1:7545"
PROJECT_ROOT = Path(__file__).parent.parent
CONTRACTS_DIR = PROJECT_ROOT / "contracts"
ARTIFACTS_DIR = PROJECT_ROOT / "artifacts"
ABI_PATH = CONTRACTS_DIR / "KeyAuthorityABI.json"
DEPLOYMENT_INFO_PATH = PROJECT_ROOT / "backend" / "blockchain" / "DEPLOYMENT_INFO.json"

# Authority addresses (same 7 authorities from Ganache)
AUTHORITIES = [
    "0x8d4d6c34EDEA4E1eb2fc2423D6A091cdCB34DB48",
    "0xfbe684383F81045249eB1E5974415f484E6F9f21",
    "0xd2A2E096ef8313db712DFaB39F40229F17Fd3f94",
    "0x57D14fF746d33127a90d4B888D378487e2C69f1f",
    "0x0e852C955e5DBF7187Ec6ed7A3B131165C63cf9a",
    "0x211Db7b2b475E9282B31Bd0fF39220805505Ff71",
    "0x7FAdEAa4442bc60678ee16E401Ed80342aC24d16"
]
THRESHOLD = 4

# ============ STEP 1: LOAD ABI ============
print("[1/5] Loading contract ABI...")
if not ABI_PATH.exists():
    print(f"❌ ABI not found: {ABI_PATH}")
    sys.exit(1)

with open(ABI_PATH, "r") as f:
    ABI = json.load(f)
print(f"✅ ABI loaded ({len(ABI)} functions)")

# ============ STEP 2: LOAD BYTECODE ============
print("\n[2/5] Loading contract bytecode from artifact...")
ARTIFACT_PATH = ARTIFACTS_DIR / "KeyAuthority.json"
if not ARTIFACT_PATH.exists():
    print(f"❌ Artifact not found: {ARTIFACT_PATH}")
    sys.exit(1)

with open(ARTIFACT_PATH, "r") as f:
    artifact = json.load(f)

# Extract bytecode from nested structure
bytecode_obj = artifact.get("data", {}).get("bytecode", {})
bytecode_hex = bytecode_obj.get("object", "")

if not bytecode_hex:
    print("❌ Bytecode not found in artifact")
    sys.exit(1)

print(f"✅ Bytecode loaded ({len(bytecode_hex)} chars, ~{len(bytecode_hex)//2} bytes)")

# ============ STEP 3: CONNECT TO GANACHE ============
print("\n[3/5] Connecting to Ganache at", GANACHE_URL)
w3 = Web3(Web3.HTTPProvider(GANACHE_URL))

if not w3.is_connected():
    print("❌ Cannot connect to Ganache. Is it running on 127.0.0.1:7545?")
    sys.exit(1)

print(f"✅ Connected to Ganache")
print(f"   Chain ID: {w3.eth.chain_id}")
print(f"   Gas price: {w3.eth.gas_price} wei")

# Get deployer account (first account from Ganache)
accounts = w3.eth.accounts
deployer = accounts[0]
print(f"   Deployer: {deployer}")
print(f"   Balance: {w3.eth.get_balance(deployer) / 10**18:.2f} ETH")

# ============ STEP 4: DEPLOY CONTRACT ============
print("\n[4/5] Deploying KeyAuthority contract...")

# Create contract object with constructor
KeyAuthority = w3.eth.contract(abi=ABI, bytecode="0x" + bytecode_hex)

# Build constructor arguments: [authorities, threshold]
constructor_args = [AUTHORITIES, THRESHOLD]

print(f"   Constructor args:")
print(f"     Authorities: {len(AUTHORITIES)} addresses")
print(f"     Threshold: {THRESHOLD}")

# Estimate gas
try:
    gas_estimate = KeyAuthority.constructor(*constructor_args).estimate_gas(
        {"from": deployer}
    )
    print(f"   Estimated gas: {gas_estimate}")
    gas_limit = int(gas_estimate * 1.2)  # Add 20% buffer
except Exception as e:
    print(f"⚠️  Gas estimation failed: {e}")
    gas_limit = 3_000_000
    print(f"   Using fallback gas limit: {gas_limit}")

# Deploy
try:
    tx_hash = KeyAuthority.constructor(*constructor_args).transact(
        {
            "from": deployer,
            "gas": gas_limit,
            "gasPrice": w3.eth.gas_price,
        }
    )
    print(f"   Transaction hash: {tx_hash.hex()}")
    
    # Wait for receipt
    print("   Waiting for confirmation...")
    receipt = w3.eth.wait_for_transaction_receipt(tx_hash, timeout=30)
    
    contract_address = receipt.contractAddress
    print(f"✅ Contract deployed at: {contract_address}")
    print(f"   Gas used: {receipt.gasUsed}")
    print(f"   Status: {'Success' if receipt.status == 1 else 'Failed'}")
    
except Exception as e:
    print(f"❌ Deployment failed: {e}")
    sys.exit(1)

# ============ STEP 5: SAVE DEPLOYMENT INFO ============
print("\n[5/5] Saving deployment info...")

deployment_info = {
    "contractAddress": contract_address,
    "deployedAt": str(Path.cwd()),
    "network": "Ganache (local)",
    "rpcUrl": GANACHE_URL,
    "authorities": AUTHORITIES,
    "threshold": THRESHOLD,
    "abi": ABI,
    "deployer": deployer,
    "transactionHash": tx_hash.hex()
}

# Create directory if needed
DEPLOYMENT_INFO_PATH.parent.mkdir(parents=True, exist_ok=True)

with open(DEPLOYMENT_INFO_PATH, "w") as f:
    json.dump(deployment_info, f, indent=2)

print(f"✅ Saved to {DEPLOYMENT_INFO_PATH}")

# Also save to artifacts folder
artifacts_deployment = ARTIFACTS_DIR / "KeyAuthority_deployed.json"
with open(artifacts_deployment, "w") as f:
    json.dump(deployment_info, f, indent=2)
print(f"✅ Also saved to {artifacts_deployment}")

# ============ VERIFY ============
print("\n" + "="*60)
print("DEPLOYMENT SUMMARY")
print("="*60)
print(f"Contract Address: {contract_address}")
print(f"Network: Ganache (http://127.0.0.1:7545)")
print(f"Deployer: {deployer}")
print(f"Authorities: {len(AUTHORITIES)}")
print(f"Threshold: {THRESHOLD}")
print(f"\nNext steps:")
print(f"1. Update backend config to use: {contract_address}")
print(f"2. Test approvals with: /api/access/simulate-approvals")
print("="*60)

print("\n✅ Deployment complete!")
