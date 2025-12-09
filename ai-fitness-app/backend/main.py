"""
main.py - FastAPI application entry point

This is the main FastAPI application that handles all API endpoints.
Run with: uvicorn main:app --reload --host 0.0.0.0 --port 8000
"""

from fastapi import FastAPI, Depends, HTTPException, status, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from typing import List, Optional
import os
import sys
from pathlib import Path

# Add current directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from database import engine, get_db, Base
import models
import schemas
import crud
from auth import (
    hash_password,
    verify_password,
    create_access_token,
    get_current_user,
    get_current_admin_user,
    ACCESS_TOKEN_EXPIRE_MINUTES
)
from datetime import timedelta

# Create database tables
Base.metadata.create_all(bind=engine)

# Create FastAPI app
app = FastAPI(
    title="AI Fitness App API",
    description="Backend API for AI Fitness App",
    version="1.0.0"
)

# CORS middleware - allow all origins for development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify allowed origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Root endpoint
@app.get("/")
def root():
    """Root endpoint"""
    return {"message": "AI Fitness App API", "version": "1.0.0"}


# Test endpoint
@app.get("/test")
def test():
    """Test endpoint to check if API is running"""
    return {"message": "API is working!"}


# Authentication endpoints
@app.post("/signup", response_model=schemas.UserResponse)
def signup(user_data: schemas.UserCreate, db: Session = Depends(get_db)):
    """Create a new user account"""
    try:
        # Check if user already exists
        existing_user = crud.get_user_by_name(db, user_data.first_name)
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"User with name '{user_data.first_name}' already exists"
            )
        
        # Create user
        user = crud.create_user(db, user_data)
        
        # Return user data (without password hash)
        return schemas.UserResponse(
            user_id=user.id,
            first_name=user.first_name,
            age=user.age,
            height_cm=user.height_cm,
            weight_kg=user.weight_kg,
            goal=user.goal,
            sex=user.sex,
            role=user.role,
            active=user.active,
            bmi=user.bmi,
            bmr=user.bmr,
            water_intake_l=user.water_intake_l,
            created_at=user.created_at
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error creating user: {str(e)}"
        )


@app.post("/login", response_model=schemas.LoginResponse)
def login(form_data: schemas.LoginRequest, db: Session = Depends(get_db)):
    """Login and get access token"""
    # Get user by first_name
    user = crud.get_user_by_name(db, form_data.first_name)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    if not verify_password(form_data.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    if not user.active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is inactive"
        )
    
    # Create access token
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.first_name},
        expires_delta=access_token_expires
    )
    
    return schemas.LoginResponse(
        access_token=access_token,
        token_type="bearer",
        first_name=user.first_name,
        user_id=user.id,
        role=user.role
    )


# User endpoints
@app.get("/user/{user_id}", response_model=schemas.UserResponse)
def get_user(user_id: int, current_user: models.User = Depends(get_current_user), db: Session = Depends(get_db)):
    """Get user by ID (requires authentication)"""
    user = crud.get_user_by_id(db, user_id)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # Users can only view their own profile unless they're admin
    if current_user.role != "admin" and current_user.id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    
    return schemas.UserResponse(
        user_id=user.id,
        first_name=user.first_name,
        age=user.age,
        height_cm=user.height_cm,
        weight_kg=user.weight_kg,
        goal=user.goal,
        sex=user.sex,
        role=user.role,
        active=user.active,
        bmi=user.bmi,
        bmr=user.bmr,
        water_intake_l=user.water_intake_l,
        created_at=user.created_at
    )


@app.put("/user/{user_id}", response_model=schemas.UserResponse)
def update_user(
    user_id: int,
    user_update: schemas.UserUpdate,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update user profile (requires authentication)"""
    # Users can only update their own profile unless they're admin
    if current_user.role != "admin" and current_user.id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    
    user = crud.update_user(db, user_id, user_update)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    return schemas.UserResponse(
        user_id=user.id,
        first_name=user.first_name,
        age=user.age,
        height_cm=user.height_cm,
        weight_kg=user.weight_kg,
        goal=user.goal,
        sex=user.sex,
        role=user.role,
        active=user.active,
        bmi=user.bmi,
        bmr=user.bmr,
        water_intake_l=user.water_intake_l,
        created_at=user.created_at
    )


# Supplement endpoints
@app.get("/supplements", response_model=List[schemas.SupplementResponse])
def get_supplements(db: Session = Depends(get_db)):
    """Get all supplements (public endpoint)"""
    supplements = crud.get_all_supplements(db)
    return supplements


@app.get("/supplements/{supplement_id}", response_model=schemas.SupplementResponse)
def get_supplement(supplement_id: int, db: Session = Depends(get_db)):
    """Get supplement by ID (public endpoint)"""
    supplement = crud.get_supplement_by_id(db, supplement_id)
    
    if not supplement:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Supplement not found"
        )
    
    return supplement


@app.post("/supplements", response_model=schemas.SupplementResponse)
def create_supplement(
    supplement_data: schemas.SupplementCreate,
    image_file: Optional[UploadFile] = File(None),
    current_user: models.User = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """Create a new supplement (admin only)"""
    image_url = None
    
    # Handle image upload if provided
    if image_file:
        # In production, upload to cloud storage
        # For now, just store the filename
        image_url = image_file.filename
    
    supplement = crud.add_supplement(db, supplement_data, image_url)
    return supplement


@app.put("/supplements/{supplement_id}", response_model=schemas.SupplementResponse)
def update_supplement(
    supplement_id: int,
    supplement_update: schemas.SupplementUpdate,
    current_user: models.User = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """Update supplement (admin only)"""
    supplement = crud.update_supplement(db, supplement_id, supplement_update)
    
    if not supplement:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Supplement not found"
        )
    
    return supplement


@app.delete("/supplements/{supplement_id}")
def delete_supplement(
    supplement_id: int,
    current_user: models.User = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """Delete supplement (admin only)"""
    success = crud.delete_supplement(db, supplement_id)
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Supplement not found"
        )
    
    return {"message": "Supplement deleted successfully"}


# Favorite endpoints
@app.get("/favorites/{user_id}", response_model=List[schemas.FavoriteResponse])
def get_favorites(user_id: int, db: Session = Depends(get_db)):
    """Get all favorites for a user"""
    favorites = crud.get_user_favorites(db, user_id)
    
    # Filter out None values and return valid favorites
    valid_favorites = []
    for fav in favorites:
        if fav and fav.supplement:  # Make sure supplement exists
            valid_favorites.append(fav)
    
    return valid_favorites


@app.post("/favorites/{user_id}/{supplement_id}", response_model=schemas.FavoriteResponse)
def add_favorite(
    user_id: int,
    supplement_id: int,
    db: Session = Depends(get_db)
):
    """Add a supplement to user's favorites"""
    # Verify user exists
    user = crud.get_user_by_id(db, user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # Verify supplement exists
    supplement = crud.get_supplement_by_id(db, supplement_id)
    if not supplement:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Supplement not found"
        )
    
    favorite = crud.add_favorite(db, user_id, supplement_id)
    return favorite


@app.delete("/favorites/{favorite_id}")
def remove_favorite(favorite_id: int, db: Session = Depends(get_db)):
    """Remove a favorite by ID"""
    success = crud.remove_favorite(db, favorite_id)
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Favorite not found"
        )
    
    return {"message": "Favorite removed successfully"}


# Admin endpoints
@app.get("/admin/users", response_model=List[schemas.UserResponse])
def get_all_users_admin(
    current_user: models.User = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """Get all users (admin only)"""
    users = crud.get_all_users(db)
    return [
        schemas.UserResponse(
            user_id=user.id,
            first_name=user.first_name,
            age=user.age,
            height_cm=user.height_cm,
            weight_kg=user.weight_kg,
            goal=user.goal,
            sex=user.sex,
            role=user.role,
            active=user.active,
            bmi=user.bmi,
            bmr=user.bmr,
            water_intake_l=user.water_intake_l,
            created_at=user.created_at
        )
        for user in users
    ]


@app.put("/admin/users/{user_id}/toggle")
def toggle_user_status(
    user_id: int,
    status_update: schemas.UserStatusUpdate,
    current_user: models.User = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """Toggle user active status (admin only)"""
    user = crud.toggle_user_active(db, user_id, status_update.active)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    return {"message": f"User {'activated' if user.active else 'deactivated'} successfully"}


# Workout endpoints (placeholder - implement later if needed)
@app.get("/workouts/{user_id}")
def get_workouts(user_id: int, db: Session = Depends(get_db)):
    """Get workouts for a user (placeholder)"""
    # This is a placeholder endpoint for future workout tracking feature
    return []


# Meal Plan endpoints
@app.post("/meal-plan/generate", response_model=schemas.MealPlanData)
def generate_meal_plan(
    request: schemas.MealPlanGenerateRequest,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Generate a 7-day meal plan based on user preferences and targets"""
    # Verify user is requesting their own plan (unless admin)
    if current_user.role != "admin" and current_user.id != request.userId:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    
    # Import meal plan generation logic
    from meal_plan_generator import generate_meal_plan
    
    try:
        meal_plan = generate_meal_plan(request.preferences, request.targets, request.duration)
        return meal_plan
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error generating meal plan: {str(e)}"
        )


@app.post("/meal-plan/regenerate-day", response_model=schemas.DayPlan)
def regenerate_day(
    request: schemas.MealPlanRegenerateDayRequest,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Regenerate a specific day of the meal plan"""
    # Verify user is requesting their own plan (unless admin)
    if current_user.role != "admin" and current_user.id != request.userId:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    
    # Import meal plan generation logic
    from meal_plan_generator import generate_single_day
    
    try:
        day_plan = generate_single_day(
            request.dayNumber,
            request.preferences,
            request.targets
        )
        return day_plan
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error regenerating day: {str(e)}"
        )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
