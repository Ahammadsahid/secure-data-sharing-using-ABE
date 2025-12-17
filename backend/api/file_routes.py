from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
import base64

from backend.database import SessionLocal
from backend.models import SecureFile, User
from backend.aes.aes_utils import generate_aes_key, encrypt_file, decrypt_file
from backend.abe.cpabe_utils import encrypt_aes_key, decrypt_aes_key
from backend.auth.routes import get_db

router = APIRouter(prefix="/files")


# -------------------------------
# Request Model (NO UploadFile)
# -------------------------------
class FileUploadRequest(BaseModel):
    filename: str
    data_base64: str
    policy: str
    username: str


# -------------------------------
# Upload API
# -------------------------------
@router.post("/upload")
def upload_file(payload: FileUploadRequest, db: Session = Depends(get_db)):
    try:
        file_bytes = base64.b64decode(payload.data_base64)
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid base64 data")

    # AES encrypt file
    aes_key = generate_aes_key()
    iv, encrypted_data = encrypt_file(file_bytes, aes_key)

    # CP-ABE encrypt AES key
    encrypted_key = encrypt_aes_key(aes_key, payload.policy)

    secure_file = SecureFile(
        filename=payload.filename,
        owner=payload.username,
        encrypted_data=iv + encrypted_data,
        encrypted_key=str(encrypted_key).encode(),
        policy=payload.policy
    )

    db.add(secure_file)
    db.commit()
    db.refresh(secure_file)

    return {
        "message": "File uploaded securely",
        "file_id": secure_file.id
    }


# -------------------------------
# Download API
# -------------------------------
@router.get("/download/{file_id}")
def download_file(
    file_id: int,
    username: str,
    db: Session = Depends(get_db)
):
    secure_file = db.query(SecureFile).filter(SecureFile.id == file_id).first()
    if not secure_file:
        raise HTTPException(status_code=404, detail="File not found")

    user = db.query(User).filter(User.username == username).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # Build user attributes
    attributes = {
        f"role:{user.role}",
        f"dept:{user.department}",
        f"clearance:{user.clearance}"
    }

    user_key = {"attributes": attributes}

    try:
        aes_key = decrypt_aes_key(
            eval(secure_file.encrypted_key.decode()),
            user_key
        )
    except Exception:
        raise HTTPException(status_code=403, detail="Access denied")

    # Split IV and ciphertext
    iv = secure_file.encrypted_data[:16]
    ciphertext = secure_file.encrypted_data[16:]

    decrypted_data = decrypt_file(ciphertext, aes_key, iv)

    return {
        "filename": secure_file.filename,
        "data_base64": base64.b64encode(decrypted_data).decode()
    }
