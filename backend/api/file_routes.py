
from fastapi import APIRouter, UploadFile, File, Form, Depends, HTTPException
from fastapi.responses import StreamingResponse
import mimetypes
from sqlalchemy.orm import Session
import io
import os
import shutil
from backend.database import SessionLocal
from backend.models import SecureFile, User
from backend.aes.aes_utils import generate_aes_key, encrypt_file, decrypt_file
from backend.abe.cpabe_utils import encrypt_aes_key, decrypt_aes_key
from backend.storage.file_storage import save_encrypted_file, load_encrypted_file, delete_encrypted_file
from backend.blockchain.blockchain_auth import get_blockchain_service
from backend.abe.abe_key_manager import get_abe_manager
import json
import base64

# -------------------------------
# Router
# -------------------------------
router = APIRouter(prefix="/files", tags=["Files"])

# -------------------------------
# DB Dependency
# -------------------------------
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# =====================================================
# LIST ALL FILES (for frontend display)
# =====================================================
@router.get("/all")
def list_all_files(db: Session = Depends(get_db)):
    files = db.query(SecureFile).all()
    return [
        {
            "id": f.id,
            "filename": f.filename,
            "owner": f.owner,
            "policy": f.policy
        }
        for f in files
    ]

# =====================================================
# UPLOAD FILE (ADMIN ONLY)
# =====================================================
@router.post("/upload")
async def upload_file(
    file: UploadFile = File(...),
    policy: str = Form(...),
    username: str = Form(...),
    db: Session = Depends(get_db)
):
    user = db.query(User).filter(User.username == username).first()
    if user is None:
        raise HTTPException(status_code=401, detail="User not found")

    if user.role.lower() != "admin":
        raise HTTPException(status_code=403, detail="Only admin can upload files")

    raw_data = await file.read()
    if not raw_data:
        raise HTTPException(status_code=400, detail="Empty file uploaded")

    aes_key = generate_aes_key()
    iv, encrypted_data = encrypt_file(raw_data, aes_key)

    file_path = save_encrypted_file(iv + encrypted_data)

    # Encrypt the AES key with the policy using CP-ABE logic
    encrypted_key_struct = encrypt_aes_key(aes_key, policy)
    secure_file = SecureFile(
        filename=file.filename,
        owner=username,
        file_path=file_path,
        encrypted_key=json.dumps({
            "encrypted_key": encrypted_key_struct["encrypted_key"].decode() if hasattr(encrypted_key_struct["encrypted_key"], 'decode') else base64.b64encode(encrypted_key_struct["encrypted_key"]).decode(),
            "policy": encrypted_key_struct["policy"],
            "fernet_key": encrypted_key_struct["fernet_key"].decode() if hasattr(encrypted_key_struct["fernet_key"], 'decode') else base64.b64encode(encrypted_key_struct["fernet_key"]).decode()
        }).encode(),
        policy=policy
    )

    db.add(secure_file)
    db.commit()
    db.refresh(secure_file)

    # Now split AES key into Shamir shares and persist per-authority
    try:
        blockchain = get_blockchain_service()
        abe = get_abe_manager()
        authorities = blockchain.authorities

        abe.split_key_to_shares(aes_key, str(secure_file.id), authorities)
    except Exception as e:
        # Cleanup on failure
        print(f"Error while splitting/storing shares: {e}")

    return {
        "message": "File uploaded, encrypted, and shares distributed to authorities",
        "file_id": secure_file.id
    }

# =====================================================
# DOWNLOAD / DECRYPT FILE
# =====================================================
@router.get("/download/{file_id}")
def download_file(
    file_id: int,
    username: str,
    key_id: str,
    db: Session = Depends(get_db)
):
    user = db.query(User).filter(User.username == username).first()
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")

    secure_file = db.query(SecureFile).filter(SecureFile.id == file_id).first()
    if secure_file is None:
        raise HTTPException(status_code=404, detail="File not found")

    # Check blockchain approval for the provided key_id
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
                "message": "Blockchain approval check failed. Ensure Ganache is running and KeyAuthority is deployed.",
                "error": str(e),
            },
        )

    attributes = {
        f"role:{user.role}",
        f"dept:{user.department}",
        f"clearance:{user.clearance}"
    }

    user_key = {"attributes": attributes}

    try:
        aes_key = decrypt_aes_key(
            json.loads(secure_file.encrypted_key.decode()),
            user_key
        )
    except Exception as e:
        raise HTTPException(status_code=403, detail=f"Access denied by policy: {str(e)}")

    encrypted_blob = load_encrypted_file(secure_file.file_path)
    iv = encrypted_blob[:16]
    ciphertext = encrypted_blob[16:]

    plaintext = decrypt_file(ciphertext, aes_key, iv)

    # Guess MIME type from original filename so browser saves with correct extension
    mime_type, _ = mimetypes.guess_type(secure_file.filename)
    if not mime_type:
        mime_type = "application/octet-stream"

    # Ensure filename is quoted in Content-Disposition
    headers = {"Content-Disposition": f'attachment; filename="{secure_file.filename}"'}

    return StreamingResponse(
        io.BytesIO(plaintext),
        media_type=mime_type,
        headers=headers
    )


# =====================================================
# DELETE FILE (ADMIN ONLY)
# =====================================================
@router.delete("/{file_id}")
def delete_file(
    file_id: int,
    username: str,
    db: Session = Depends(get_db)
):
    user = db.query(User).filter(User.username == username).first()
    if user is None:
        raise HTTPException(status_code=401, detail="User not found")

    if user.role.lower() != "admin":
        raise HTTPException(status_code=403, detail="Only admin can delete files")

    secure_file = db.query(SecureFile).filter(SecureFile.id == file_id).first()
    if secure_file is None:
        raise HTTPException(status_code=404, detail="File not found")

    # Delete encrypted blob from disk (best-effort)
    try:
        delete_encrypted_file(secure_file.file_path)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to delete encrypted file blob: {str(e)}")

    # Delete any stored shares for this file (best-effort)
    try:
        shares_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "storage", "shares", str(file_id)))
        if os.path.isdir(shares_dir):
            shutil.rmtree(shares_dir, ignore_errors=True)
    except Exception:
        # Shares are not required for runtime correctness; don't block deletion.
        pass

    db.delete(secure_file)
    db.commit()

    return {"message": "File deleted successfully", "file_id": file_id}
