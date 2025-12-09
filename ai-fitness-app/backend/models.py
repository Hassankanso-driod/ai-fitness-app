"""
models.py - SQLAlchemy database models

Defines all database tables and relationships.
"""

from sqlalchemy import Column, Integer, String, Float, Boolean, ForeignKey, DateTime, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from database import Base


class User(Base):
    """User model - stores user information"""
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    first_name = Column(String(100), unique=True, index=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    age = Column(Integer, nullable=False)
    height_cm = Column(Float, nullable=False)
    weight_kg = Column(Float, nullable=False)
    goal = Column(String(20), nullable=False)  # gain, lose, maintain
    sex = Column(String(10), nullable=False)  # male, female
    role = Column(String(20), default="user")  # user, admin
    active = Column(Boolean, default=True)
    
    # Calculated fields
    bmi = Column(Float, nullable=True)
    bmr = Column(Float, nullable=True)
    water_intake_l = Column(Float, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    favorites = relationship("Favorite", back_populates="user", cascade="all, delete-orphan")


class Supplement(Base):
    """Supplement model - stores supplement information"""
    __tablename__ = "supplements"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(200), nullable=False, index=True)
    description = Column(Text, nullable=True)
    price = Column(Float, nullable=False)
    image_url = Column(String(500), nullable=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    favorites = relationship("Favorite", back_populates="supplement", cascade="all, delete-orphan")


class Favorite(Base):
    """Favorite model - stores user's favorite supplements"""
    __tablename__ = "favorites"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    supplement_id = Column(Integer, ForeignKey("supplements.id"), nullable=False)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    user = relationship("User", back_populates="favorites")
    supplement = relationship("Supplement", back_populates="favorites")

