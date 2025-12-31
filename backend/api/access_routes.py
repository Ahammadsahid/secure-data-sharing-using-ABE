"""backend.api.access_routes

Decentralized access-control routes.
Integrates blockchain authentication with ABE key management.
"""

import mimetypes
import os
from typing import Dict, List

from eth_account.messages import encode_defunct
from fastapi import APIRouter, Body, Depends, HTTPException
from fastapi.responses import FileResponse
from pydantic import BaseModel
from web3 import Web3

from backend.blockchain.blockchain_auth import get_blockchain_service
from backend.database import SessionLocal
from backend.models import SecureFile

router = APIRouter(prefix="/api/access", tags=["Decentralized Access"])


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.post("/blockchain/status")
async def blockchain_status():
    """Return Ganache + contract connectivity info for the UI."""
    try:
        blockchain = get_blockchain_service()

        connected = blockchain.check_connection()
        chain_id = None
        if connected:
            try:
                chain_id = blockchain.w3.eth.chain_id
            except Exception:
                chain_id = None

        return {
            "connected": connected,
            "network": "Ganache" if connected else "disconnected",
            "rpc_url": getattr(getattr(blockchain.w3, "provider", None), "endpoint_uri", None),
            "chain_id": chain_id,
            "contract_address": blockchain.contract_address,
            "threshold": blockchain.threshold,
            "total_authorities": len(blockchain.authorities),
        }
    except Exception as e:
        raise HTTPException(
            status_code=503,
            detail={
                "reason": "contract_misconfigured",
                "message": "Blockchain is reachable but the KeyAuthority contract is misconfigured.",
                "error": str(e),
            },
        )


@router.post("/verify-signature")
async def verify_signature(body: dict = Body(...), db=Depends(get_db)):
    """Verify MetaMask signature; optionally check ABE policy for a file."""
    try:
        message = body.get("message")
        signature = body.get("signature")
        address = body.get("address")
        file_id = body.get("file_id")
        user_attributes = body.get("user_attributes")

        if isinstance(user_attributes, dict):
            # Accept both naming conventions from frontend / stored policies
            if "department" in user_attributes and "dept" not in user_attributes:
                user_attributes["dept"] = user_attributes["department"]
            if "dept" in user_attributes and "department" not in user_attributes:
                user_attributes["department"] = user_attributes["dept"]

        if not message or not signature or not address:
            return {"verified": False, "reason": "missing_fields"}

        msg = encode_defunct(text=message)
        recovered = Web3().eth.account.recover_message(msg, signature=signature)

        if recovered.lower() != address.lower():
            return {
                "verified": False,
                "reason": "signature_mismatch",
                "recovered": recovered,
                "address": address,
            }

        if file_id and user_attributes:
            file_record = db.query(SecureFile).filter(SecureFile.id == file_id).first()
            if not file_record:
                return {"verified": False, "reason": "file_not_found"}

            from backend.abe.abe_key_manager import get_abe_manager

            abe = get_abe_manager()
            if not abe.verify_attributes(user_attributes, file_record.policy):
                return {"verified": False, "reason": "policy_not_satisfied"}

        return {"verified": True, "address": address, "recovered": recovered}
    except Exception as e:
        return {"verified": False, "reason": str(e)}


class KeyApprovalRequest(BaseModel):
    file_id: str
    user_id: str
    user_attributes: Dict[str, str]


class KeyApprovalResponse(BaseModel):
    key_id: str
    file_id: str
    authorities: List[str]
    threshold: int
    required_approvals: int
    status: str
    expiration: str


@router.post("/request-key-approval", response_model=KeyApprovalResponse)
async def request_key_approval(req: KeyApprovalRequest):
    try:
        blockchain = get_blockchain_service()
    except Exception as e:
        raise HTTPException(status_code=503, detail={"reason": "contract_misconfigured", "error": str(e)})

    attrs = dict(req.user_attributes or {})
    if "department" in attrs and "dept" not in attrs:
        attrs["dept"] = attrs["department"]
    if "dept" in attrs and "department" not in attrs:
        attrs["department"] = attrs["dept"]

    approval_data = blockchain.initiate_key_approval(
        file_id=req.file_id,
        user_id=req.user_id,
        user_attributes=attrs,
    )

    return KeyApprovalResponse(
        key_id=approval_data["key_id"],
        file_id=req.file_id,
        authorities=approval_data["authorities"],
        threshold=approval_data["threshold"],
        required_approvals=approval_data["threshold"],
        status="pending",
        expiration=approval_data["expiration"],
    )


class ApprovalStatusResponse(BaseModel):
    key_id: str
    current_approvals: int
    required_approvals: int
    is_approved: bool
    approval_percentage: int


@router.get("/approval-status/{key_id}", response_model=ApprovalStatusResponse)
async def get_approval_status(key_id: str):
    try:
        blockchain = get_blockchain_service()
    except Exception as e:
        raise HTTPException(status_code=503, detail={"reason": "contract_misconfigured", "error": str(e)})
    status_data = blockchain.get_approval_status(key_id)

    if "error" in status_data:
        raise HTTPException(status_code=400, detail=status_data["error"])

    return ApprovalStatusResponse(**status_data)


@router.get("/authorities")
async def get_authorities_list():
    try:
        blockchain = get_blockchain_service()
    except Exception as e:
        raise HTTPException(status_code=503, detail={"reason": "contract_misconfigured", "error": str(e)})
    authorities = blockchain.get_authorities_info()
    return {
        "total_authorities": len(authorities),
        "required_approvals": blockchain.threshold,
        "authorities": authorities,
    }


class DecryptionRequest(BaseModel):
    file_id: str
    key_id: str
    approving_authorities: List[str]


@router.post("/decrypt")
async def decrypt_file(req: DecryptionRequest, db=Depends(get_db)):
    try:
        blockchain = get_blockchain_service()
    except Exception as e:
        raise HTTPException(status_code=503, detail={"reason": "contract_misconfigured", "error": str(e)})

    if not blockchain.verify_approval(req.key_id):
        return {"decrypted": False, "message": "Insufficient approvals"}

    file_record = db.query(SecureFile).filter(SecureFile.id == req.file_id).first()
    if not file_record:
        return {"decrypted": False, "message": "File not found"}

    from backend.abe.abe_key_manager import get_abe_manager

    abe = get_abe_manager()
    reconstructed_key = abe.collect_shares(
        file_id=req.file_id,
        approving_authorities=req.approving_authorities,
    )
    if not reconstructed_key:
        return {"decrypted": False, "message": "Key reconstruction failed"}

    with open(file_record.file_path, "rb") as f:
        encrypted_data = f.read()

    decrypted_data = abe.decrypt_file(encrypted_data, reconstructed_key, {})
    if not decrypted_data:
        return {"decrypted": False, "message": "Decryption failed"}

    out_dir = os.path.join("storage", "decrypted_files")
    os.makedirs(out_dir, exist_ok=True)
    out_path = os.path.join(out_dir, file_record.filename)

    with open(out_path, "wb") as f:
        f.write(decrypted_data)

    mime_type, _ = mimetypes.guess_type(file_record.filename)
    return FileResponse(
        path=out_path,
        filename=file_record.filename,
        media_type=mime_type or "application/octet-stream",
    )


class SimulateApprovalRequest(BaseModel):
    key_id: str
    authority_addresses: List[str]


@router.post("/simulate-approvals")
async def simulate_approvals(req: SimulateApprovalRequest):
    try:
        blockchain = get_blockchain_service()
    except Exception as e:
        raise HTTPException(status_code=503, detail={"reason": "contract_misconfigured", "error": str(e)})
    results = []

    if not blockchain.check_connection():
        raise HTTPException(status_code=503, detail={"reason": "blockchain_unavailable", "message": "Not connected to Ganache"})

    for addr in req.authority_addresses:
        if not blockchain.is_authority(addr):
            results.append({"authority": addr, "tx_hash": None, "error": "Not an authority (per contract)"})
            continue

        tx, err = blockchain.approve_key(req.key_id, addr)
        results.append({"authority": addr, "tx_hash": tx, "error": err})

    failed = [r for r in results if not r.get("tx_hash")]
    if failed:
        raise HTTPException(
            status_code=400,
            detail={
                "reason": "approval_transactions_failed",
                "message": "One or more authority approval transactions failed (check authority addresses and contract deployment).",
                "results": results,
            },
        )

    return {"results": results}
