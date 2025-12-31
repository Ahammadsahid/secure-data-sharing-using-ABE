from sqlalchemy import Column, Integer, String, LargeBinary
from backend.database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True, nullable=False)
    password = Column(String, nullable=False)

    role = Column(String, nullable=False)
    department = Column(String, nullable=False)
    clearance = Column(String, nullable=False)

class SecureFile(Base):
    __tablename__ = "secure_files"

    id = Column(Integer, primary_key=True, index=True)
    filename = Column(String, nullable=False)
    owner = Column(String, nullable=False)

    file_path = Column(String, nullable=False)
    encrypted_key = Column(LargeBinary, nullable=False)
    policy = Column(String, nullable=False)


class RecoveryCode(Base):
    __tablename__ = "recovery_codes"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True, nullable=False)
    code_hash = Column(String, nullable=False)
