#!/usr/bin/env python3
"""Deploy KeyAuthority settings for local Ganache.

This script does not compile Solidity. It helps you save the deployed contract
address and related metadata to `backend/blockchain/DEPLOYMENT_INFO.json`.
"""

import json
import os
import sys
from pathlib import Path

try:
    from web3 import Web3
except ImportError:
    print("Missing dependency: web3. Install with: pip install web3")
    sys.exit(1)

# Configuration
GANACHE_RPC = "http://127.0.0.1:7545"
SOLIDITY_FILE = "contracts/KeyAuthority.sol"
DEPLOYMENT_INFO_PATH = "backend/blockchain/DEPLOYMENT_INFO.json"

# Authority addresses (7 Ganache default accounts)
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

def connect_to_ganache():
    """Connect to Ganache"""
    print(f"Connecting to Ganache at {GANACHE_RPC}...")
    w3 = Web3(Web3.HTTPProvider(GANACHE_RPC))
    
    if not w3.is_connected():
        print("Cannot connect to Ganache. Is it running?")
        print("Start Ganache with: ganache-cli --host 127.0.0.1 --port 7545")
        sys.exit(1)
    
    print("Connected")
    return w3

def deploy_with_remix_bytecode(w3):
    """
    Alternative: Use pre-compiled bytecode from Remix
    Get bytecode from Remix: Solidity Compiler → Compilation Details → Bytecode
    """
    print("\nAlternative: deploy in Remix and paste the deployed address here.")
    
    contract_addr = input("\nPaste deployed contract address (0x...): ").strip()
    
    if not contract_addr.startswith("0x") or len(contract_addr) != 42:
        print("Invalid address format")
        sys.exit(1)
    
    save_deployment_info(contract_addr, {"contractAddress": contract_addr})
    return contract_addr

def save_deployment_info(contract_address, receipt=None):
    """Save deployment info to JSON"""
    deployment_info = {
        "contractAddress": contract_address,
        "network": "Ganache",
        "rpcUrl": GANACHE_RPC,
        "chainId": 1337,
        "threshold": THRESHOLD,
        "authorities": AUTHORITIES,
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
    print("\nThis script focuses on saving the address used by the backend:")
    print("  1. Deploy via Remix GUI (you already did this)")
    print("  2. Copy the deployed contract address")
    print("  3. Paste it below to save to the backend\n")
    
    choice = input("Do you already have a deployed contract address? (y/n): ").strip().lower()
    
    if choice == 'y':
        addr = input("Paste contract address (0x...): ").strip()
        if addr.startswith("0x") and len(addr) == 42:
            deploy_with_remix_bytecode.__doc__ = None  # Hide the function
            save_deployment_info(addr)
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
        print("\n📍 MANUAL DEPLOYMENT VIA REMIX:")
        deploy_with_remix_bytecode(w3)

if __name__ == "__main__":
    main()
