"""
database.py - Database connection and session management

This module handles database connection using SQLAlchemy.
Supports SQLite for development/testing and MySQL for production.
"""

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os

# Database URL - Default to SQLite for easier setup
# For MySQL, set environment variable: DATABASE_URL="mysql://user:password@localhost/fitness_ai"
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "sqlite:///./fitness_ai.db"  # SQLite for development
)

# Create engine
if DATABASE_URL.startswith("sqlite"):
    engine = create_engine(
        DATABASE_URL,
        connect_args={"check_same_thread": False}  # SQLite specific
    )
else:
    engine = create_engine(DATABASE_URL)

# Create session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class for models
Base = declarative_base()

def get_db():
    """Dependency to get database session"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

