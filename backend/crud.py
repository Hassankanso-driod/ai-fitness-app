from sqlalchemy.orm import Session
import models, schemas
from auth import hash_password
from email_utils import generate_verification_token, send_verification_email, send_password_reset_email
from datetime import datetime, timedelta
import re


# ---------- USERS ----------
def get_user_by_name(db: Session, first_name: str):
    return db.query(models.User).filter(models.User.first_name == first_name).first()


def get_user_by_email(db: Session, email: str):
    return db.query(models.User).filter(models.User.email == email).first()


def get_user_by_username_or_email(db: Session, username_or_email: str):
    # In your app, "first_name" is used as username in login token subject.
    # Keep compatibility: allow login via email OR first_name.
    return (
        db.query(models.User)
        .filter(
            (models.User.first_name == username_or_email)
            | (models.User.email == username_or_email)
        )
        .first()
    )


def is_valid_email(email: str) -> bool:
    # simple but decent validation
    pattern = r"^[^@\s]+@[^@\s]+\.[^@\s]+$"
    return re.match(pattern, email or "") is not None


def create_user(db: Session, user: schemas.UserCreate):
    """
    Create a new user account
    Automatically calculates BMI, BMR, and water intake recommendations
    """
    # Calculate water intake recommendation
    water_intake = round(user.weight_kg * 0.033, 2) if user.weight_kg else 2.5

    # Calculate BMI if height and weight are provided
    bmi = None
    if user.height_cm and user.weight_kg:
        height_m = user.height_cm / 100
        bmi = round(user.weight_kg / (height_m ** 2), 2)

    # Calculate BMR using Mifflin-St Jeor Equation
    bmr = None
    if user.weight_kg and user.height_cm and user.age:
        if user.sex == "male":
            bmr = round(10 * user.weight_kg + 6.25 * user.height_cm - 5 * user.age + 5, 2)
        else:
            bmr = round(10 * user.weight_kg + 6.25 * user.height_cm - 5 * user.age - 161, 2)

    # Email validation (if provided)
    if user.email and not is_valid_email(user.email):
        raise ValueError("Invalid email format")

    hashed_password = hash_password(user.password)

    db_user = models.User(
        first_name=user.first_name,
        sex=user.sex,
        age=user.age,
        height_cm=user.height_cm,
        weight_kg=user.weight_kg,
        goal=user.goal,
        password=hashed_password,
        bmi=bmi,
        bmr=bmr,
        water_intake_l=water_intake,
        role=user.role or "user",
        email=user.email,
        active=True,
        email_verified=False,
    )

    # If user provided email, create verification token and send email
    if user.email:
        token = generate_verification_token()
        db_user.email_verification_token = token

    db.add(db_user)
    db.commit()
    db.refresh(db_user)

    if user.email:
        try:
            send_verification_email(user.email, token)
        except Exception as e:
            print("Email send error:", e)

    return db_user


# ---------- SUPPLEMENTS ----------
def add_supplement(
    db: Session,
    sup: schemas.SupplementCreate,
    image_filenames: list[str] | None = None,
    # Backward-compat: main.py used to pass image_filename="file.jpg"
    image_filename: str | None = None,
):
    """Create a new supplement.

    - `image_filenames`: optional list of image filenames (preferred)
    - `image_filename`: optional single filename (backward compatibility)
    """
    import json

    # Normalize: allow passing a single filename
    if image_filenames is None and image_filename:
        image_filenames = [image_filename]

    image_urls_json = None
    image_url = None  # backward compatibility (first image)

    if image_filenames:
        image_urls_json = json.dumps(image_filenames)
        image_url = image_filenames[0]

    db_sup = models.Supplement(
        name=sup.name,
        description=sup.description,
        price=sup.price,
        image_url=image_url,
        image_urls=image_urls_json,
    )
    db.add(db_sup)
    db.commit()
    db.refresh(db_sup)
    return db_sup


def get_all_supplements(db: Session):
    return db.query(models.Supplement).order_by(models.Supplement.id.desc()).all()


def get_supplement(db: Session, sup_id: int):
    return db.query(models.Supplement).filter(models.Supplement.id == sup_id).first()


def update_supplement(
    db: Session,
    sup_id: int,
    data: schemas.SupplementUpdate,
    image_filenames: list[str] | None = None,
    # Backward-compat: main.py used to pass image_filename="file.jpg" when image changed
    image_filename: str | None = None,
):
    import json

    # Normalize: allow passing a single filename
    if image_filenames is None and image_filename is not None:
        image_filenames = [image_filename] if image_filename else []

    sup = get_supplement(db, sup_id)
    if not sup:
        return None

    # update fields only if provided
    if data.name is not None:
        sup.name = data.name
    if data.description is not None:
        sup.description = data.description
    if data.price is not None:
        sup.price = data.price

    # update images only if a new image was actually passed
    if image_filenames is not None:
        sup.image_urls = json.dumps(image_filenames) if image_filenames else None
        sup.image_url = image_filenames[0] if image_filenames else None

    db.commit()
    db.refresh(sup)
    return sup


def delete_supplement(db: Session, sup_id: int):
    sup = get_supplement(db, sup_id)
    if not sup:
        return False
    db.delete(sup)
    db.commit()
    return True


# ---------- FAVORITES ----------
def add_favorite(db: Session, user_id: int, sup_id: int):
    fav = models.Favorite(user_id=user_id, supplement_id=sup_id)
    db.add(fav)
    db.commit()
    db.refresh(fav)
    return fav


def get_favorites(db: Session, user_id: int):
    return db.query(models.Favorite).filter(models.Favorite.user_id == user_id).all()


def remove_favorite(db: Session, favorite_id: int):
    fav = db.query(models.Favorite).filter(models.Favorite.id == favorite_id).first()
    if fav:
        db.delete(fav)
        db.commit()
    return True


def get_favorite_by_user_and_supplement(db: Session, user_id: int, sup_id: int):
    return (
        db.query(models.Favorite)
        .filter(models.Favorite.user_id == user_id, models.Favorite.supplement_id == sup_id)
        .first()
    )


# ---------- USER UPDATE / PROFILE ----------
def update_user(db: Session, user_id: int, data: schemas.UserUpdate):
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if not user:
        return None

    if data.first_name is not None:
        user.first_name = data.first_name
    if data.sex is not None:
        user.sex = data.sex
    if data.age is not None:
        user.age = data.age
    if data.height_cm is not None:
        user.height_cm = data.height_cm
    if data.weight_kg is not None:
        user.weight_kg = data.weight_kg
    if data.goal is not None:
        user.goal = data.goal

    # Recompute BMI/BMR/water if enough data present
    if user.height_cm and user.weight_kg:
        height_m = user.height_cm / 100
        user.bmi = round(user.weight_kg / (height_m ** 2), 2)
        user.water_intake_l = round(user.weight_kg * 0.033, 2)

    if user.weight_kg and user.height_cm and user.age:
        if (user.sex or "").lower() == "male":
            user.bmr = round(10 * user.weight_kg + 6.25 * user.height_cm - 5 * user.age + 5, 2)
        else:
            user.bmr = round(10 * user.weight_kg + 6.25 * user.height_cm - 5 * user.age - 161, 2)

    db.commit()
    db.refresh(user)
    return user


def get_user_by_id(db: Session, user_id: int):
    return db.query(models.User).filter(models.User.id == user_id).first()


# ---------- ADMIN USERS ----------
def admin_get_all_users(db: Session):
    return db.query(models.User).order_by(models.User.id.desc()).all()


def admin_set_user_active(db: Session, user_id: int, active: bool):
    user = get_user_by_id(db, user_id)
    if not user:
        return None
    user.active = bool(active)
    db.commit()
    db.refresh(user)
    return user


# ---------- EMAIL VERIFICATION / RESET ----------
def verify_email_token(db: Session, token: str):
    user = db.query(models.User).filter(models.User.email_verification_token == token).first()
    if not user:
        return None
    user.email_verified = True
    user.email_verification_token = None
    db.commit()
    db.refresh(user)
    return user


def request_password_reset(db: Session, email: str):
    user = get_user_by_email(db, email)
    if not user:
        return None

    token = generate_verification_token()
    user.password_reset_token = token
    user.password_reset_expires = datetime.utcnow() + timedelta(hours=1)
    db.commit()
    db.refresh(user)

    try:
        send_password_reset_email(email, token)
    except Exception as e:
        print("Reset email error:", e)

    return True


def reset_password(db: Session, token: str, new_password: str):
    user = db.query(models.User).filter(models.User.password_reset_token == token).first()
    if not user:
        return None
    if not user.password_reset_expires or user.password_reset_expires < datetime.utcnow():
        return None

    user.password = hash_password(new_password)
    user.password_reset_token = None
    user.password_reset_expires = None
    db.commit()
    db.refresh(user)
    return user


# ---------- MEAL PLANS ----------
def create_meal_plan(db: Session, meal_plan: schemas.MealPlanCreate):
    db_plan = models.MealPlan(**meal_plan.model_dump())
    db.add(db_plan)
    db.commit()
    db.refresh(db_plan)
    return db_plan


def get_meal_plans(db: Session, user_id: int):
    return db.query(models.MealPlan).filter(models.MealPlan.user_id == user_id).order_by(models.MealPlan.id.desc()).all()


def delete_meal_plan(db: Session, plan_id: int):
    plan = db.query(models.MealPlan).filter(models.MealPlan.id == plan_id).first()
    if not plan:
        return False
    db.delete(plan)
    db.commit()
    return True


# ---------- NOTIFICATIONS ----------
def get_notifications(db: Session, user_id: int):
    return db.query(models.Notification).filter(models.Notification.user_id == user_id).order_by(models.Notification.id.desc()).all()


def update_notification_status(db: Session, notif_id: int, status: str):
    notif = db.query(models.Notification).filter(models.Notification.id == notif_id).first()
    if not notif:
        return None
    notif.status = status
    db.commit()
    db.refresh(notif)
    return notif


def delete_notification(db: Session, notif_id: int):
    notif = db.query(models.Notification).filter(models.Notification.id == notif_id).first()
    if not notif:
        return False
    db.delete(notif)
    db.commit()
    return True


def create_notification(db: Session, notification: schemas.NotificationCreate):
    notif = models.Notification(**notification.model_dump())
    db.add(notif)
    db.commit()
    db.refresh(notif)
    return notif


# ---------- REMINDERS ----------
def create_reminder(db: Session, reminder: schemas.ReminderCreate):
    r = models.Reminder(**reminder.model_dump())
    db.add(r)
    db.commit()
    db.refresh(r)
    return r


def get_user_reminders(db: Session, user_id: int):
    return db.query(models.Reminder).filter(models.Reminder.user_id == user_id).order_by(models.Reminder.id.desc()).all()


def delete_reminder(db: Session, reminder_id: int):
    r = db.query(models.Reminder).filter(models.Reminder.id == reminder_id).first()
    if not r:
        return False
    db.delete(r)
    db.commit()
    return True


# ---------- WATER INTAKES ----------
def add_water_intake(db: Session, water: schemas.WaterIntakeCreate):
    w = models.WaterIntake(**water.model_dump())
    db.add(w)
    db.commit()
    db.refresh(w)
    return w


def get_water_intakes(db: Session, user_id: int):
    return db.query(models.WaterIntake).filter(models.WaterIntake.user_id == user_id).order_by(models.WaterIntake.id.desc()).all()


# ---------- WORKOUT LOGS ----------
def create_workout_log(db: Session, data: schemas.WorkoutLogCreate):
    log = models.WorkoutLog(**data.model_dump())
    db.add(log)
    db.commit()
    db.refresh(log)
    return log


def get_workout_logs(db: Session, user_id: int):
    return db.query(models.WorkoutLog).filter(models.WorkoutLog.user_id == user_id).order_by(models.WorkoutLog.id.desc()).all()


def delete_workout_log(db: Session, log_id: int):
    log = db.query(models.WorkoutLog).filter(models.WorkoutLog.id == log_id).first()
    if not log:
        return False
    db.delete(log)
    db.commit()
    return True


# ---------- PROGRESS ENTRIES ----------
def create_progress_entry(db: Session, data: schemas.ProgressEntryCreate):
    entry = models.ProgressEntry(**data.model_dump())
    db.add(entry)
    db.commit()
    db.refresh(entry)
    return entry


def get_progress_entries(db: Session, user_id: int):
    return (
        db.query(models.ProgressEntry)
        .filter(models.ProgressEntry.user_id == user_id)
        .order_by(models.ProgressEntry.id.desc())
        .all()
    )


def delete_progress_entry(db: Session, entry_id: int):
    entry = db.query(models.ProgressEntry).filter(models.ProgressEntry.id == entry_id).first()
    if not entry:
        return False
    db.delete(entry)
    db.commit()
    return True


# ---------- WORKOUT PLANS ----------
def get_workout_plans(db: Session, user_id: int):
    return db.query(models.WorkoutPlan).filter(models.WorkoutPlan.user_id == user_id).order_by(models.WorkoutPlan.id.desc()).all()


def get_workout_plan_by_id(db: Session, plan_id: int):
    return db.query(models.WorkoutPlan).filter(models.WorkoutPlan.id == plan_id).first()


# ---------- AI MEAL PLAN (DB STORE) ----------
def create_ai_meal_plan(db: Session, user_id: int, plan_json: str):
    plan = models.MealPlan(user_id=user_id, plan_json=plan_json)
    db.add(plan)
    db.commit()
    db.refresh(plan)
    return plan


def get_latest_ai_meal_plan(db: Session, user_id: int):
    return (
        db.query(models.MealPlan)
        .filter(models.MealPlan.user_id == user_id)
        .order_by(models.MealPlan.id.desc())
        .first()
    )
