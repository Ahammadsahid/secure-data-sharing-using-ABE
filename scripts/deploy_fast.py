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

DEFAULT_AUTHORITIES = [
    "0x266E6E85ae9D38F8888925c724Ab1B739E4794f3",
    "0x8F29929fC7094318BF562f981b04ecfA177Ecc54",
    "0x6518Bcb59B8E40A5a24189217912C511b783590f",
    "0x380cb6B16Ee5AbbB8A635e55e91c6F0eb982D7b6",
    "0x463433BC694b26751130e6382081818B4D205a0C",
    "0xF811e1e3eFFf3f857431f4CEea4D67c0a0c0e4C9",
    "0x6c60d1EEc446c567eF756bf9d07CE0056DAEC777",
]

AUTHORITIES = DEFAULT_AUTHORITIES  # Can be overridden via GANACHE_AUTHORITIES/AUTHORITIES
THRESHOLD = 4


def _parse_authorities_env():
    raw = os.getenv("GANACHE_AUTHORITIES") or os.getenv("AUTHORITIES")
    if not raw:
        return None
    raw = raw.strip()
    try:
        if raw.startswith("["):
            authorities = json.loads(raw)
        else:
            authorities = [a.strip() for a in raw.split(",") if a.strip()]
    except Exception as e:
        raise SystemExit(f"Invalid GANACHE_AUTHORITIES/AUTHORITIES format: {e}")
    if not isinstance(authorities, list) or not all(isinstance(a, str) for a in authorities):
        raise SystemExit("GANACHE_AUTHORITIES/AUTHORITIES must be a list of hex addresses")
    return authorities


def resolve_authorities(w3: Web3, expected: int = 7):
    env_list = _parse_authorities_env()
    if env_list is not None:
        authorities = env_list
    elif AUTHORITIES:
        authorities = AUTHORITIES
    else:
        authorities = list((w3.eth.accounts or [])[:expected])
    if len(authorities) < expected:
        raise SystemExit(f"Need {expected} authorities, got {len(authorities)}")
    return [Web3.to_checksum_address(a) for a in authorities[:expected]]

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

# Use first 7 unlocked Ganache accounts as authorities (or env override)
AUTHORITIES = resolve_authorities(w3)

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
