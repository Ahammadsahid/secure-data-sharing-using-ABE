from fastapi import APIRouter, UploadFile, File, Depends, HTTPException
from sqlalchemy.orm import Session

from backend.database import SessionLocal
from backend.models import SecureFile, User
from backend.aes.aes_utils import generate_aes_key, encrypt_file, decrypt_file
from backend.abe.cpabe_utils import encrypt_aes_key, decrypt_aes_key
from backend.storage.file_storage import save_encrypted_file, load_encrypted_file
from backend.blockchain.blockchain_utils import is_key_approved

# -------------------------------
# Router
# -------------------------------
router = APIRouter(prefix="/files")

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
    policy: str = "",
    username: str = "",
    db: Session = Depends(get_db)
):
    # Check user
    user = db.query(User).filter(User.username == username).first()
    if not user or user.role != "admin":
        raise HTTPException(status_code=403, detail="Only admin can upload files")

    # Read file
    raw_data = await file.read()

    # AES Encryption
    aes_key = generate_aes_key()
    iv, encrypted_data = encrypt_file(raw_data, aes_key)

    # Save encrypted file
    file_path = save_encrypted_file(iv + encrypted_data)

    # CP-ABE encrypt AES key
    encrypted_key = encrypt_aes_key(aes_key, policy)

    # Store metadata
    secure_file = SecureFile(
        filename=file.filename,
        owner=username,
        file_path=file_path,
        encrypted_key=str(encrypted_key).encode(),
        policy=policy
    )

    db.add(secure_file)
    db.commit()

    return {
        "message": "File uploaded & encrypted successfully",
        "file_id": secure_file.id
    }


# =====================================================
# DOWNLOAD / DECRYPT FILE (BLOCKCHAIN + ABE)
# =====================================================
@router.get("/download/{file_id}")
def download_file(
    file_id: int,
    username: str,
    key_id: str,
    db: Session = Depends(get_db)
):
    # User check
    user = db.query(User).filter(User.username == username).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # File check
    secure_file = db.query(SecureFile).filter(SecureFile.id == file_id).first()
    if not secure_file:
        raise HTTPException(status_code=404, detail="File not found")

    # -------------------------------
    # BLOCKCHAIN CHECK (4-of-7)
    # -------------------------------
    approved = is_key_approved(key_id)
    if not approved:
        raise HTTPException(
            status_code=403,
            detail="Blockchain approval not completed"
        )

    # -------------------------------
    # CP-ABE CHECK
    # -------------------------------
    attributes = [
        f"role:{user.role}",
        f"dept:{user.department}",
        f"clearance:{user.clearance}"
    ]

    user_key = {"attributes": set(attributes)}

    try:
        aes_key = decrypt_aes_key(
            eval(secure_file.encrypted_key.decode()),
            user_key
        )
    except Exception:
        raise HTTPException(status_code=403, detail="CP-ABE policy denied")

    # -------------------------------
    # AES DECRYPT FILE
    # -------------------------------
    encrypted_blob = load_encrypted_file(secure_file.file_path)
    iv = encrypted_blob[:16]
    ciphertext = encrypted_blob[16:]

    plaintext = decrypt_file(ciphertext, aes_key, iv)

    return {
        "filename": secure_file.filename,
        "data": plaintext.decode(errors="ignore")
    }
