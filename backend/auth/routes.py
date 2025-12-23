# from fastapi import APIRouter, Depends, HTTPException
# from sqlalchemy.orm import Session

# from backend.database import SessionLocal
# from backend.models import User
# from backend.schemas import LoginSchema, UserCreate, UserRoleAssign
# from passlib.context import CryptContext
# pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# def hash_password(password: str):
#     return pwd_context.hash(password)

# def verify_password(plain, hashed):
#     return pwd_context.verify(plain, hashed)

# router = APIRouter()

# def get_db():
#     db = SessionLocal()
#     try:
#         yield db
#     finally:
#         db.close()

# # =========================
# # REGISTER (NO ROLE HERE)
# # =========================
# from backend.schemas import UserCreate, LoginSchema

# @router.post("/register")
# def register(user: UserCreate, db: Session = Depends(get_db)):

#     if db.query(User).filter(User.username == user.username).first():
#         raise HTTPException(status_code=400, detail="User exists")

#     new_user = User(
#         username=user.username,
#         password=user.password,  # ⚠ plain for now
#         role=user.role,          # 🔥 ROLE COMES FROM FRONTEND
#         department="NA",
#         clearance="low"
#     )

#     db.add(new_user)
#     db.commit()

#     return {"message": "Registered successfully"}


# # =========================
# # LOGIN
# # =========================
# # @router.post("/login")
# # def login(user: UserLogin, db: Session = Depends(get_db)):
# #     db_user = db.query(User).filter(User.username == user.username).first()
# #     if not db_user or not verify_password(user.password, db_user.password):
# #         raise HTTPException(status_code=401, detail="Invalid credentials")

# #     return {
# #         "message": "Login successful",
# #         "role": db_user.role
# #     }
# @router.post("/login")
# def login(user_data: LoginSchema, db: Session = Depends(get_db)):
#     user = db.query(User).filter(User.username == user_data.username).first()

#     if not user or not verify_password(user_data.password, user.password):
#         raise HTTPException(status_code=401, detail="Invalid credentials")

#     return {
#         "username": user.username,
#         "role": user.role
#     }


# # =========================
# # ADMIN ASSIGNS ROLE (ABE ATTRIBUTES)
# # =========================
# @router.post("/assign-role/{username}")
# def assign_role(username: str, data: UserRoleAssign, db: Session = Depends(get_db)):
#     user = db.query(User).filter(User.username == username).first()
#     if not user:
#         raise HTTPException(404, "User not found")

#     user.role = data.role
#     user.department = data.department
#     user.clearance = data.clearance
#     db.commit()

#     return {"message": "Attributes assigned"}
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from backend.database import SessionLocal
from backend.models import User
from backend.schemas import LoginSchema, UserCreate

router = APIRouter()

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
        raise HTTPException(status_code=400, detail="User exists")

    new_user = User(
        username=user.username,
        password=user.password,   # 🔥 NO HASH
        role=user.role,
        department="NA",
        clearance="low"
    )

    db.add(new_user)
    db.commit()

    return {"message": "Registered successfully"}

# =========================
# LOGIN
# =========================
@router.post("/login")
def login(user_data: LoginSchema, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.username == user_data.username).first()

    if not user or user.password != user_data.password:
        raise HTTPException(status_code=401, detail="Invalid username or password")

    return {
        "username": user.username,
        "role": user.role
    }
