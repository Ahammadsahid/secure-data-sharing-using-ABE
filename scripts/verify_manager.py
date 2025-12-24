import sys
sys.path.append(r'c:/7th sem/CAPSTON PROJECT/code/secure-data-sharing')
from backend.database import SessionLocal
from backend.models import User
from backend.auth.routes import verify_password

s = SessionLocal()
user = s.query(User).filter(User.username=='manager').first()
print('found user:', bool(user))
if user:
    print('stored hash:', user.password)
    print('verify manager123 ->', verify_password('manager123', user.password))
    print('verify wrong ->', verify_password('nope', user.password))
s.close()
