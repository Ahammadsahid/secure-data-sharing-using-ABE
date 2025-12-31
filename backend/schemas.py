from pydantic import BaseModel
from typing import Optional

class UserCreate(BaseModel):
    username: str
    password: str
    role: str   # 🔥 REQUIRED FOR YOUR PROJECT
    department: Optional[str] = "IT"  # Default to IT
    clearance: Optional[str] = "medium"  # Default to medium
class LoginSchema(BaseModel):
    username: str
    password: str


class ChangePasswordSchema(BaseModel):
    username: str
    current_password: str
    new_password: str


class ForgotPasswordResetSchema(BaseModel):
    username: str
    recovery_code: str
    new_password: str


class UserRoleAssign(BaseModel):
    role: str
    department: str
    clearance: str
