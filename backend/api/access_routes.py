"""
Decentralized Access Control Routes
Integrates blockchain authentication with ABE key management
"""
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from typing import List, Dict, Optional
from datetime import datetime
import json
import os
from fastapi.responses import FileResponse
import mimetypes

from backend.blockchain.blockchain_auth import get_blockchain_service
from backend.database import SessionLocal
from backend.models import User, SecureFile

router = APIRouter(prefix="/api/access", tags=["Decentralized Access"])

# ============ Models ============

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

class ApprovalStatusResponse(BaseModel):
    key_id: str
    current_approvals: int
    required_approvals: int
    is_approved: bool
    approval_percentage: int

class DecryptionRequest(BaseModel):
    file_id: str
    key_id: str
    approving_authorities: List[str]

class DecryptionResponse(BaseModel):
    file_id: str
    decrypted: bool
    message: str
    decryption_key: Optional[str] = None

# ============ Database Helper ============

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# ============ Routes ============

@router.post("/blockchain/status")
async def check_blockchain_status():
    """Check blockchain connection and contract status"""
    try:
        blockchain = get_blockchain_service()
        is_connected = blockchain.check_connection()
        
        if not is_connected:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Blockchain network not available"
            )
        
        return {
            "status": "connected",
            "network": "Ganache",
            "contract_address": blockchain.contract_address,
            "rpc_url": "http://127.0.0.1:7545",
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Blockchain error: {str(e)}"
        )

@router.post("/request-key-approval", response_model=KeyApprovalResponse)
async def request_key_approval(request: KeyApprovalRequest):
    """
    Initiate decentralized key approval process
    
    Flow:
    1. User uploads file with ABE encryption
    2. Key is split into 4-of-7 shares
    3. Shares are distributed to 7 authorities
    4. User requests approval from authorities
    5. Each authority verifies user attributes via blockchain
    6. Once 4 approvals received, user can decrypt
    """
    try:
        blockchain = get_blockchain_service()
        
        # Initiate approval request
        approval_data = blockchain.initiate_key_approval(
            file_id=request.file_id,
            user_id=request.user_id,
            user_attributes=request.user_attributes
        )
        
        return KeyApprovalResponse(
            key_id=approval_data["key_id"],
            file_id=request.file_id,
            authorities=approval_data["authorities"],
            threshold=approval_data["threshold"],
            required_approvals=approval_data["threshold"],
            status="pending",
            expiration=approval_data["expiration"]
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create approval request: {str(e)}"
        )

@router.get("/approval-status/{key_id}", response_model=ApprovalStatusResponse)
async def get_approval_status(key_id: str):
    """
    Get current approval status for a key
    Shows how many authorities have approved (need 4/7)
    """
    try:
        blockchain = get_blockchain_service()
        status_data = blockchain.get_approval_status(key_id)
        
        if "error" in status_data:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=status_data["error"]
            )
        
        return ApprovalStatusResponse(**status_data)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get approval status: {str(e)}"
        )

@router.get("/authorities")
async def get_authorities_list():
    """
    Get list of all 7 authorities and their approval status
    Shows which authorities can approve decryption
    """
    try:
        blockchain = get_blockchain_service()
        authorities = blockchain.get_authorities_info()
        
        return {
            "total_authorities": len(authorities),
            "required_approvals": blockchain.threshold,
            "authorities": authorities,
            "threshold_info": f"{blockchain.threshold} out of {len(authorities)} approvals required"
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get authorities: {str(e)}"
        )

@router.post("/decrypt")
async def decrypt_file(request: DecryptionRequest, db = Depends(get_db)):
    """
    Decrypt file after collecting 4 out of 7 approvals
    
    Process:
    1. Verify 4+ authorities have approved via blockchain
    2. Collect key shares from blockchain
    3. Reconstruct original key using Shamir's Secret Sharing
    4. Decrypt file content
    """
    try:
        blockchain = get_blockchain_service()
        # Lazy import ABE manager to avoid import-time dependency on charm
        from backend.abe.abe_key_manager import get_abe_manager
        abe = get_abe_manager()
        
        # Check if key is approved (4+ authorities)
        if not blockchain.verify_approval(request.key_id):
            return DecryptionResponse(
                file_id=request.file_id,
                decrypted=False,
                message="Insufficient approvals. Need 4 out of 7 authorities."
            )
        
        # Get file from database
        file_record = db.query(SecureFile).filter(
            SecureFile.id == request.file_id
        ).first()
        
        if not file_record:
            return DecryptionResponse(
                file_id=request.file_id,
                decrypted=False,
                message="File not found"
            )
        
        # Reconstruct key from shares
        reconstructed_key = abe.collect_shares(
            file_id=request.file_id,
            approving_authorities=request.approving_authorities
        )
        
        if not reconstructed_key:
            return DecryptionResponse(
                file_id=request.file_id,
                decrypted=False,
                message="Failed to reconstruct key from approvals"
            )
        
        # Read encrypted file
        with open(file_record.file_path, 'rb') as f:
            encrypted_data = f.read()
        
        # Decrypt file
        decrypted_data = abe.decrypt_file(
            encrypted_data=encrypted_data,
            decryption_key=reconstructed_key,
            user_attributes={}  # Would get from user session
        )
        
        if not decrypted_data:
            return DecryptionResponse(
                file_id=request.file_id,
                decrypted=False,
                message="Decryption failed"
            )

        # Write decrypted file to temporary path and return as downloadable response
        decrypted_dir = os.path.join(os.path.dirname(__file__), "..", "..", "storage", "decrypted_files")
        os.makedirs(decrypted_dir, exist_ok=True)
        out_name = f"decrypted_{request.file_id}_{int(datetime.utcnow().timestamp())}_{file_record.filename}"
        out_path = os.path.abspath(os.path.join(decrypted_dir, out_name))

        with open(out_path, 'wb') as outf:
            outf.write(decrypted_data)

        # Determine MIME type from original filename (default to application/octet-stream)
        mime_type, _ = mimetypes.guess_type(file_record.filename)
        if not mime_type:
            mime_type = 'application/octet-stream'

        # Return file with correct filename and Content-Type so browsers save with extension
        return FileResponse(path=out_path, filename=file_record.filename, media_type=mime_type)
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Decryption error: {str(e)}"
        )

@router.get("/approval-requirements/{file_id}")
async def get_approval_requirements(file_id: str, db = Depends(get_db)):
    """
    Get approval requirements for a specific file
    Shows policy, attributes needed, and current approval status
    """
    try:
        file_record = db.query(SecureFile).filter(
            SecureFile.id == file_id
        ).first()
        
        if not file_record:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="File not found"
            )
        
        from backend.abe.abe_key_manager import get_abe_manager
        abe = get_abe_manager()
        required_attrs = abe._parse_policy(file_record.policy)
        
        return {
            "file_id": file_id,
            "filename": file_record.filename,
            "owner": file_record.owner,
            "access_policy": file_record.policy,
            "required_attributes": required_attrs,
            "threshold": abe.threshold,
            "total_authorities": abe.total_shares,
            "approval_info": f"Requires {abe.threshold} out of {abe.total_shares} authorities to approve"
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error: {str(e)}"
        )

@router.post("/verify-attributes")
async def verify_user_attributes(user_id: str, file_id: str, db = Depends(get_db)):
    """
    Verify if user's attributes satisfy file's access policy
    """
    try:
        # Get user
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        # Get file
        file_record = db.query(SecureFile).filter(
            SecureFile.id == file_id
        ).first()
        if not file_record:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="File not found"
            )
        
        # Check attributes
        from backend.abe.abe_key_manager import get_abe_manager
        abe = get_abe_manager()
        user_attributes = {
            "role": user.role,
            "department": user.department,
            "clearance": user.clearance
        }
        
        satisfies = abe.verify_attributes(user_attributes, file_record.policy)
        
        return {
            "user_id": user_id,
            "file_id": file_id,
            "user_attributes": user_attributes,
            "policy": file_record.policy,
            "satisfies_policy": satisfies,
            "message": "User attributes satisfy file policy" if satisfies else "User attributes do not satisfy file policy"
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error: {str(e)}"
        )


class SimulateApprovalRequest(BaseModel):
    key_id: str
    authority_addresses: List[str]


@router.post("/simulate-approvals")
async def simulate_approvals(req: SimulateApprovalRequest):
    """Simulate authority approvals by sending transactions from the provided authority addresses (for local Ganache testing)."""
    blockchain = get_blockchain_service()
    results = []
    for addr in req.authority_addresses:
        tx_hash = blockchain.approve_key(req.key_id, addr)
        results.append({"authority": addr, "tx_hash": tx_hash})

    return {"results": results}
