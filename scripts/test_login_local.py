from backend.database import SessionLocal
from backend.models import User
from backend.auth.routes import verify_password

s = SessionLocal()
user = s.query(User).filter(User.username=='admin').first()
print('found user:', bool(user))
if user:
    print('stored hash:', user.password)
    print('verify admin123 ->', verify_password('admin123', user.password))
    print('verify wrong ->', verify_password('nope', user.password))
s.close()
