from web3 import Web3
import json
import os

GANACHE_URL = "http://127.0.0.1:7545"
CONTRACT_ADDRESS = "0x85F05208B6C3613f42366dE27BAFBd4df40a8ceb"  # ✅ SAME AS REMIX

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
ABI_PATH = os.path.join(BASE_DIR, "contracts", "KeyAuthorityABI.json")

with open(ABI_PATH, "r") as f:
    ABI = json.load(f)

web3 = Web3(Web3.HTTPProvider(GANACHE_URL))

contract = web3.eth.contract(
    address=Web3.to_checksum_address(CONTRACT_ADDRESS),
    abi=ABI
)

def is_key_approved(key_id_hex: str) -> bool:
    """
    key_id_hex example:
    0x6b65793100000000000000000000000000000000000000000000000000000000
    """
    
    
    
    return contract.functions.isApproved(
        bytes.fromhex(key_id_hex[2:])
    ).call()
