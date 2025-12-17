from fastapi import APIRouter, UploadFile, File, Depends, HTTPException
from sqlalchemy.orm import Session

from backend.database import SessionLocal
from backend.models import SecureFile, User
from backend.aes.aes_utils import generate_aes_key, encrypt_file, decrypt_file
from backend.abe.cpabe_utils import encrypt_aes_key, decrypt_aes_key
from backend.storage.file_storage import save_encrypted_file, load_encrypted_file


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

router = APIRouter(prefix="/files")


# =========================
# UPLOAD FILEfrom fastapi import APIRouter, UploadFile, File, Depends, HTTPException
from sqlalchemy.orm import Session

from backend.database import SessionLocal
from backend.models import SecureFile, User
from backend.aes.aes_utils import generate_aes_key, encrypt_file, decrypt_file
from backend.abe.cpabe_utils import encrypt_aes_key, decrypt_aes_key
from backend.storage.file_storage import save_encrypted_file, load_encrypted_file

# DB dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

router = APIRouter()   # ✅ NO prefix here


# =========================
# UPLOAD FILE
# =========================
@router.post("/upload")
async def upload_file(
    file: UploadFile = File(...),
    policy: str = "role:admin",
    username: str = "user1",
    db: Session = Depends(get_db)
):
    raw_data = await file.read()

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

    return {"message": "File uploaded securely"}


# =========================
# DOWNLOAD FILE
# =========================
@router.get("/download/{file_id}")
def download_file(
    file_id: int,
    username: str = "user1",
    db: Session = Depends(get_db)
):
    secure_file = db.query(SecureFile).filter(SecureFile.id == file_id).first()
    if not secure_file:
        raise HTTPException(status_code=404, detail="File not found")

    user = db.query(User).filter(User.username == username).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    attributes = [
        f"role:{user.role}",
        f"dept:{user.department}",
        f"clearance:{user.clearance}"
    ]

    user_key = {"attributes": set(attributes)}

    try:
        # NOTE: eval used only for academic prototype
        aes_key = decrypt_aes_key(
            eval(secure_file.encrypted_key.decode()),
            user_key
        )
    except Exception:
        raise HTTPException(status_code=403, detail="Access denied")

    encrypted_blob = load_encrypted_file(secure_file.file_path)
    iv = encrypted_blob[:16]
    ciphertext = encrypted_blob[16:]

    decrypted_data = decrypt_file(ciphertext, aes_key, iv)

    return {
        "filename": secure_file.filename,
        "data": decrypted_data.decode(errors="ignore")
    }

# =========================
@router.post("/upload")
async def upload_file(
    file: UploadFile = File(...),
    policy: str = "role:admin",
    username: str = "user1",
    db: Session = Depends(get_db)
):
    # Read file
    raw_data = await file.read()

    # AES encrypt file
    aes_key = generate_aes_key()
    iv, encrypted_data = encrypt_file(raw_data, aes_key)

    # Save encrypted file to disk
    file_path = save_encrypted_file(iv + encrypted_data)

    # CP-ABE encrypt AES key
    encrypted_key = encrypt_aes_key(aes_key, policy)

    # Store metadata in DB
    secure_file = SecureFile(
        filename=file.filename,
        owner=username,
        file_path=file_path,
        encrypted_key=str(encrypted_key).encode(),
        policy=policy
    )

    db.add(secure_file)
    db.commit()

    return {"message": "File uploaded securely"}


# =========================
# DOWNLOAD FILE
# =========================
@router.get("/download/{file_id}")
def download_file(
    file_id: int,
    username: str = "user1",
    db: Session = Depends(get_db)
):
    secure_file = db.query(SecureFile).filter(SecureFile.id == file_id).first()
    if not secure_file:
        raise HTTPException(status_code=404, detail="File not found")

    user = db.query(User).filter(User.username == username).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

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
        raise HTTPException(status_code=403, detail="Access denied")

    encrypted_blob = load_encrypted_file(secure_file.file_path)
    iv = encrypted_blob[:16]
    ciphertext = encrypted_blob[16:]

    decrypted_data = decrypt_file(ciphertext, aes_key, iv)

    return {
        "filename": secure_file.filename,
        "data": decrypted_data.decode(errors="ignore")
    }
