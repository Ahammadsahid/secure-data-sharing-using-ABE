from pydantic import BaseModel

class UserCreate(BaseModel):
    username: str
    password: str
    role: str   # 🔥 REQUIRED FOR YOUR PROJECT

class LoginSchema(BaseModel):
    username: str
    password: str


class UserRoleAssign(BaseModel):
    role: str
    department: str
    clearance: str
