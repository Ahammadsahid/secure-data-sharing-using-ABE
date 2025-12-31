from fastapi import APIRouter, Depends, HTTPException
import logging
from fastapi import Request
from sqlalchemy.orm import Session
from passlib.context import CryptContext

from fastapi.security import HTTPBasic, HTTPBasicCredentials

from backend.database import SessionLocal
from backend.models import User, RecoveryCode
from backend.schemas import LoginSchema, UserCreate, ChangePasswordSchema, ForgotPasswordResetSchema

import re
import secrets
import string

router = APIRouter()

security = HTTPBasic()

# =========================
# PASSWORD UTILS
# =========================
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(plain: str, hashed: str) -> bool:
    return pwd_context.verify(plain, hashed)


def validate_password_strength(password: str) -> None:
    """Raise HTTPException if password doesn't meet basic strength requirements."""
    if password is None:
        raise HTTPException(status_code=400, detail="Password is required")

    # Professional baseline: length + upper/lower + number + special
    if len(password) < 8:
        raise HTTPException(status_code=400, detail="Password must be at least 8 characters")
    if not re.search(r"[A-Z]", password):
        raise HTTPException(status_code=400, detail="Password must include at least one uppercase letter")
    if not re.search(r"[a-z]", password):
        raise HTTPException(status_code=400, detail="Password must include at least one lowercase letter")
    if not re.search(r"\d", password):
        raise HTTPException(status_code=400, detail="Password must include at least one number")
    if not re.search(r"[^A-Za-z0-9]", password):
        raise HTTPException(status_code=400, detail="Password must include at least one special character")


def validate_initial_password(password: str) -> None:
    """Validation for admin-provisioned initial passwords.

    Per project requirement: admin can set a basic password and share it with the user.
    The user is expected to change it later to a strong password (enforced by /change-password and /forgot-password/reset).
    """
    if password is None:
        raise HTTPException(status_code=400, detail="Password is required")
    if len(password) < 6:
        raise HTTPException(status_code=400, detail="Initial password must be at least 6 characters")


def generate_recovery_code(length: int = 12) -> str:
    alphabet = string.ascii_uppercase + string.digits
    return "".join(secrets.choice(alphabet) for _ in range(length))


def generate_temporary_password(length: int = 8) -> str:
    # Basic initial password generator (not necessarily "strong")
    if length < 6:
        length = 6
    pool = string.ascii_letters + string.digits
    return "".join(secrets.choice(pool) for _ in range(length))

# =========================
# DB DEPENDENCY
# =========================
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def require_admin(credentials: HTTPBasicCredentials = Depends(security), db: Session = Depends(get_db)) -> User:
    user = db.query(User).filter(User.username == credentials.username).first()
    if not user or not verify_password(credentials.password, user.password):
        raise HTTPException(status_code=401, detail="Invalid admin credentials")
    if user.role != "admin":
        raise HTTPException(status_code=403, detail="Admin privileges required")
    return user

# =========================
# REGISTER
# =========================
@router.post("/register")
def register(user: UserCreate, db: Session = Depends(get_db)):
    # Public self-registration is disabled.
    # Accounts must be created by an admin via the admin endpoints.
    raise HTTPException(status_code=403, detail="Registration is disabled. Contact an admin to create your account.")


@router.get("/admin/users")
def admin_list_users(admin: User = Depends(require_admin), db: Session = Depends(get_db)):
    users = db.query(User).order_by(User.username.asc()).all()
    return {
        "items": [
            {
                "username": u.username,
                "role": u.role,
                "department": u.department,
                "clearance": u.clearance,
            }
            for u in users
        ]
    }


@router.post("/admin/users")
def admin_create_user(payload: dict, admin: User = Depends(require_admin), db: Session = Depends(get_db)):
    username = (payload.get("username") or "").strip()
    role = (payload.get("role") or "user").strip()
    # For admin accounts we don't require assigning department/clearance in the UI.
    # DB columns are non-null, so we set safe defaults.
    if role == "admin":
        department = "IT"
        clearance = "high"
    else:
        department = (payload.get("department") or "IT").strip()
        clearance = (payload.get("clearance") or "medium").strip()
    password = payload.get("password")

    if len(username) < 3:
        raise HTTPException(status_code=400, detail="Username must be at least 3 characters")

    allowed_roles = {"admin", "manager", "accountant", "employee", "worker", "user"}
    if role not in allowed_roles:
        raise HTTPException(status_code=400, detail=f"Invalid role. Allowed: {', '.join(sorted(allowed_roles))}")

    if db.query(User).filter(User.username == username).first():
        raise HTTPException(status_code=400, detail="User already exists")

    if not password:
        password = generate_temporary_password()
    validate_initial_password(password)

    new_user = User(
        username=username,
        password=hash_password(password),
        role=role,
        department=department,
        clearance=clearance,
    )
    db.add(new_user)
    db.commit()

    recovery_code = generate_recovery_code()
    existing = db.query(RecoveryCode).filter(RecoveryCode.username == username).first()
    if existing:
        existing.code_hash = hash_password(recovery_code)
        db.add(existing)
    else:
        db.add(RecoveryCode(username=username, code_hash=hash_password(recovery_code)))
    db.commit()

    # Note: Password hashes are not reversible; we return the temp password ONCE here.
    return {
        "message": "User created",
        "username": username,
        "temporary_password": password,
        "recovery_code": recovery_code,
    }


@router.post("/admin/users/{username}/reset-password")
def admin_reset_user_password(username: str, payload: dict, admin: User = Depends(require_admin), db: Session = Depends(get_db)):
    user = db.query(User).filter(User.username == username).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    new_password = payload.get("new_password") if isinstance(payload, dict) else None
    if not new_password:
        new_password = generate_temporary_password()
    validate_initial_password(new_password)
    user.password = hash_password(new_password)
    db.add(user)

    recovery_code = generate_recovery_code()
    recovery = db.query(RecoveryCode).filter(RecoveryCode.username == username).first()
    if recovery:
        recovery.code_hash = hash_password(recovery_code)
        db.add(recovery)
    else:
        db.add(RecoveryCode(username=username, code_hash=hash_password(recovery_code)))

    db.commit()
    return {
        "message": "Password reset",
        "username": username,
        "temporary_password": new_password,
        "recovery_code": recovery_code,
    }


@router.post("/admin/users/{username}/reset-recovery-code")
def admin_reset_recovery_code(username: str, admin: User = Depends(require_admin), db: Session = Depends(get_db)):
    user = db.query(User).filter(User.username == username).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # Create and return a NEW recovery code (cannot retrieve the old one because it's hashed)
    recovery_code = generate_recovery_code()
    recovery = db.query(RecoveryCode).filter(RecoveryCode.username == username).first()
    if recovery:
        recovery.code_hash = hash_password(recovery_code)
        db.add(recovery)
    else:
        db.add(RecoveryCode(username=username, code_hash=hash_password(recovery_code)))
    db.commit()

    return {
        "message": "Recovery code reset",
        "username": username,
        "recovery_code": recovery_code,
    }

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


@router.post("/change-password")
def change_password(payload: ChangePasswordSchema, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.username == payload.username).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    if not verify_password(payload.current_password, user.password):
        raise HTTPException(status_code=401, detail="Current password is incorrect")

    validate_password_strength(payload.new_password)
    user.password = hash_password(payload.new_password)
    db.add(user)
    db.commit()
    return {"message": "Password updated successfully"}


@router.post("/forgot-password/reset")
def forgot_password_reset(payload: ForgotPasswordResetSchema, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.username == payload.username).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    recovery = db.query(RecoveryCode).filter(RecoveryCode.username == payload.username).first()
    if not recovery:
        raise HTTPException(status_code=400, detail="No recovery code is set for this user")

    if not verify_password(payload.recovery_code, recovery.code_hash):
        raise HTTPException(status_code=401, detail="Invalid recovery code")

    validate_password_strength(payload.new_password)
    user.password = hash_password(payload.new_password)
    db.add(user)
    db.commit()
    return {"message": "Password reset successfully"}


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
