# models.py
from datetime import datetime

from sqlalchemy import (
    Column,
    Integer,
    String,
    Float,
    Boolean,
    DateTime,
    Text,
    ForeignKey,
)
from sqlalchemy.orm import relationship

from database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    first_name = Column(String(100), nullable=False)
    sex = Column(String(10), nullable=True)
    age = Column(Integer, nullable=True)
    height_cm = Column(Float, nullable=True)
    weight_kg = Column(Float, nullable=True)
    goal = Column(String(50), nullable=True)

    password = Column(String(255), nullable=False)

    bmi = Column(Float, nullable=True)
    bmr = Column(Float, nullable=True)
    water_intake_l = Column(Float, nullable=True)

    role = Column(String(20), default="user")
    email = Column(String(255), nullable=True)
    email_verified = Column(Boolean, default=False)
    email_verification_token = Column(String(255), nullable=True)
    password_reset_token = Column(String(255), nullable=True)
    password_reset_expires = Column(DateTime, nullable=True)

    active = Column(Boolean, default=True)
    last_login = Column(DateTime, nullable=True)

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=True)

    favorites = relationship("Favorite", back_populates="user", cascade="all, delete")
    meal_plans = relationship("MealPlan", back_populates="user", cascade="all, delete")


class Supplement(Base):
    __tablename__ = "supplements"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    price = Column(Float, nullable=False)
    image_url = Column(String(255), nullable=True)
    image_urls = Column(Text, nullable=True)

    favorites = relationship("Favorite", back_populates="supplement", cascade="all, delete")


class Favorite(Base):
    __tablename__ = "favorites"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    supplement_id = Column(Integer, ForeignKey("supplements.id"), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="favorites")
    supplement = relationship("Supplement", back_populates="favorites")


class MealPlan(Base):
    __tablename__ = "mealplans"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    title = Column(String(255), nullable=True)
    goal = Column(String(50), nullable=True)

    diet_style = Column(String(100), nullable=True)
    cuisine = Column(String(100), nullable=True)
    meals_per_day = Column(Integer, nullable=True)
    cooking_time = Column(String(50), nullable=True)
    budget_level = Column(String(50), nullable=True)

    likes = Column(Text, nullable=True)
    dislikes = Column(Text, nullable=True)
    allergies = Column(Text, nullable=True)
    medical_flags = Column(Text, nullable=True)  # store json string

    language = Column(String(10), nullable=True)
    plan_duration_days = Column(Integer, default=7)

    calories = Column(Float, nullable=True)
    protein = Column(Float, nullable=True)
    carbs = Column(Float, nullable=True)
    fat = Column(Float, nullable=True)
    water_liters = Column(Float, nullable=True)

    plan_json = Column(Text, nullable=True)

    version = Column(Integer, default=1)
    is_active = Column(Boolean, default=True)

    prompt_version = Column(String(20), nullable=True)
    model = Column(String(100), nullable=True)

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=True)

    user = relationship("User", back_populates="meal_plans")


class Reminder(Base):
    __tablename__ = "reminders"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    type = Column(String(50), nullable=False)
    time = Column(String(10), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)


class WaterIntake(Base):
    __tablename__ = "water_intakes"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    amount_ml = Column(Integer, nullable=False)
    date = Column(DateTime, default=datetime.utcnow)


class WorkoutLog(Base):
    __tablename__ = "workout_logs"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    exercise_name = Column(String(255), nullable=False)
    category = Column(String(100), nullable=True)
    sets = Column(Integer, nullable=False)
    reps = Column(Integer, nullable=False)
    weight_kg = Column(Float, nullable=True)
    duration_minutes = Column(Integer, nullable=True)
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)


class ProgressEntry(Base):
    __tablename__ = "progress_entries"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    weight_kg = Column(Float, nullable=False)
    bmi = Column(Float, nullable=True)
    body_fat_percentage = Column(Float, nullable=True)
    muscle_mass_kg = Column(Float, nullable=True)
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)


class Notification(Base):
    __tablename__ = "notifications"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    message = Column(Text, nullable=False)
    status = Column(String(50), default="pending")
    created_at = Column(DateTime, default=datetime.utcnow)


class WorkoutPlan(Base):
    __tablename__ = "workout_plans"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    split = Column(String(50), nullable=True)
    days_per_week = Column(Integer, nullable=True)
    experience = Column(String(50), nullable=True)
    goal_focus = Column(String(50), nullable=True)
    language = Column(String(10), nullable=True)
    plan_json = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
