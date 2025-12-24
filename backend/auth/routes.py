from fastapi import APIRouter, Depends, HTTPException
import logging
from fastapi import Request
from sqlalchemy.orm import Session
from passlib.context import CryptContext

from backend.database import SessionLocal
from backend.models import User
from backend.schemas import LoginSchema, UserCreate

router = APIRouter()

# =========================
# PASSWORD UTILS
# =========================
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(plain: str, hashed: str) -> bool:
    return pwd_context.verify(plain, hashed)

# =========================
# DB DEPENDENCY
# =========================
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# =========================
# REGISTER
# =========================
@router.post("/register")
def register(user: UserCreate, db: Session = Depends(get_db)):

    if db.query(User).filter(User.username == user.username).first():
        raise HTTPException(status_code=400, detail="User already exists")

    new_user = User(
        username=user.username,
        password=hash_password(user.password),  # 🔥 HASHED
        role=user.role,                          # from frontend
        department=getattr(user, "department", "IT"),  # Default to IT
        clearance=getattr(user, "clearance", "medium")  # Default to medium
    )

    db.add(new_user)
    db.commit()

    return {"message": "Registered successfully"}

# =========================
# LOGIN
# =========================
@router.post("/login")
def login(user_data: LoginSchema, db: Session = Depends(get_db)):
    # Debug logs to help diagnose login issues during development
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger("auth")

    logger.info(f"Login attempt for username: {user_data.username}")

    user = db.query(User).filter(User.username == user_data.username).first()

    if not user:
        logger.warning(f"Login failed: user not found: {user_data.username}")
        raise HTTPException(status_code=401, detail="Invalid username or password")

    pw_ok = verify_password(user_data.password, user.password)
    logger.info(f"Password verification for {user_data.username}: {pw_ok}")

    if not pw_ok:
        raise HTTPException(status_code=401, detail="Invalid username or password")

    return {
        "username": user.username,
        "role": user.role,
        "department": user.department,
        "clearance": user.clearance
    }


@router.post("/debug/reset-test-users")
def reset_test_users(request: Request):
    """Recreate or reset test users to known passwords (development helper).

    This endpoint is intended for local development only. It will recreate
    the default test users with known passwords (admin/admin123, manager/manager123, etc.).
    """
    # Only allow local requests for safety
    client = request.client.host
    if client not in ("127.0.0.1", "::1", "localhost"):
        raise HTTPException(status_code=403, detail="Forbidden")

    try:
        # import here to avoid circular imports at module import time
        from backend.main import init_test_users
        init_test_users()
        return {"message": "Test users reset/initialized"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/debug/set-password")
def set_user_password(payload: dict, request: Request):
    """Set a user's password (local-only dev helper).

    Body: {"username": "ahammad", "password": "newpass"}
    """
    client = request.client.host
    if client not in ("127.0.0.1", "::1", "localhost"):
        raise HTTPException(status_code=403, detail="Forbidden")

    username = payload.get("username")
    new_password = payload.get("password")
    if not username or not new_password:
        raise HTTPException(status_code=400, detail="username and password required")

    db = SessionLocal()
    try:
        user = db.query(User).filter(User.username == username).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        user.password = hash_password(new_password)
        db.add(user)
        db.commit()
        return {"message": f"Password for {username} updated"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        db.close()
