from fastapi import FastAPI, Depends, HTTPException, UploadFile, File, Form, status
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime
import os
from meal_plan_router import router as meal_plan_router

# ✅ Load .env early (IMPORTANT)
from dotenv import load_dotenv
load_dotenv()

from database import SessionLocal
import crud, schemas
from auth import verify_password, create_access_token
from utils import save_uploaded_file, delete_uploaded_file

# ✅ Routers
from meal_plan_router import router as meal_plan_router

# ✅ AI workout service (if you have it)
# If you don't have ai_workout_service.py, either create it or comment the endpoint below.
import ai_workout_service


# ---------- INIT ----------
app = FastAPI(title="AI Fitness Backend ✅")

# ---------- CORS ----------
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # change later for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---------- STATIC FILES (Serve uploaded images) ----------
UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)
app.mount("/uploads", StaticFiles(directory=UPLOAD_DIR), name="uploads")


# ---------- DB ----------
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# ---------- ROOT ----------
@app.get("/")
def root():
    return {"message": "AI Fitness Backend is running ✅"}


# ---------- AUTH ----------
@app.post("/register", response_model=schemas.UserOut)
def register(data: schemas.UserCreate, db: Session = Depends(get_db)):
    user = crud.get_user_by_name(db, data.first_name)
    if user:
        raise HTTPException(status_code=400, detail="User already exists")
    new_user = crud.create_user(db, data)
    return new_user


@app.post("/login")
def login(data: schemas.UserLogin, db: Session = Depends(get_db)):
    """
    Login Rules:
    1) Must exist
    2) Password must match
    3) User account is active
    """
    user = crud.get_user_by_username_or_email(db, data.username_or_email)
    if not user or not verify_password(data.password, user.password):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    if not user.active:
        raise HTTPException(
            status_code=403,
            detail="Your account has been deactivated. Please contact an administrator.",
        )

    user.last_login = datetime.now()
    db.commit()

    token = create_access_token({"sub": user.first_name})
    return {"access_token": token, "token_type": "bearer", "user": schemas.UserOut.model_validate(user)}


# ---------- ADMIN: USERS ----------
@app.get("/admin/users", response_model=list[schemas.AdminUserOut])
def admin_get_users(db: Session = Depends(get_db)):
    return crud.admin_get_all_users(db)


@app.put("/admin/users/{user_id}/status", response_model=schemas.AdminUserOut)
def admin_update_user_status(
    user_id: int,
    data: schemas.UserStatusUpdate,
    db: Session = Depends(get_db),
):
    user = crud.admin_set_user_active(db, user_id, data.active)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


# ---------- USER PROFILE ----------
@app.get("/user/{user_id}", response_model=schemas.UserOut)
def get_user(user_id: int, db: Session = Depends(get_db)):
    user = crud.get_user_by_id(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # BMI and BMR are already calculated and stored in the user model
    return schemas.UserOut.model_validate(user)


@app.put("/user/{user_id}", response_model=schemas.UserOut)
def update_user(user_id: int, data: schemas.UserUpdate, db: Session = Depends(get_db)):
    user = crud.update_user(db, user_id, data)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # BMI and BMR are already calculated and stored in the user model
    return schemas.UserOut.model_validate(user)


# ---------- SUPPLEMENTS ----------
@app.get("/supplements", response_model=list[schemas.SupplementOut])
def get_supplements(db: Session = Depends(get_db)):
    return crud.get_all_supplements(db)


@app.post("/supplements", response_model=schemas.SupplementOut)
def create_supplement(
    db: Session = Depends(get_db),
    name: str = Form(...),
    description: str = Form(...),
    price: float = Form(...),
    image: UploadFile = File(None),
):
    image_url = None
    if image:
        image_url = save_uploaded_file(image, UPLOAD_DIR)

    sup_data = schemas.SupplementCreate(name=name, description=description, price=price)
    sup = crud.add_supplement(db, sup_data, image_filename=image_url)
    return sup


@app.put("/supplements/{sup_id}", response_model=schemas.SupplementOut)
def update_supplement(
    sup_id: int,
    db: Session = Depends(get_db),
    name: str = Form(None),
    description: str = Form(None),
    price: float = Form(None),
    image: UploadFile = File(None),
):
    sup = crud.get_supplement(db, sup_id)
    if not sup:
        raise HTTPException(status_code=404, detail="Supplement not found")

    image_url = sup.image_url
    if image:
        if image_url:
            delete_uploaded_file(image_url, UPLOAD_DIR)
        image_url = save_uploaded_file(image, UPLOAD_DIR)

    # Only pass fields that were actually provided (not None)
    sup_data = schemas.SupplementUpdate(
        name=name,
        description=description,
        price=price
    )
    updated = crud.update_supplement(db, sup_id, sup_data, image_filename=image_url if image else None)
    return updated


@app.delete("/supplements/{sup_id}")
def delete_supplement(sup_id: int, db: Session = Depends(get_db)):
    sup = crud.get_supplement(db, sup_id)
    if not sup:
        raise HTTPException(status_code=404, detail="Supplement not found")

    if sup.image_url:
        delete_uploaded_file(sup.image_url, UPLOAD_DIR)

    crud.delete_supplement(db, sup_id)
    return {"message": "Supplement deleted ✅"}


# ---------- FAVORITES ----------
@app.post("/favorites", response_model=schemas.FavoriteOut)
def add_favorite(data: schemas.FavoriteCreate, db: Session = Depends(get_db)):
    return crud.add_favorite(db, data.user_id, data.supplement_id)


@app.get("/favorites/user/{user_id}", response_model=list[schemas.FavoriteOut])
def get_user_favorites(user_id: int, db: Session = Depends(get_db)):
    return crud.get_favorites(db, user_id)


@app.delete("/favorites/{favorite_id}")
def delete_favorite(favorite_id: int, db: Session = Depends(get_db)):
    crud.remove_favorite(db, favorite_id)
    return {"message": "Favorite removed ✅"}


@app.get("/favorites/check/{user_id}/{sup_id}")
def check_favorite(user_id: int, sup_id: int, db: Session = Depends(get_db)):
    fav = crud.get_favorite_by_user_and_supplement(db, user_id, sup_id)
    return {"is_favorite": fav is not None, "favorite_id": fav.id if fav else None}


# ---------- REMINDERS ----------
@app.post("/reminders", response_model=schemas.ReminderOut)
def create_reminder(data: schemas.ReminderCreate, db: Session = Depends(get_db)):
    return crud.create_reminder(db, data)


@app.get("/reminders/user/{user_id}", response_model=list[schemas.ReminderOut])
def get_user_reminders(user_id: int, db: Session = Depends(get_db)):
    return crud.get_user_reminders(db, user_id)


@app.delete("/reminders/{reminder_id}")
def delete_reminder(reminder_id: int, db: Session = Depends(get_db)):
    crud.delete_reminder(db, reminder_id)
    return {"message": "Reminder deleted ✅"}


# ---------- WATER INTAKE ----------
@app.post("/water", response_model=schemas.WaterIntakeOut)
def add_water_intake(data: schemas.WaterIntakeCreate, db: Session = Depends(get_db)):
    return crud.add_water_intake(db, data)


@app.get("/water/user/{user_id}", response_model=list[schemas.WaterIntakeOut])
def get_water_intakes(user_id: int, db: Session = Depends(get_db)):
    return crud.get_water_intakes(db, user_id)


# ---------- PROGRESS ----------
@app.post("/progress", response_model=schemas.ProgressEntryOut)
def add_progress(data: schemas.ProgressEntryCreate, db: Session = Depends(get_db)):
    return crud.create_progress_entry(db, data)


@app.get("/progress/user/{user_id}", response_model=list[schemas.ProgressEntryOut])
def get_user_progress(user_id: int, db: Session = Depends(get_db)):
    return crud.get_progress_entries(db, user_id)


# ---------- WORKOUT LOGS ----------
@app.post("/workout-logs", response_model=schemas.WorkoutLogOut)
def add_workout_log(data: schemas.WorkoutLogCreate, db: Session = Depends(get_db)):
    return crud.create_workout_log(db, data)


@app.get("/workout-logs/user/{user_id}", response_model=list[schemas.WorkoutLogOut])
def get_user_workout_logs(user_id: int, db: Session = Depends(get_db)):
    return crud.get_workout_logs(db, user_id)


# ---------- NOTIFICATIONS ----------
@app.post("/notifications", response_model=schemas.NotificationOut)
def create_notification(data: schemas.NotificationCreate, db: Session = Depends(get_db)):
    return crud.create_notification(db, data)


@app.get("/notifications/user/{user_id}", response_model=list[schemas.NotificationOut])
def get_user_notifications(user_id: int, db: Session = Depends(get_db)):
    return crud.get_notifications(db, user_id)


@app.put("/notifications/{notif_id}")
def update_notification(
    notif_id: int,
    data: schemas.NotificationUpdate,
    db: Session = Depends(get_db),
):
    notif = crud.update_notification_status(db, notif_id, data.status)
    if not notif:
        raise HTTPException(status_code=404, detail="Notification not found")
    return {"message": "Notification updated ✅"}


# ---------- AI WORKOUT PLAN ----------
@app.post("/ai/workout-plan/monthly")
def generate_ai_workout_plan(
    payload: schemas.AIWorkoutPlanRequest,
    db: Session = Depends(get_db),
):
    """
    Generate 1 monthly AI workout plan for an existing user.
    Saves plan JSON in workout_plans table (service logic).
    """
    try:
        data = ai_workout_service.generate_monthly_workout_plan(db, payload)
        return data
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        print("AI workout plan error:", e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to generate AI workout plan",
        )



