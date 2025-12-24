# from passlib.context import CryptContext

# pwd_context = CryptContext(
#     schemes=["pbkdf2_sha256"],
#     deprecated="auto"
# )

# def hash_password(password: str):
#     return pwd_context.hash(password)

# def verify_password(password: str, hashed: str):
#     return pwd_context.verify(password, hashed)



from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(plain: str, hashed: str) -> bool:
    return pwd_context.verify(plain, hashed)
