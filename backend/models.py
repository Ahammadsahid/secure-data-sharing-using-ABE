from sqlalchemy import Column, Integer, String, LargeBinary
from backend.database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True, nullable=False)
    password = Column(String, nullable=False)

    role = Column(String, default="user")
    department = Column(String, default="NA")
    clearance = Column(String, default="low")


class SecureFile(Base):
    __tablename__ = "secure_files"

    id = Column(Integer, primary_key=True, index=True)
    filename = Column(String, nullable=False)
    owner = Column(String, nullable=False)

    file_path = Column(String, nullable=False)        # 🔥 NEW
    encrypted_key = Column(LargeBinary, nullable=False)
    policy = Column(String, nullable=False)
