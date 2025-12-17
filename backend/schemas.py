from pydantic import BaseModel

class UserCreate(BaseModel):
    username: str
    password: str

class UserLogin(BaseModel):
    username: str
    password: str

class UserAttributes(BaseModel):
    role: str
    department: str
    clearance: str
