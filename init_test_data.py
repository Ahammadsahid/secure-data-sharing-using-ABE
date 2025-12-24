#!/usr/bin/env python3
"""
Initialize test data for the secure data sharing project
Creates test users (admin + regular users) with attributes
"""

import json
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from backend.database import Base
from backend.models import User

# Database setup
DATABASE_URL = "sqlite:///./sqlite/test.db"
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
Base.metadata.create_all(bind=engine)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Test users
TEST_USERS = [
    {
        "username": "admin",
        "password": "admin123",  # In production: hash this!
        "role": "admin",
        "department": "IT",
        "clearance": "high"
    },
    {
        "username": "alice",
        "password": "alice123",
        "role": "user",
        "department": "IT",
        "clearance": "high"
    },
    {
        "username": "bob",
        "password": "bob123",
        "role": "user",
        "department": "Finance",
        "clearance": "medium"
    },
    {
        "username": "charlie",
        "password": "charlie123",
        "role": "user",
        "department": "HR",
        "clearance": "low"
    }
]

def initialize_db():
    """Create test users in database"""
    db = SessionLocal()
    
    try:
        # Delete existing users (for fresh start)
        db.query(User).delete()
        db.commit()
        
        # Add test users
        for user_data in TEST_USERS:
            user = User(**user_data)
            db.add(user)
        
        db.commit()
        print("✅ Database initialized with test users:")
        print("\nTest Users:")
        print("-" * 60)
        for user_data in TEST_USERS:
            print(f"  Username: {user_data['username']:12} | Password: {user_data['password']}")
            print(f"    Role: {user_data['role']:8} | Department: {user_data['department']:10} | Clearance: {user_data['clearance']}")
            print()
        
    except Exception as e:
        print(f"❌ Error: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    initialize_db()
