"""
crud.py - Database CRUD operations

Contains all database create, read, update, delete operations.
"""

from sqlalchemy.orm import Session
from sqlalchemy import and_
from typing import Optional, List
import models
import schemas
from auth import hash_password


def calculate_bmi(weight_kg: float, height_cm: float) -> float:
    """Calculate BMI (Body Mass Index)"""
    height_m = height_cm / 100
    return round(weight_kg / (height_m ** 2), 2)


def calculate_bmr(weight_kg: float, height_cm: float, age: int, sex: str) -> float:
    """Calculate BMR (Basal Metabolic Rate) using Mifflin-St Jeor Equation"""
    height_m = height_cm / 100
    
    if sex.lower() == "male":
        bmr = (10 * weight_kg) + (6.25 * height_cm) - (5 * age) + 5
    else:  # female
        bmr = (10 * weight_kg) + (6.25 * height_cm) - (5 * age) - 161
    
    return round(bmr, 2)


def calculate_water_intake(weight_kg: float) -> float:
    """Calculate daily water intake in liters (35ml per kg)"""
    return round((weight_kg * 35) / 1000, 2)


# User CRUD operations
def create_user(db: Session, user_data: schemas.UserCreate) -> models.User:
    """Create a new user with calculated BMI, BMR, and water intake"""
    # Check if user already exists
    existing_user = db.query(models.User).filter(
        models.User.first_name == user_data.first_name
    ).first()
    
    if existing_user:
        raise ValueError(f"User with name '{user_data.first_name}' already exists")
    
    # Calculate health metrics
    bmi = calculate_bmi(user_data.weight_kg, user_data.height_cm)
    bmr = calculate_bmr(
        user_data.weight_kg,
        user_data.height_cm,
        user_data.age,
        user_data.sex
    )
    water_intake = calculate_water_intake(user_data.weight_kg)
    
    # Create user object
    db_user = models.User(
        first_name=user_data.first_name,
        password_hash=hash_password(user_data.password),
        age=user_data.age,
        height_cm=user_data.height_cm,
        weight_kg=user_data.weight_kg,
        goal=user_data.goal,
        sex=user_data.sex,
        role=user_data.role,
        bmi=bmi,
        bmr=bmr,
        water_intake_l=water_intake,
        active=True
    )
    
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


def get_user_by_id(db: Session, user_id: int) -> Optional[models.User]:
    """Get user by ID"""
    return db.query(models.User).filter(models.User.id == user_id).first()


def get_user_by_name(db: Session, first_name: str) -> Optional[models.User]:
    """Get user by first name"""
    return db.query(models.User).filter(models.User.first_name == first_name).first()


def get_all_users(db: Session) -> List[models.User]:
    """Get all users"""
    return db.query(models.User).all()


def update_user(db: Session, user_id: int, user_update: schemas.UserUpdate) -> Optional[models.User]:
    """Update user information"""
    db_user = get_user_by_id(db, user_id)
    if not db_user:
        return None
    
    # Update fields if provided
    update_data = user_update.dict(exclude_unset=True)
    
    for field, value in update_data.items():
        setattr(db_user, field, value)
    
    # Recalculate health metrics if weight or height changed
    if "weight_kg" in update_data or "height_cm" in update_data:
        db_user.bmi = calculate_bmi(db_user.weight_kg, db_user.height_cm)
        db_user.bmr = calculate_bmr(
            db_user.weight_kg,
            db_user.height_cm,
            db_user.age,
            db_user.sex
        )
        db_user.water_intake_l = calculate_water_intake(db_user.weight_kg)
    
    db.commit()
    db.refresh(db_user)
    return db_user


def toggle_user_active(db: Session, user_id: int, active: bool) -> Optional[models.User]:
    """Toggle user active status"""
    db_user = get_user_by_id(db, user_id)
    if not db_user:
        return None
    
    db_user.active = active
    db.commit()
    db.refresh(db_user)
    return db_user


# Supplement CRUD operations
def add_supplement(db: Session, supplement_data: schemas.SupplementCreate, image_url: Optional[str] = None) -> models.Supplement:
    """Create a new supplement"""
    db_supplement = models.Supplement(
        name=supplement_data.name,
        description=supplement_data.description,
        price=supplement_data.price,
        image_url=image_url
    )
    
    db.add(db_supplement)
    db.commit()
    db.refresh(db_supplement)
    return db_supplement


def get_supplement_by_id(db: Session, supplement_id: int) -> Optional[models.Supplement]:
    """Get supplement by ID"""
    return db.query(models.Supplement).filter(models.Supplement.id == supplement_id).first()


def get_all_supplements(db: Session) -> List[models.Supplement]:
    """Get all supplements"""
    return db.query(models.Supplement).all()


def update_supplement(db: Session, supplement_id: int, supplement_update: schemas.SupplementUpdate) -> Optional[models.Supplement]:
    """Update supplement information"""
    db_supplement = get_supplement_by_id(db, supplement_id)
    if not db_supplement:
        return None
    
    update_data = supplement_update.dict(exclude_unset=True)
    
    for field, value in update_data.items():
        setattr(db_supplement, field, value)
    
    db.commit()
    db.refresh(db_supplement)
    return db_supplement


def delete_supplement(db: Session, supplement_id: int) -> bool:
    """Delete a supplement"""
    db_supplement = get_supplement_by_id(db, supplement_id)
    if not db_supplement:
        return False
    
    db.delete(db_supplement)
    db.commit()
    return True


# Favorite CRUD operations
def add_favorite(db: Session, user_id: int, supplement_id: int) -> models.Favorite:
    """Add a supplement to user's favorites"""
    # Check if already exists
    existing = db.query(models.Favorite).filter(
        and_(
            models.Favorite.user_id == user_id,
            models.Favorite.supplement_id == supplement_id
        )
    ).first()
    
    if existing:
        return existing
    
    db_favorite = models.Favorite(
        user_id=user_id,
        supplement_id=supplement_id
    )
    
    db.add(db_favorite)
    db.commit()
    db.refresh(db_favorite)
    return db_favorite


def get_user_favorites(db: Session, user_id: int) -> List[models.Favorite]:
    """Get all favorites for a user"""
    return db.query(models.Favorite).filter(
        models.Favorite.user_id == user_id
    ).all()


def remove_favorite(db: Session, favorite_id: int) -> bool:
    """Remove a favorite by ID"""
    db_favorite = db.query(models.Favorite).filter(models.Favorite.id == favorite_id).first()
    if not db_favorite:
        return False
    
    db.delete(db_favorite)
    db.commit()
    return True


def remove_favorite_by_ids(db: Session, user_id: int, supplement_id: int) -> bool:
    """Remove a favorite by user_id and supplement_id"""
    db_favorite = db.query(models.Favorite).filter(
        and_(
            models.Favorite.user_id == user_id,
            models.Favorite.supplement_id == supplement_id
        )
    ).first()
    
    if not db_favorite:
        return False
    
    db.delete(db_favorite)
    db.commit()
    return True

