import logging
import os
from pathlib import Path

# Load environment variables from project-root .env for local development.
# Safe in production: load_dotenv() is a no-op if no .env file exists.
from dotenv import load_dotenv

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.database import Base, engine, SessionLocal
from backend.auth.routes import router as auth_router
from backend.api.file_routes import router as file_router
from backend.api.access_routes import router as access_router
from backend.api.storage_routes import router as storage_router
from backend.models import User
from backend.auth.routes import hash_password, verify_password

logger = logging.getLogger("backend")
load_dotenv(dotenv_path=Path(__file__).resolve().parents[1] / ".env")
Base.metadata.create_all(bind=engine)

def init_test_users():
    db = SessionLocal()
    try:
        reset_demo_users = (os.getenv("DEMO_RESET_USERS") or "true").strip().lower() in {"1", "true", "yes", "y", "on"}

        demo_users = [
            ("admin", "admin123", "admin", "IT", "high"),
            ("manager", "manager123", "manager", "IT", "high"),
            ("alice", "alice123", "employee", "IT", "high"),
            ("bob", "bob123", "accountant", "Finance", "medium"),
            ("charlie", "charlie123", "worker", "HR", "low"),
        ]

        for username, password, role, department, clearance in demo_users:
            u = db.query(User).filter(User.username == username).first()
            if not u:
                u = User(
                    username=username,
                    password=hash_password(password),
                    role=role,
                    department=department,
                    clearance=clearance,
                )
                db.add(u)
                continue

            # Ensure role/attributes exist (demo stability)
            u.role = role
            u.department = department
            u.clearance = clearance

            if reset_demo_users and not verify_password(password, u.password):
                u.password = hash_password(password)
                db.add(u)

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
    allow_origins=list(
        {
            "http://localhost:3000",
            "http://127.0.0.1:3000",
            *[
                o.strip()
                for o in (os.getenv("CORS_ALLOW_ORIGINS") or "").split(",")
                if o.strip()
            ],
        }
    ),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["Content-Disposition"],
)

app.include_router(auth_router)
app.include_router(file_router)
app.include_router(access_router)
app.include_router(storage_router)

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
