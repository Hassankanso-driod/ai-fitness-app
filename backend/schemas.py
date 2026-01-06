# schemas.py (FINAL) - compatible with your main.py + crud.py
from __future__ import annotations

from datetime import datetime
from typing import Optional, List, Literal, Dict, Any

from pydantic import BaseModel, ConfigDict, Field


# -----------------------------
# Base for ORM models (Pydantic v2)
# -----------------------------
class ORMBase(BaseModel):
    model_config = ConfigDict(from_attributes=True)


# =============================
# AUTH / USERS
# =============================
class UserCreate(BaseModel):
    first_name: str
    password: str
    email: str

    sex: Optional[str] = None  # "male" / "female"
    age: int
    height_cm: float
    weight_kg: float
    goal: str

    role: Optional[str] = "user"


class UserLogin(BaseModel):
    username_or_email: str  # Can be either username (first_name) or email
    password: str


class LoginData(BaseModel):
    username_or_email: str  # Can be either username (first_name) or email
    password: str


class UserUpdate(BaseModel):
    first_name: Optional[str] = None
    sex: Optional[str] = None
    age: Optional[int] = None
    height_cm: Optional[float] = None
    weight_kg: Optional[float] = None
    goal: Optional[str] = None


class UserOut(ORMBase):
    id: int
    first_name: str
    email: Optional[str] = None
    email_verified: Optional[bool] = False

    sex: Optional[str] = None
    age: Optional[int] = None
    height_cm: Optional[float] = None
    weight_kg: Optional[float] = None
    goal: Optional[str] = None
    role: Optional[str] = None

    # stored/calculated fields in your create_user/update_user
    water_intake_l: Optional[float] = None
    bmi: Optional[float] = None
    bmr: Optional[float] = None

    # used in main.py login/admin logic
    active: Optional[bool] = True
    last_login: Optional[datetime] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


# =============================
# ADMIN
# =============================
class AdminUserOut(ORMBase):
    id: int
    first_name: str
    email: Optional[str] = None
    role: Optional[str] = None
    active: bool
    last_login: Optional[datetime] = None
    created_at: Optional[datetime] = None

    sex: Optional[str] = None
    age: Optional[int] = None
    height_cm: Optional[float] = None
    weight_kg: Optional[float] = None
    goal: Optional[str] = None


class UserStatusUpdate(BaseModel):
    active: bool


class EmailVerificationRequest(BaseModel):
    token: str


class ForgotPasswordRequest(BaseModel):
    email: str


class ResetPasswordRequest(BaseModel):
    token: str
    new_password: str


# =============================
# SUPPLEMENTS (crud expects these)
# =============================
class SupplementCreate(BaseModel):
    name: str
    description: str
    price: float


class SupplementUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    price: Optional[float] = None


class SupplementOut(ORMBase):
    id: int
    name: str
    description: str
    price: float
    image_url: Optional[str] = None  # Backward compatibility
    image_urls: Optional[str] = None  # JSON array of image filenames
    created_at: Optional[datetime] = None


# =============================
# FAVORITES
# =============================
class FavoriteCreate(BaseModel):
    user_id: int
    supplement_id: int


class FavoriteOut(ORMBase):
    id: int
    user_id: int
    supplement_id: int
    created_at: Optional[datetime] = None


# =============================
# REMINDERS
# =============================
class ReminderCreate(BaseModel):
    user_id: int
    type: str   # "water", "meal", "workout", "sleep"
    time: str   # "08:00"


class ReminderOut(ORMBase):
    id: int
    user_id: int
    type: str
    time: str
    created_at: Optional[datetime] = None


# =============================
# WATER INTAKE (main.py endpoints)
# =============================
class WaterIntakeCreate(BaseModel):
    user_id: int
    amount_ml: int


class WaterIntakeOut(ORMBase):
    id: int
    user_id: int
    amount_ml: int
    date: Optional[datetime] = None


# =============================
# WORKOUT LOGS (crud expects duration_minutes + notes)
# =============================
class WorkoutLogCreate(BaseModel):
    user_id: int
    exercise_name: str
    category: str
    sets: int
    reps: int
    weight_kg: Optional[float] = None
    duration_minutes: Optional[int] = None
    notes: Optional[str] = None


class WorkoutLogOut(ORMBase):
    id: int
    user_id: int
    exercise_name: str
    category: str
    sets: int
    reps: int
    weight_kg: Optional[float] = None
    duration_minutes: Optional[int] = None
    notes: Optional[str] = None
    created_at: Optional[datetime] = None


class WorkoutStatsOut(BaseModel):
    """Comprehensive workout statistics for analytics"""
    total_workouts: int
    total_exercises: int
    total_volume_kg: Optional[float] = None  # Total weight lifted (sets * reps * weight)
    total_duration_minutes: Optional[int] = None
    average_sets_per_workout: Optional[float] = None
    average_reps_per_set: Optional[float] = None
    most_trained_category: Optional[str] = None
    most_trained_exercise: Optional[str] = None
    personal_records: Dict[str, Any] = Field(default_factory=dict)  # PRs by exercise
    workouts_this_week: int
    workouts_this_month: int
    longest_streak_days: int
    last_workout_date: Optional[datetime] = None


# =============================
# PROGRESS ENTRIES (crud expects bmi/body_fat_percentage/muscle_mass_kg)
# =============================
class ProgressEntryCreate(BaseModel):
    user_id: int
    weight_kg: float
    bmi: Optional[float] = None
    body_fat_percentage: Optional[float] = None
    muscle_mass_kg: Optional[float] = None
    notes: Optional[str] = None


class ProgressEntryOut(ORMBase):
    id: int
    user_id: int
    weight_kg: float
    bmi: Optional[float] = None
    body_fat_percentage: Optional[float] = None
    muscle_mass_kg: Optional[float] = None
    notes: Optional[str] = None
    created_at: Optional[datetime] = None


# =============================
# MEAL PLANS (manual) - crud expects this
# (AI Meal Plan uses meal_plan_schema.py, separate)
# =============================
class MealPlanCreate(BaseModel):
    user_id: int
    goal: str
    calories: float
    protein: float
    carbs: float
    fat: float


class MealPlanOut(ORMBase):
    id: int
    user_id: int
    goal: str
    calories: float
    protein: float
    carbs: float
    fat: float
    created_at: Optional[datetime] = None


# =============================
# NOTIFICATIONS (main.py uses create + update)
# =============================
class NotificationCreate(BaseModel):
    user_id: int
    message: str
    status: Optional[str] = "pending"


class NotificationUpdate(BaseModel):
    status: str


class NotificationOut(ORMBase):
    id: int
    user_id: int
    message: str
    status: str
    created_at: Optional[datetime] = None


# =============================
# AI WORKOUT PLAN (your main.py uses schemas.AIWorkoutPlanRequest)
# Keep it simple and compatible with your service
# =============================
class WorkoutPreferences(BaseModel):
    experience: Optional[Literal["beginner", "intermediate", "advanced"]] = "beginner"
    days_per_week: Optional[int] = Field(default=4, ge=2, le=7)
    split: Optional[str] = "push_pull_legs"
    equipment: Optional[str] = "gym"
    focus: Optional[str] = "muscle_gain"
    injuries: Optional[str] = None
    language: Optional[Literal["en", "ar"]] = "en"

class AIWorkoutPlanRequest(BaseModel):
    user_id: int
    prefs: WorkoutPreferences


class WorkoutPlanOut(ORMBase):
    id: int
    user_id: int
    split: Optional[str] = None
    days_per_week: Optional[int] = None
    experience: Optional[str] = None
    goal_focus: Optional[str] = None
    language: Optional[str] = None
    plan_json: Optional[str] = None
    created_at: Optional[datetime] = None
# =============================
# AI MEAL PLAN (NEW - replaces meal_plan_schema.py)
# =============================
class MealPlanMacros(BaseModel):
    calories: float = 0
    protein_g: float = 0
    carbs_g: float = 0
    fat_g: float = 0


class MealPlanOption(BaseModel):
    title: str
    ingredients: List[str] = Field(default_factory=list)
    portions: str = ""
    steps: List[str] = Field(default_factory=list)
    macros: MealPlanMacros = Field(default_factory=MealPlanMacros)
    swaps: List[str] = Field(default_factory=list)


class MealPlanDayMeals(BaseModel):
    breakfast: List[MealPlanOption] = Field(default_factory=list)
    lunch: List[MealPlanOption] = Field(default_factory=list)
    dinner: List[MealPlanOption] = Field(default_factory=list)
    snacks: List[MealPlanOption] = Field(default_factory=list)


class MealPlanDay(BaseModel):
    day: str
    why_this_day_works: str = ""
    meals: MealPlanDayMeals = Field(default_factory=MealPlanDayMeals)
    totals: MealPlanMacros = Field(default_factory=MealPlanMacros)
    tips: List[str] = Field(default_factory=list)


class MealPlanMeta(BaseModel):
    language: Literal["en", "ar"] = "en"
    created_at: str = ""
    model: str = ""
    prompt_version: str = ""
    disclaimer: str = ""


class MealPlanDailyTargets(BaseModel):
    calories: float = 0
    protein: float = 0
    carbs: float = 0
    fat: float = 0
    water_liters: float = 2.5


class AIMealPlanResponse(BaseModel):
    meta: MealPlanMeta = Field(default_factory=MealPlanMeta)
    daily_targets: MealPlanDailyTargets = Field(default_factory=MealPlanDailyTargets)
    week: List[MealPlanDay] = Field(default_factory=list)
    grocery_list: Dict[str, List[str]] = Field(default_factory=dict)
    meal_prep_plan: List[str] = Field(default_factory=list)


class MealPlanPreferences(BaseModel):
    diet_style: Optional[str] = None
    allergies: Optional[str] = None
    cuisine: Optional[str] = None
    liked_foods: Optional[str] = None
    disliked_foods: Optional[str] = None

    budget_level: Optional[str] = "medium"      # "low" | "medium" | "high"
    cooking_time: Optional[str] = "quick"       # "quick" | "medium" | "advanced"
    meals_per_day: Optional[int] = 4            # your screen uses 4
    # (optional) allow user override goal later
    goal: Optional[str] = None


class AIMealPlanRequest(BaseModel):
    user_id: int
    flags: Dict[str, bool] = Field(default_factory=dict)  # diabetes/obesity
    language: Literal["en", "ar"] = "en"
    preferences: MealPlanPreferences = Field(default_factory=MealPlanPreferences)
    model: Optional[str] = None


class AIMealPlanDBOut(ORMBase):
    id: int
    user_id: int
    plan_json: str
    created_at: Optional[datetime] = None
