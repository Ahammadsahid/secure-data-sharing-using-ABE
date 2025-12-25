#!/usr/bin/env python3
"""
Deploy a minimal working KeyAuthority contract using web3.py
Hardcodes the bytecode to a known working version for Solidity 0.8.20
"""

import json
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from web3 import Web3

# ============ CONFIGURATION ============
GANACHE_URL = "http://127.0.0.1:7545"
PROJECT_ROOT = Path(__file__).parent.parent
ARTIFACTS_DIR = PROJECT_ROOT / "artifacts"
ABI_PATH = PROJECT_ROOT / "contracts" / "KeyAuthorityABI.json"
DEPLOYMENT_INFO_PATH = PROJECT_ROOT / "backend" / "blockchain" / "DEPLOYMENT_INFO.json"

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

print("[1/5] Loading ABI...")
with open(ABI_PATH, "r") as f:
    abi = json.load(f)
print(f"✅ ABI loaded ({len(abi)} functions)")

print("\n[2/5] Connecting to Ganache...")
w3 = Web3(Web3.HTTPProvider(GANACHE_URL))
if not w3.is_connected():
    print("❌ Cannot connect to Ganache")
    sys.exit(1)

deployer = w3.eth.accounts[0]
print(f"✅ Connected")
print(f"   Deployer: {deployer}")
print(f"   Balance: {w3.eth.get_balance(deployer) / 10**18:.2f} ETH")

# ============ STEP 3: USE EXISTING ARTIFACT BYTECODE ============
print("\n[3/5] Loading bytecode from artifact...")
artifact_path = ARTIFACTS_DIR / "KeyAuthority.json"
with open(artifact_path, "r") as f:
    artifact = json.load(f)

bytecode_hex = artifact.get("data", {}).get("bytecode", {}).get("object", "")
if not bytecode_hex:
    print("❌ Bytecode not found in artifact")
    sys.exit(1)

print(f"✅ Bytecode loaded ({len(bytecode_hex)} chars)")

# ============ STEP 4: DEPLOY ============
print("\n[4/5] Deploying contract...")

# Create contract interface
contract = w3.eth.contract(abi=abi, bytecode="0x" + bytecode_hex)

# Prepare constructor args
# The contract expects: address[] _authorities, uint _threshold
constructor_args = [AUTHORITIES, THRESHOLD]

# Build transaction
tx_dict = {
    "from": deployer,
    "gas": 3000000,
    "gasPrice": w3.eth.gas_price,
}

try:
    # Send transaction directly (Ganache allows unsigned tx from account)
    tx_hash = contract.constructor(*constructor_args).transact(tx_dict)
    print(f"   TX hash: {tx_hash.hex()}")
    
    # Wait for receipt
    print("   Waiting for confirmation...")
    receipt = w3.eth.wait_for_transaction_receipt(tx_hash, timeout=30)
    
    contract_address = receipt.contractAddress
    print(f"✅ Deployed at: {contract_address}")
    print(f"   Gas used: {receipt.gasUsed}")
    
except Exception as e:
    print(f"❌ Deployment error: {type(e).__name__}: {e}")
    sys.exit(1)

# ============ STEP 5: SAVE INFO ============
print("\n[5/5] Saving deployment info...")

deployment_info = {
    "contractAddress": contract_address,
    "network": "Ganache",
    "rpcUrl": GANACHE_URL,
    "authorities": AUTHORITIES,
    "threshold": THRESHOLD,
    "deployer": deployer,
    "transactionHash": tx_hash.hex(),
    "abi": abi
}

DEPLOYMENT_INFO_PATH.parent.mkdir(parents=True, exist_ok=True)
with open(DEPLOYMENT_INFO_PATH, "w") as f:
    json.dump(deployment_info, f, indent=2)

print(f"✅ Saved to {DEPLOYMENT_INFO_PATH}")

print("\n" + "="*60)
print(f"Contract: {contract_address}")
print(f"Authorities: {len(AUTHORITIES)}")
print(f"Threshold: {THRESHOLD}")
print("="*60)
