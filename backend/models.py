from sqlalchemy import Column, Integer, String, Float, ForeignKey, Boolean, DateTime, Text, func
from sqlalchemy.orm import relationship
from datetime import datetime
from database import Base


class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    first_name = Column(String(50), unique=True, index=True, nullable=False)
    sex = Column(String(10), nullable=True)
    age = Column(Integer, nullable=False)
    height_cm = Column(Float, nullable=False)
    weight_kg = Column(Float, nullable=False)
    goal = Column(String(20), nullable=False)
    password = Column(String(255), nullable=False)
    bmi = Column(Float, nullable=True)
    bmr = Column(Float, nullable=True)
    water_intake_l = Column(Float, nullable=True)
    role = Column(String(20), nullable=False, default="user")
    created_at = Column(DateTime, default=func.now())
    active = Column(Boolean, nullable=False, default=True)
    email = Column(String(100), nullable=True)
    last_login = Column(DateTime, default=func.now(), onupdate=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    
    # Relationships
    reminders = relationship("Reminder", back_populates="user")
    favorites = relationship("Favorite", back_populates="user")
    mealplans = relationship("MealPlan", back_populates="user")
    notifications = relationship("Notification", back_populates="user")
    workout_logs = relationship("WorkoutLog", back_populates="user")
    progress_entries = relationship("ProgressEntry", back_populates="user")
    # 🔥 NEW
    workout_plans = relationship("WorkoutPlan", back_populates="user")


class Reminder(Base):
    __tablename__ = "reminders"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    type = Column(String(50))  # water, meal, sleep, workout
    time = Column(String(50))
    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="reminders")


class Supplement(Base):
    __tablename__ = "supplements"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    description = Column(String(500), nullable=False)
    image_url = Column(String(255), nullable=True)  # Store filename only
    price = Column(Float, nullable=False)
    created_at = Column(DateTime, default=func.now())

    favorites = relationship("Favorite", back_populates="supplement")


class Favorite(Base):
    __tablename__ = "favorites"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    supplement_id = Column(Integer, ForeignKey("supplements.id"))
    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="favorites")
    supplement = relationship("Supplement", back_populates="favorites")


class MealPlan(Base):
    __tablename__ = "mealplans"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    goal = Column(String(50))
    calories = Column(Float)
    protein = Column(Float)
    carbs = Column(Float, nullable=True)
    fat = Column(Float, nullable=True)
    plan_json = Column(Text, nullable=True)  # الخطة الكاملة من GPT (weekly JSON)
    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="mealplans")

    


class Notification(Base):
    __tablename__ = "notifications"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    message = Column(String(255))
    status = Column(String(50), default="pending")
    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="notifications")


class WorkoutLog(Base):
    __tablename__ = "workout_logs"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    exercise_name = Column(String(255))
    category = Column(String(50))
    sets = Column(Integer)
    reps = Column(Integer)
    weight_kg = Column(Float, nullable=True)
    duration_minutes = Column(Integer, nullable=True)
    notes = Column(String(500), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="workout_logs")


class ProgressEntry(Base):
    __tablename__ = "progress_entries"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    weight_kg = Column(Float)
    bmi = Column(Float, nullable=True)
    body_fat_percentage = Column(Float, nullable=True)
    muscle_mass_kg = Column(Float, nullable=True)
    notes = Column(String(500), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="progress_entries")

class WorkoutPlan(Base):
    __tablename__ = "workout_plans"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    split = Column(String(50), nullable=True)          # full_body / upper_lower / ppl / bro_split
    days_per_week = Column(Integer, nullable=True)
    experience = Column(String(50), nullable=True)     # beginner / intermediate / advanced
    goal_focus = Column(String(50), nullable=True)     # strength / muscle_gain / fat_loss
    language = Column(String(5), nullable=True)        # "en" or "ar"
    plan_json = Column(Text, nullable=True)            # الخطة الكاملة (4 أسابيع) من GPT
    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="workout_plans")
