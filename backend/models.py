from sqlalchemy import Column, Integer, String
from backend.database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    password = Column(String)

    role = Column(String, default="user")        # admin / user
    department = Column(String, default="NA")
    clearance = Column(String, default="low")


from sqlalchemy import Column, Integer, String, LargeBinary

class SecureFile(Base):
    __tablename__ = "files"

    id = Column(Integer, primary_key=True, index=True)
    filename = Column(String)
    owner = Column(String)

    encrypted_data = Column(LargeBinary)
    encrypted_key = Column(LargeBinary)
    policy = Column(String)
