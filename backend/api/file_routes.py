# FastAPI imports for building REST APIs
from fastapi import APIRouter, UploadFile, File, Form, Depends, HTTPException
from fastapi.responses import StreamingResponse

# Used to detect MIME type of files (pdf, jpg, etc.)
import mimetypes

# SQLAlchemy session handling
from sqlalchemy.orm import Session

# Used for in-memory byte streaming
import io

# OS and file utilities
import os
import shutil

# Database session factory
from backend.database import SessionLocal

# Database models
from backend.models import SecureFile, User

# AES utilities: key generation, encryption, decryption
from backend.aes.aes_utils import generate_aes_key, encrypt_blob, decrypt_blob

# Attribute-Based Encryption utilities (for encrypting/decrypting AES key)
from backend.abe.cpabe_utils import encrypt_aes_key, decrypt_aes_key

# Encrypted blob storage (MongoDB GridFS by default; configurable via STORAGE_BACKEND)
from backend.storage.storage_backend import (
    save_encrypted_blob,
    load_encrypted_blob,
    delete_encrypted_blob,
)

# Blockchain approval service (4-of-7 authority voting)
from backend.blockchain.blockchain_auth import get_blockchain_service

# ABE key manager (for demo key-share distribution)
from backend.abe.abe_key_manager import get_abe_manager

# JSON and encoding utilities
import json
import base64

# Regex used for parsing policy attributes
import re

# Used to safely encode filenames in HTTP headers
from urllib.parse import quote


# Create FastAPI router with /files prefix
router = APIRouter(prefix="/files", tags=["Files"])


# Helper function: Extract attributes from policy

def _extract_policy_tokens(policy: str) -> list:
    """
    Extract attribute tokens from policy string.
    Example:
        policy = "role:admin AND department:IT"
        output = ["role:admin", "department:IT"]
    """
    if not policy:
        return []

    # Regex finds patterns like key:value
    tokens = re.findall(r"[A-Za-z_]+:[A-Za-z0-9_-]+", policy)

    # Remove duplicates while preserving order
    seen = set()
    out = []
    for t in tokens:
        if t not in seen:
            seen.add(t)
            out.append(t)
    return out



# Helper function: Safe filename for downloads

def _content_disposition_filename(filename: str) -> str:
    """
    Builds a Content-Disposition header that supports:
    - ASCII filenames
    - Unicode filenames
    - Browser compatibility
    """
    name = filename or "download"

    # ASCII fallback (remove non-ASCII characters)
    ascii_fallback = name.encode("ascii", "ignore").decode("ascii")
    if not ascii_fallback:
        ascii_fallback = "download"

    # Prevent header injection
    ascii_fallback = ascii_fallback.replace("\\", "_").replace('"', "'")

    # Proper UTF-8 encoding for modern browsers
    utf8_quoted = quote(name, safe="")
    return f"attachment; filename=\"{ascii_fallback}\"; filename*=UTF-8''{utf8_quoted}"


# Database dependency (auto open/close session)

def get_db():
    # Creates a new DB session
    db = SessionLocal()
    try:
        yield db
    finally:
        # Ensures DB session is closed after request
        db.close()


# API: List all uploaded files (metadata only)

@router.get("/all")
def list_all_files(db: Session = Depends(get_db)):
    # Fetch all SecureFile records
    files = db.query(SecureFile).all()

    # Return file metadata (not file content)
    return [
        {
            "id": f.id,
            "filename": f.filename,
            "owner": f.owner,
            "policy": f.policy,
            "required_attributes": _extract_policy_tokens(f.policy),
        }
        for f in files
    ]



# API: Upload file (ADMIN ONLY)

@router.post("/upload")
async def upload_file(
    file: UploadFile = File(...),        # File sent by client
    policy: str = Form(...),             # Access policy (ABE)
    username: str = Form(...),           # Uploader username
    db: Session = Depends(get_db)
):
    # Verify user exists
    user = db.query(User).filter(User.username == username).first()
    if user is None:
        raise HTTPException(status_code=401, detail="User not found")

    # Only admin can upload files
    if user.role.lower() != "admin":
        raise HTTPException(status_code=403, detail="Only admin can upload files")

    # Read file content as bytes
    raw_data = await file.read()
    if not raw_data:
        raise HTTPException(status_code=400, detail="Empty file uploaded")

    # Generate random AES-256 key
    aes_key = generate_aes_key()

    # Encrypt file using AES
    encrypted_blob = encrypt_blob(raw_data, aes_key)

    # Store encrypted file in the configured storage backend
    file_path = save_encrypted_blob(
        encrypted_blob,
        filename=file.filename,
        metadata={"owner": username, "policy": policy},
    )

    # Encrypt AES key using ABE policy
    encrypted_key_struct = encrypt_aes_key(aes_key, policy)

    # Create SecureFile DB record
    secure_file = SecureFile(
        filename=file.filename,
        owner=username,
        file_path=file_path,

        # Store encrypted AES key + policy + Fernet key as JSON
        encrypted_key=json.dumps({
            "encrypted_key": encrypted_key_struct["encrypted_key"].decode()
            if hasattr(encrypted_key_struct["encrypted_key"], 'decode')
            else base64.b64encode(encrypted_key_struct["encrypted_key"]).decode(),

            "policy": encrypted_key_struct["policy"],

            "fernet_key": encrypted_key_struct["fernet_key"].decode()
            if hasattr(encrypted_key_struct["fernet_key"], 'decode')
            else base64.b64encode(encrypted_key_struct["fernet_key"]).decode()
        }).encode(),

        policy=policy
    )

    # Save metadata to database
    db.add(secure_file)
    db.commit()
    db.refresh(secure_file)

    # OPTIONAL: Distribute AES key shares to authorities (demo logic)
    try:
        blockchain = get_blockchain_service()
        abe = get_abe_manager()
        authorities = blockchain.authorities

        abe.split_key_to_shares(aes_key, str(secure_file.id), authorities)
    except Exception as e:
        print(f"Error while splitting/storing shares: {e}")

    return {
        "message": "File uploaded, encrypted, and shares distributed to authorities",
        "file_id": secure_file.id
    }



# API: Download file (Policy + Blockchain Protected)

@router.get("/download/{file_id}")
def download_file(
    file_id: int,
    username: str,
    key_id: str,                         # Blockchain approval key ID
    db: Session = Depends(get_db)
):
    # Verify user exists
    user = db.query(User).filter(User.username == username).first()
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")

    # Verify file exists
    secure_file = db.query(SecureFile).filter(SecureFile.id == file_id).first()
    if secure_file is None:
        raise HTTPException(status_code=404, detail="File not found")

    
    # BLOCKCHAIN APPROVAL CHECK (4-of-7)
    
    try:
        blockchain = get_blockchain_service()
        approval_status = blockchain.verify_approval(key_id)

        if not approval_status:
            status = blockchain.get_approval_status(key_id)
            raise HTTPException(
                status_code=403,
                detail={
                    "reason": "not_approved_on_blockchain",
                    "message": "Key has not reached the required authority-approval threshold on Ganache.",
                    "approval_status": status,
                },
            )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=503,
            detail={
                "reason": "blockchain_unavailable",
                "message": "Blockchain approval check failed.",
                "error": str(e),
            },
        )

    # Build user attributes for policy check
    attributes = {
        f"role:{user.role}",
        f"dept:{user.department}",
        f"department:{user.department}",
        f"clearance:{user.clearance}",
    }

    user_key = {"attributes": attributes}

   
    # ABE POLICY CHECK + AES KEY DECRYPTION
    
    try:
        aes_key = decrypt_aes_key(
            json.loads(secure_file.encrypted_key.decode()),
            user_key
        )
    except Exception as e:
        raise HTTPException(status_code=403, detail=f"Access denied by policy: {str(e)}")

    # Load encrypted file from storage
    encrypted_blob = load_encrypted_blob(secure_file.file_path)

    # Decrypt file using AES key
    plaintext = decrypt_blob(encrypted_blob, aes_key)

    # Guess MIME[Multipurpose Internet Mail Extensions] type
    mime_type, _ = mimetypes.guess_type(secure_file.filename)
    if not mime_type:
        mime_type = "application/octet-stream"

    # Safe filename header
    headers = {"Content-Disposition": _content_disposition_filename(secure_file.filename)}

    # Stream decrypted file to client
    return StreamingResponse(
        io.BytesIO(plaintext),
        media_type=mime_type,
        headers=headers
    )



# API: Delete file (ADMIN ONLY)

@router.delete("/{file_id}")
def delete_file(
    file_id: int,
    username: str,
    db: Session = Depends(get_db)
):
    # Verify user exists
    user = db.query(User).filter(User.username == username).first()
    if user is None:
        raise HTTPException(status_code=401, detail="User not found")

    # Only admin can delete files
    if user.role.lower() != "admin":
        raise HTTPException(status_code=403, detail="Only admin can delete files")

    # Verify file exists
    secure_file = db.query(SecureFile).filter(SecureFile.id == file_id).first()
    if secure_file is None:
        raise HTTPException(status_code=404, detail="File not found")

    # Delete encrypted file blob
    try:
        delete_encrypted_blob(secure_file.file_path)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to delete encrypted file blob: {str(e)}")

    # Delete stored key shares (if present)
    try:
        shares_dir = os.path.abspath(
            os.path.join(os.path.dirname(__file__), "..", "storage", "shares", str(file_id))
        )
        if os.path.isdir(shares_dir):
            shutil.rmtree(shares_dir, ignore_errors=True)
    except Exception:
        pass

    # Delete DB record
    db.delete(secure_file)
    db.commit()

    return {"message": "File deleted successfully", "file_id": file_id}
