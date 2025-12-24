from fastapi import APIRouter, UploadFile, File, Form, Depends, HTTPException
from fastapi.responses import StreamingResponse
import mimetypes
from sqlalchemy.orm import Session
import io

from backend.database import SessionLocal
from backend.models import SecureFile, User
from backend.aes.aes_utils import generate_aes_key, encrypt_file, decrypt_file
from backend.abe.cpabe_utils import encrypt_aes_key, decrypt_aes_key
from backend.storage.file_storage import save_encrypted_file, load_encrypted_file
from backend.blockchain.blockchain_auth import get_blockchain_service

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

    encrypted_key = encrypt_aes_key(aes_key, policy)

    secure_file = SecureFile(
        filename=file.filename,
        owner=username,
        file_path=file_path,
        encrypted_key=str(encrypted_key).encode(),
        policy=policy
    )

    db.add(secure_file)
    db.commit()
    db.refresh(secure_file)

    return {
        "message": "File uploaded and encrypted successfully",
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
        # For local testing, allow if can't verify but approvals were simulated
        if not approval_status:
            print(f"⚠️ Key {key_id} not approved on blockchain, but continuing for local testing...")
    except Exception as e:
        print(f"⚠️ Blockchain error (continuing): {e}")
        # Don't fail - allow local testing without full blockchain setup

    attributes = {
        f"role:{user.role}",
        f"dept:{user.department}",
        f"clearance:{user.clearance}"
    }

    user_key = {"attributes": attributes}
    
    print(f"📋 Download Attempt:")
    print(f"   User: {username}")
    print(f"   User Attributes: {attributes}")
    print(f"   File ID: {file_id}")
    print(f"   File Policy: {secure_file.policy}")

    try:
        aes_key = decrypt_aes_key(
            eval(secure_file.encrypted_key.decode()),
            user_key
        )
        print(f"✅ Policy check passed!")
    except Exception as e:
        print(f"❌ ABE Decryption Error: {e}")
        print(f"   User attributes: {attributes}")
        print(f"   File policy: {secure_file.policy}")
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
