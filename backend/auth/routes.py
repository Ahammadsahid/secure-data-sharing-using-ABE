from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from backend.database import SessionLocal
from backend.models import User
from backend.schemas import UserCreate, UserLogin, UserAttributes
from backend.auth.auth_utils import hash_password, verify_password, create_access_token

router = APIRouter(prefix="/auth")

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/register")
def register(user: UserCreate, db: Session = Depends(get_db)):
    if db.query(User).filter(User.username == user.username).first():
        raise HTTPException(status_code=400, detail="User exists")

    new_user = User(
        username=user.username,
        password=hash_password(user.password)
    )
    db.add(new_user)
    db.commit()
    return {"message": "User registered successfully"}

@router.post("/login")
def login(user: UserLogin, db: Session = Depends(get_db)):
    db_user = db.query(User).filter(User.username == user.username).first()
    if not db_user or not verify_password(user.password, db_user.password):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    token = create_access_token({"sub": db_user.username, "role": db_user.role})
    return {"access_token": token}

@router.put("/assign/{username}")
def assign_attributes(username: str, attrs: UserAttributes, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.username == username).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    user.role = attrs.role
    user.department = attrs.department
    user.clearance = attrs.clearance
    db.commit()

    return {"message": "Attributes assigned"}
