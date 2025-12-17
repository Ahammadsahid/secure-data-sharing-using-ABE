from web3 import Web3
import json
import os

# -------------------------------
# Ganache Configuration
# -------------------------------
GANACHE_URL = "http://127.0.0.1:7545"
CONTRACT_ADDRESS = "0xa82ed7bd78CdeEec4685b2b09e62afc6baf786E2"

# -------------------------------
# Load ABI
# -------------------------------
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
ABI_PATH = os.path.join(BASE_DIR, "contracts", "KeyAuthorityABI.json")

with open(ABI_PATH, "r") as f:
    ABI = json.load(f)

# -------------------------------
# Web3 Setup
# -------------------------------
web3 = Web3(Web3.HTTPProvider(GANACHE_URL))

contract = web3.eth.contract(
    address=Web3.to_checksum_address(CONTRACT_ADDRESS),
    abi=ABI
)

# Use first Ganache account as backend authority
ACCOUNT = web3.eth.accounts[0]


# -------------------------------
# Blockchain Helper Functions
# -------------------------------
def request_approval(key_id: str):
    """
    Authority approves a key request
    """
    tx_hash = contract.functions.approveKey(
        web3.keccak(text=key_id)
    ).transact({"from": ACCOUNT})

    web3.eth.wait_for_transaction_receipt(tx_hash)


def check_threshold(key_id: str) -> bool:
    """
    Check if approval threshold is reached
    """
    return contract.functions.isApproved(
        web3.keccak(text=key_id)
    ).call()
