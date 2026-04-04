#!/usr/bin/env python3
"""
Script to create an initial admin user for the finance dashboard.
Run this once to set up the first admin user.
"""

from app.core.config import get_settings
from app.db.session import engine
from app.models.user import User
from app.utils.security import hash_password
from sqlalchemy.orm import sessionmaker

def create_admin_user():
    settings = get_settings()

    # Don't call create_all() – Alembic already manages tables and indexes
    # Base.metadata.create_all(bind=engine)

    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db = SessionLocal()

    try:
        # Check if admin user already exists
        existing_admin = db.query(User).filter(User.role == "admin").first()
        if existing_admin:
            print(f"Admin user already exists: {existing_admin.email}")
            return

        print("Using DB at:", engine.url)

        # Create admin user
        admin_user = User(
            email="admin@example.com",
            full_name="Admin User",
            password_hash=hash_password("admin"),  # Make sure hash_password works
            role="admin",
            is_active=True,
        )

        db.add(admin_user)
        db.commit()
        db.refresh(admin_user)

        print("Admin user created successfully!")
        print("Email: admin@example.com")
        print("Password: admin")
        print("Role: admin")

    except Exception as e:
        db.rollback()
        print(f"Error creating admin user: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    create_admin_user()