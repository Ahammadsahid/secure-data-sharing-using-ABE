import logging

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.database import Base, engine, SessionLocal
from backend.auth.routes import router as auth_router
from backend.api.file_routes import router as file_router
from backend.api.access_routes import router as access_router
from backend.models import User
from backend.auth.routes import hash_password

logger = logging.getLogger("backend")
Base.metadata.create_all(bind=engine)

def init_test_users():
    db = SessionLocal()
    try:
        admin = db.query(User).filter(User.username == "admin").first()
        if not admin:
            admin = User(
                username="admin",
                password=hash_password("admin123"),
                role="admin",
                department="IT",
                clearance="high"
            )
            db.add(admin)
        
        manager = db.query(User).filter(User.username == "manager").first()
        if not manager:
            manager = User(
                username="manager",
                password=hash_password("manager123"),
                role="manager",
                department="IT",
                clearance="high"
            )
            db.add(manager)
        
        alice = db.query(User).filter(User.username == "alice").first()
        if not alice:
            alice = User(
                username="alice",
                password=hash_password("alice123"),
                role="employee",
                department="IT",
                clearance="high"
            )
            db.add(alice)
        
        bob = db.query(User).filter(User.username == "bob").first()
        if not bob:
            bob = User(
                username="bob",
                password=hash_password("bob123"),
                role="accountant",
                department="Finance",
                clearance="medium"
            )
            db.add(bob)
        
        charlie = db.query(User).filter(User.username == "charlie").first()
        if not charlie:
            charlie = User(
                username="charlie",
                password=hash_password("charlie123"),
                role="worker",
                department="HR",
                clearance="low"
            )
            db.add(charlie)
        
        db.commit()
        logger.info("Test users initialized")
    except Exception as e:
        logger.warning("Error initializing test users: %s", e)
    finally:
        db.close()

init_test_users()

app = FastAPI(
    title="Secure Data Sharing API",
    description="Secure file sharing with attribute policies and a local blockchain approval flow.",
    version="2.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://127.0.0.1:3000",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["Content-Disposition"],
)

app.include_router(auth_router)
app.include_router(file_router)
app.include_router(access_router)

@app.get("/")
async def root():
    return {
        "name": "Secure Data Sharing API",
        "version": "2.0",
        "features": [
            "Attribute-Based Encryption (ABE)",
            "Blockchain Authentication (4-of-7 threshold)",
            "Decentralized Access Control",
            "Smart Contract Integration (Ganache)"
        ],
        "docs": "/docs"
    }
