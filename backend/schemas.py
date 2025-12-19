from pydantic import BaseModel   # ✅ THIS WAS MISSING

class UserCreate(BaseModel):
    username: str
    password: str
    role: str

class UserLogin(BaseModel):
    username: str
    password: str


class UserAttributes(BaseModel):
    role: str
    department: str
    clearance: str
