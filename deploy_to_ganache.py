#!/usr/bin/env python3
"""Save the deployed KeyAuthority address/config for Ganache."""

import json
import os
import sys
from pathlib import Path

try:
    from web3 import Web3
except ImportError:
    print("Missing dependency: web3. Install with: pip install web3")
    sys.exit(1)

GANACHE_RPC = "http://127.0.0.1:7545"
SOLIDITY_FILE = "contracts/KeyAuthority.sol"
DEPLOYMENT_INFO_PATH = "backend/blockchain/DEPLOYMENT_INFO.json"

DEFAULT_AUTHORITIES = [
    "0x266E6E85ae9D38F8888925c724Ab1B739E4794f3",
    "0x8F29929fC7094318BF562f981b04ecfA177Ecc54",
    "0x6518Bcb59B8E40A5a24189217912C511b783590f",
    "0x380cb6B16Ee5AbbB8A635e55e91c6F0eb982D7b6",
    "0x463433BC694b26751130e6382081818B4D205a0C",
    "0xF811e1e3eFFf3f857431f4CEea4D67c0a0c0e4C9",
    "0x6c60d1EEc446c567eF756bf9d07CE0056DAEC777",
]
AUTHORITIES = DEFAULT_AUTHORITIES

THRESHOLD = 4


def _parse_authorities_env():
    """Optional override: JSON array or comma-separated list."""
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


def _resolve_authorities(w3: Web3, expected: int = 7):
    env_list = _parse_authorities_env()
    if env_list is not None:
        authorities = env_list
    elif DEFAULT_AUTHORITIES:
        authorities = DEFAULT_AUTHORITIES
    else:
        authorities = list((w3.eth.accounts or [])[:expected])

    if len(authorities) < expected:
        raise SystemExit(f"Need {expected} authority addresses, got {len(authorities)}")
    return [Web3.to_checksum_address(a) for a in authorities[:expected]]

def connect_to_ganache():
    """Connect to Ganache."""
    print(f"Connecting to Ganache at {GANACHE_RPC}...")
    w3 = Web3(Web3.HTTPProvider(GANACHE_RPC))
    
    if not w3.is_connected():
        print("Cannot connect to Ganache. Is it running?")
        print("Start Ganache with: ganache-cli --host 127.0.0.1 --port 7545")
        sys.exit(1)
    
    print("Connected")
    return w3

def deploy_with_remix_bytecode(w3):
    """Prompt for an address (when deployed via Remix) and save it."""
    print("\nDeploy in Remix, then paste the contract address here.")
    
    contract_addr = input("\nPaste deployed contract address (0x...): ").strip()
    
    if not contract_addr.startswith("0x") or len(contract_addr) != 42:
        print("Invalid address format")
        sys.exit(1)
    
    save_deployment_info(contract_addr, w3, {"contractAddress": contract_addr})
    return contract_addr

def save_deployment_info(contract_address, w3: Web3, receipt=None):
    """Write backend/blockchain/DEPLOYMENT_INFO.json."""
    authorities = _resolve_authorities(w3)
    deployment_info = {
        "contractAddress": contract_address,
        "network": "Ganache",
        "rpcUrl": GANACHE_RPC,
        "chainId": int(w3.eth.chain_id),
        "threshold": THRESHOLD,
        "authorities": authorities,
    }
    
    if receipt and isinstance(receipt, dict):
        if 'transactionHash' in receipt:
            deployment_info["transactionHash"] = receipt['transactionHash'].hex() if hasattr(receipt['transactionHash'], 'hex') else receipt['transactionHash']
        if 'blockNumber' in receipt:
            deployment_info["blockNumber"] = receipt['blockNumber']
        if 'gasUsed' in receipt:
            deployment_info["gasUsed"] = receipt['gasUsed']
    
    os.makedirs(os.path.dirname(DEPLOYMENT_INFO_PATH), exist_ok=True)
    
    with open(DEPLOYMENT_INFO_PATH, 'w') as f:
        json.dump(deployment_info, f, indent=2)
    
    print(f"\nDeployment info saved to {DEPLOYMENT_INFO_PATH}")
    print(json.dumps(deployment_info, indent=2))

def main():
    print("=" * 70)
    print("KeyAuthority contract settings (Ganache)")
    print("=" * 70)
    
    w3 = connect_to_ganache()
    
    print("\n" + "=" * 70)
    print("Recommended: deploy via Remix and save the contract address")
    print("=" * 70)
    print("\nThis saves the contract address used by the backend.")
    
    choice = input("Do you already have a deployed contract address? (y/n): ").strip().lower()
    
    if choice == 'y':
        addr = input("Paste contract address (0x...): ").strip()
        if addr.startswith("0x") and len(addr) == 42:
            save_deployment_info(addr, w3)
            print("\n" + "=" * 70)
            print("Contract address saved")
            print("=" * 70)
            print("\nNow you can:")
            print("1. Start backend: python -m uvicorn backend.main:app --reload")
            print("2. Start frontend: cd frontend && npm start")
            print("3. Test the download flow")
            print("\n" + "=" * 70)
            return
        else:
            print("Invalid address")
            sys.exit(1)
    else:
        print("\nManual deployment via Remix:")
        deploy_with_remix_bytecode(w3)

if __name__ == "__main__":
    main()
