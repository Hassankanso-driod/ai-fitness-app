from sqlalchemy.orm import Session
import models, schemas
from auth import hash_password

# ---------- USERS ----------
def get_user_by_name(db: Session, first_name: str):
    return db.query(models.User).filter(models.User.first_name == first_name).first()

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
            bmr = round(10 * user.weight_kg + 6.25 * user.height_cm - 5 * user.age + 5, 0)
        elif user.sex == "female":
            bmr = round(10 * user.weight_kg + 6.25 * user.height_cm - 5 * user.age - 161, 0)
    
    db_user = models.User(
        first_name=user.first_name,
        sex=user.sex,
        age=user.age,
        height_cm=user.height_cm,
        weight_kg=user.weight_kg,
        password=hash_password(user.password),
        goal=user.goal,
        role=user.role,
        water_intake_l=water_intake,
        bmi=bmi,
        bmr=bmr,
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

# ---------- SUPPLEMENTS ----------
def add_supplement(db: Session, sup: schemas.SupplementCreate, image_filename: str = None):
    """Create a new supplement with optional image filename"""
    db_sup = models.Supplement(
        name=sup.name,
        description=sup.description,
        price=sup.price,
        image_url=image_filename,  # Store only filename
    )
    db.add(db_sup)
    db.commit()
    db.refresh(db_sup)
    return db_sup

def get_all_supplements(db: Session):
    """Get all supplements"""
    return db.query(models.Supplement).all()

def get_supplement(db: Session, sup_id: int):
    """Get a single supplement by ID"""
    return db.query(models.Supplement).filter(models.Supplement.id == sup_id).first()

def update_supplement(db: Session, sup_id: int, data: schemas.SupplementUpdate, image_filename: str = None):
    """Update supplement - image_filename is optional (only if new image uploaded)"""
    sup = db.query(models.Supplement).filter(models.Supplement.id == sup_id).first()
    if not sup:
        return None
    
    if data.name is not None:
        sup.name = data.name
    if data.description is not None:
        sup.description = data.description
    if data.price is not None:
        sup.price = data.price
    if image_filename is not None:
        sup.image_url = image_filename  # Update image only if new one provided
    
    db.commit()
    db.refresh(sup)
    return sup

def delete_supplement(db: Session, sup_id: int):
    """Delete supplement - returns the supplement object (so we can delete its image file)"""
    sup = db.query(models.Supplement).filter(models.Supplement.id == sup_id).first()
    if not sup:
        return None
    db.delete(sup)
    db.commit()
    return sup

# ---------- FAVORITES ----------
def add_favorite(db: Session, user_id: int, sup_id: int):
    fav = models.Favorite(user_id=user_id, supplement_id=sup_id)
    db.add(fav)
    db.commit()
    db.refresh(fav)
    return fav

def get_favorites(db: Session, user_id: int):
    return db.query(models.Favorite).filter(models.Favorite.user_id == user_id).all()

def remove_favorite(db: Session, fav_id: int):
    fav = db.query(models.Favorite).filter(models.Favorite.id == fav_id).first()
    if not fav:
        return None
    db.delete(fav)
    db.commit()
    return fav

def get_favorite_by_user_and_supplement(db: Session, user_id: int, sup_id: int):
    return db.query(models.Favorite).filter(
        models.Favorite.user_id == user_id,
        models.Favorite.supplement_id == sup_id
    ).first()


# ---------- USER UPDATE ----------
def update_user(db: Session, user_id: int, data: schemas.UserUpdate):
    """
    Update user profile information
    Automatically recalculates BMI and BMR when weight/height/age changes
    Updates updated_at timestamp automatically
    """
    from datetime import datetime
    
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if not user:
        return None
    
    # Update basic fields
    if data.first_name is not None:
        user.first_name = data.first_name
    if data.age is not None:
        user.age = data.age
    if data.height_cm is not None:
        user.height_cm = data.height_cm
    if data.weight_kg is not None:
        user.weight_kg = data.weight_kg
    if data.goal is not None:
        user.goal = data.goal
    
    # Recalculate BMI if weight or height changed
    if (data.weight_kg is not None or data.height_cm is not None) and user.weight_kg and user.height_cm:
        height_m = user.height_cm / 100
        user.bmi = round(user.weight_kg / (height_m ** 2), 2)
    
    # Recalculate BMR if weight, height, age, or sex changed
    if (data.weight_kg is not None or data.height_cm is not None or data.age is not None) and user.weight_kg and user.height_cm and user.age:
        # Mifflin-St Jeor Equation for BMR
        if user.sex == "male":
            user.bmr = round(10 * user.weight_kg + 6.25 * user.height_cm - 5 * user.age + 5, 0)
        else:  # female
            user.bmr = round(10 * user.weight_kg + 6.25 * user.height_cm - 5 * user.age - 161, 0)
    
    # Update water intake recommendation based on weight
    if data.weight_kg is not None and user.weight_kg:
        user.water_intake_l = round(user.weight_kg * 0.033, 2)
    
    # Update updated_at timestamp
    user.updated_at = datetime.now()
    
    db.commit()
    db.refresh(user)
    return user

def get_user_by_id(db: Session, user_id: int):
    return db.query(models.User).filter(models.User.id == user_id).first()


# ---------- WORKOUT LOGS ----------
def create_workout_log(db: Session, workout: schemas.WorkoutLogCreate):
    db_workout = models.WorkoutLog(
        user_id=workout.user_id,
        exercise_name=workout.exercise_name,
        category=workout.category,
        sets=workout.sets,
        reps=workout.reps,
        weight_kg=workout.weight_kg,
        duration_minutes=workout.duration_minutes,
        notes=workout.notes,
    )
    db.add(db_workout)
    db.commit()
    db.refresh(db_workout)
    return db_workout

def get_workout_logs(db: Session, user_id: int, skip: int = 0, limit: int = 100):
    return db.query(models.WorkoutLog).filter(
        models.WorkoutLog.user_id == user_id
    ).order_by(models.WorkoutLog.created_at.desc()).offset(skip).limit(limit).all()

def delete_workout_log(db: Session, log_id: int):
    log = db.query(models.WorkoutLog).filter(models.WorkoutLog.id == log_id).first()
    if not log:
        return None
    db.delete(log)
    db.commit()
    return log


# ---------- PROGRESS ENTRIES ----------
def create_progress_entry(db: Session, progress: schemas.ProgressEntryCreate):
    db_progress = models.ProgressEntry(
        user_id=progress.user_id,
        weight_kg=progress.weight_kg,
        bmi=progress.bmi,
        body_fat_percentage=progress.body_fat_percentage,
        muscle_mass_kg=progress.muscle_mass_kg,
        notes=progress.notes,
    )
    db.add(db_progress)
    db.commit()
    db.refresh(db_progress)
    return db_progress

def get_progress_entries(db: Session, user_id: int, skip: int = 0, limit: int = 100):
    return db.query(models.ProgressEntry).filter(
        models.ProgressEntry.user_id == user_id
    ).order_by(models.ProgressEntry.created_at.desc()).offset(skip).limit(limit).all()

def delete_progress_entry(db: Session, entry_id: int):
    entry = db.query(models.ProgressEntry).filter(models.ProgressEntry.id == entry_id).first()
    if not entry:
        return None
    db.delete(entry)
    db.commit()
    return entry


# ---------- MEAL PLANS (manual) ----------
def create_meal_plan(db: Session, meal_plan: schemas.MealPlanCreate):
    db_meal = models.MealPlan(
        user_id=meal_plan.user_id,
        goal=meal_plan.goal,
        calories=meal_plan.calories,
        protein=meal_plan.protein,
        carbs=meal_plan.carbs,
        fat=meal_plan.fat,
    )
    db.add(db_meal)
    db.commit()
    db.refresh(db_meal)
    return db_meal

def get_meal_plans(db: Session, user_id: int):
    return db.query(models.MealPlan).filter(
        models.MealPlan.user_id == user_id
    ).order_by(models.MealPlan.created_at.desc()).all()

def delete_meal_plan(db: Session, plan_id: int):
    plan = db.query(models.MealPlan).filter(models.MealPlan.id == plan_id).first()
    if not plan:
        return None
    db.delete(plan)
    db.commit()
    return plan


# ---------- NOTIFICATIONS ----------
def get_notifications(db: Session, user_id: int):
    return db.query(models.Notification).filter(
        models.Notification.user_id == user_id
    ).order_by(models.Notification.created_at.desc()).all()

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
        return None
    db.delete(notif)
    db.commit()
    return notif
