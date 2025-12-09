from fastapi import FastAPI, Depends, HTTPException, UploadFile, File, Form, status
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from database import Base, engine, SessionLocal
import crud, models, schemas
from auth import verify_password, create_access_token
from fastapi.middleware.cors import CORSMiddleware
from utils import save_uploaded_file, delete_uploaded_file
from datetime import datetime
import os

import ai_meal_service      # ⬅️ خدمة AI meal plan
import ai_workout_service   # ⬅️ خدمة AI workout plan (جديدة)

# ---------- INIT ----------
# Don't create tables automatically - use existing MySQL database
# Base.metadata.create_all(bind=engine)
app = FastAPI(title="AI Fitness Backend ✅")

# ---------- CORS ----------
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---------- STATIC FILES (Serve uploaded images) ----------
# Create uploads directory if it doesn't exist
os.makedirs("uploads", exist_ok=True)
app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# ---------- TEST ----------
@app.get("/test")
def test_connection():
    return {"message": "Backend is reachable ✅"}


# ---------- AUTH ----------
@app.post("/signup", response_model=schemas.UserOut)
def signup(user: schemas.UserCreate, db: Session = Depends(get_db)):
    db_user = crud.get_user_by_name(db, user.first_name)
    if db_user:
        raise HTTPException(status_code=400, detail="User already exists")
    return crud.create_user(db, user)


@app.post("/login")
def login(data: schemas.UserLogin, db: Session = Depends(get_db)):
    """
    User login endpoint
    Checks:
    1. User exists
    2. Password is correct
    3. User account is active (not deactivated by admin)
    """
    user = crud.get_user_by_name(db, data.first_name)
    if not user or not verify_password(data.password, user.password):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    # Check if user account is active
    if not user.active:
        raise HTTPException(
            status_code=403,
            detail="Your account has been deactivated. Please contact an administrator.",
        )

    # Update last_login
    user.last_login = datetime.now()
    db.commit()

    token = create_access_token({"sub": user.first_name})
    return {
        "access_token": token,
        "token_type": "bearer",
        "user_id": user.id,
        "first_name": user.first_name,
        "role": user.role,
    }


# ---------- SUPPLEMENTS ----------
@app.post("/supplements", response_model=schemas.SupplementOut)
async def add_supplement(
    name: str = Form(...),
    description: str = Form(...),
    price: float = Form(...),
    image: UploadFile = File(None),
    db: Session = Depends(get_db),
):
    """
    Create a new supplement with optional image upload
    Uses multipart/form-data
    """
    # Save image if provided
    image_filename = None
    if image:
        image_filename = save_uploaded_file(image)

    # Create supplement data
    sup_data = schemas.SupplementCreate(name=name, description=description, price=price)

    return crud.add_supplement(db, sup_data, image_filename)


@app.get("/supplements", response_model=list[schemas.SupplementOut])
def list_supplements(db: Session = Depends(get_db)):
    """Get all supplements"""
    return crud.get_all_supplements(db)


@app.get("/supplements/{sup_id}", response_model=schemas.SupplementOut)
def get_supplement(sup_id: int, db: Session = Depends(get_db)):
    """Get a single supplement by ID"""
    sup = crud.get_supplement(db, sup_id)
    if not sup:
        raise HTTPException(status_code=404, detail="Supplement not found")
    return sup


@app.put("/supplements/{sup_id}", response_model=schemas.SupplementOut)
async def edit_supplement(
    sup_id: int,
    name: str = Form(None),
    description: str = Form(None),
    price: float = Form(None),
    image: UploadFile = File(None),
    db: Session = Depends(get_db),
):
    """
    Update supplement with optional new image
    Uses multipart/form-data
    """
    # Get existing supplement
    existing = crud.get_supplement(db, sup_id)
    if not existing:
        raise HTTPException(status_code=404, detail="Supplement not found")

    # Handle new image upload
    image_filename = None
    if image:
        # Delete old image if exists
        if existing.image_url:
            delete_uploaded_file(existing.image_url)
        # Save new image
        image_filename = save_uploaded_file(image)

    # Update data
    update_data = schemas.SupplementUpdate(
        name=name,
        description=description,
        price=price,
    )

    return crud.update_supplement(db, sup_id, update_data, image_filename)


@app.delete("/supplements/{sup_id}")
def delete_supplement(sup_id: int, db: Session = Depends(get_db)):
    """Delete supplement and its image file"""
    sup = crud.delete_supplement(db, sup_id)
    if not sup:
        raise HTTPException(status_code=404, detail="Supplement not found")

    # Delete image file if exists
    if sup.image_url:
        delete_uploaded_file(sup.image_url)

    return {"message": "Supplement deleted successfully ✅"}


# ---------- FAVORITES ----------
@app.post("/favorites/{user_id}/{sup_id}")
def add_fav(user_id: int, sup_id: int, db: Session = Depends(get_db)):
    """Add supplement to user's favorites"""
    # Check if already favorited
    existing = crud.get_favorite_by_user_and_supplement(db, user_id, sup_id)
    if existing:
        raise HTTPException(status_code=400, detail="Already in favorites")

    return crud.add_favorite(db, user_id, sup_id)


@app.get("/favorites/{user_id}")
def list_fav(user_id: int, db: Session = Depends(get_db)):
    """Get all favorites for a user - returns supplement IDs"""
    favorites = crud.get_favorites(db, user_id)
    # Return list of supplement IDs
    return [fav.supplement_id for fav in favorites]


@app.delete("/favorites/{user_id}/{sup_id}")
def remove_fav(user_id: int, sup_id: int, db: Session = Depends(get_db)):
    """Remove supplement from user's favorites"""
    fav = crud.get_favorite_by_user_and_supplement(db, user_id, sup_id)
    if not fav:
        raise HTTPException(status_code=404, detail="Favorite not found")

    crud.remove_favorite(db, fav.id)
    return {"message": "Removed from favorites successfully ✅"}


# ---------- ADMIN MANAGEMENT ----------
@app.get("/admin/users")
def get_all_users(db: Session = Depends(get_db)):
    """List all users for the admin panel"""
    return db.query(models.User).all()


@app.put("/admin/user/{user_id}/status")
def toggle_user_status(user_id: int, data: dict, db: Session = Depends(get_db)):
    """Activate or deactivate a user"""
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    user.active = data.get("active", True)
    db.commit()
    db.refresh(user)
    state = "activated" if user.active else "deactivated"
    return {"message": f"User {user.first_name} has been {state} ✅"}


# ---------- USER PROFILE ----------
@app.get("/user/{user_id}")
def get_user_profile(user_id: int, db: Session = Depends(get_db)):
    """Get user profile by ID"""
    user = crud.get_user_by_id(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


@app.put("/user/{user_id}", response_model=schemas.UserOut)
def update_user_profile(
    user_id: int,
    data: schemas.UserUpdate,
    db: Session = Depends(get_db),
):
    """Update user profile"""
    user = crud.update_user(db, user_id, data)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


# ---------- WORKOUT LOGS ----------
@app.post("/workouts", response_model=schemas.WorkoutLogOut)
def create_workout_log(
    workout: schemas.WorkoutLogCreate,
    db: Session = Depends(get_db),
):
    """Log a workout"""
    return crud.create_workout_log(db, workout)


@app.get("/workouts/{user_id}", response_model=list[schemas.WorkoutLogOut])
def get_user_workouts(user_id: int, db: Session = Depends(get_db)):
    """Get all workout logs for a user"""
    return crud.get_workout_logs(db, user_id)


@app.delete("/workouts/{log_id}")
def delete_workout_log(log_id: int, db: Session = Depends(get_db)):
    """Delete a workout log"""
    log = crud.delete_workout_log(db, log_id)
    if not log:
        raise HTTPException(status_code=404, detail="Workout log not found")
    return {"message": "Workout log deleted successfully"}


# ---------- PROGRESS TRACKING ----------
@app.post("/progress", response_model=schemas.ProgressEntryOut)
def create_progress_entry(
    progress: schemas.ProgressEntryCreate,
    db: Session = Depends(get_db),
):
    """Create a progress entry"""
    return crud.create_progress_entry(db, progress)


@app.get("/progress/{user_id}", response_model=list[schemas.ProgressEntryOut])
def get_user_progress(user_id: int, db: Session = Depends(get_db)):
    """Get all progress entries for a user"""
    return crud.get_progress_entries(db, user_id)


@app.delete("/progress/{entry_id}")
def delete_progress_entry(entry_id: int, db: Session = Depends(get_db)):
    """Delete a progress entry"""
    entry = crud.delete_progress_entry(db, entry_id)
    if not entry:
        raise HTTPException(status_code=404, detail="Progress entry not found")
    return {"message": "Progress entry deleted successfully"}


# ---------- MEAL PLANS (manual) ----------
@app.post("/meals", response_model=schemas.MealPlanOut)
def create_meal_plan(meal_plan: schemas.MealPlanCreate, db: Session = Depends(get_db)):
    """Create a meal plan"""
    return crud.create_meal_plan(db, meal_plan)


@app.get("/meals/{user_id}", response_model=list[schemas.MealPlanOut])
def get_user_meals(user_id: int, db: Session = Depends(get_db)):
    """Get all meal plans for a user"""
    return crud.get_meal_plans(db, user_id)


@app.delete("/meals/{plan_id}")
def delete_meal_plan(plan_id: int, db: Session = Depends(get_db)):
    """Delete a meal plan"""
    plan = crud.delete_meal_plan(db, plan_id)
    if not plan:
        raise HTTPException(status_code=404, detail="Meal plan not found")
    return {"message": "Meal plan deleted successfully"}


# ---------- NOTIFICATIONS ----------
@app.get("/notifications/user/{user_id}", response_model=list[schemas.NotificationOut])
def get_user_notifications(user_id: int, db: Session = Depends(get_db)):
    """Get all notifications for a user"""
    return crud.get_notifications(db, user_id)


@app.put("/notifications/{notif_id}")
def update_notification(
    notif_id: int,
    data: schemas.NotificationUpdate,
    db: Session = Depends(get_db),
):
    """Update notification status"""
    notif = crud.update_notification_status(db, notif_id, data.status)
    if not notif:
        raise HTTPException(status_code=404, detail="Notification not found")
    return {"message": "Notification updated successfully"}


@app.delete("/notifications/{notif_id}")
def delete_notification(notif_id: int, db: Session = Depends(get_db)):
    """Delete a notification"""
    notif = crud.delete_notification(db, notif_id)
    if not notif:
        raise HTTPException(status_code=404, detail="Notification not found")
    return {"message": "Notification deleted successfully"}


@app.get("/favorites/check/{user_id}/{sup_id}")
def check_favorite(user_id: int, sup_id: int, db: Session = Depends(get_db)):
    """Check if a supplement is favorited by user"""
    fav = crud.get_favorite_by_user_and_supplement(db, user_id, sup_id)
    return {"is_favorite": fav is not None, "favorite_id": fav.id if fav else None}


# ---------- AI MEAL PLAN (GPT-5.1-mini) ----------
@app.post("/ai/meal-plan/weekly", response_model=schemas.AIMealPlanResponse)
def generate_ai_meal_plan(
    payload: schemas.AIMealPlanRequest,
    db: Session = Depends(get_db),
):
    """
    Generate 7-day AI meal plan using GPT-5.1-mini for an existing user.
    - Reads user from DB
    - Sends profile + flags + preferences + language to OpenAI
    - Saves summary in mealplans.plan_json
    - Returns structured JSON for frontend
    """
    try:
        data = ai_meal_service.generate_weekly_meal_plan(db, payload)
        return data
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except Exception as e:
        print("AI meal plan error:", e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to generate AI meal plan",
        )


# ---------- AI WORKOUT PLAN (GPT-4.1-mini) ----------
@app.post("/ai/workout-plan/monthly", response_model=schemas.AIWorkoutPlanResponse)
def generate_ai_workout_plan(
    payload: schemas.AIWorkoutPlanRequest,
    db: Session = Depends(get_db),
):
    """
    Generate 4-week (1 month) AI workout plan for an existing user.
    - Reads user from DB
    - Uses workout preferences (experience, days/week, split, equipment, focus, injuries, language)
    - Saves plan JSON in workout_plans table
    - Only allows one plan per user (see service logic)
    """
    try:
        data = ai_workout_service.generate_monthly_workout_plan(db, payload)
        return data
    except ValueError as e:
        # e.g. "You already generated a workout plan. Only one plan is allowed."
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        print("AI workout plan error:", e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to generate AI workout plan",
        )
