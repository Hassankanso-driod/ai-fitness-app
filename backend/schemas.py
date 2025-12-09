from pydantic import BaseModel
from typing import Optional, List, Literal, Dict, Any
from datetime import datetime

# ---------- USER ----------
class UserBase(BaseModel):
    first_name: str
    sex: Optional[str]
    age: Optional[int]
    height_cm: Optional[float]
    weight_kg: Optional[float]
    password: str
    goal: Optional[str]
    role: Optional[str] = "user"


class UserCreate(UserBase):
    pass


class UserLogin(BaseModel):
    first_name: str
    password: str


class UserOut(BaseModel):
    id: int
    first_name: str
    goal: Optional[str]
    role: Optional[str]
    water_intake_l: Optional[float]
    bmi: Optional[float] = None
    bmr: Optional[float] = None
    age: Optional[int] = None
    height_cm: Optional[float] = None
    weight_kg: Optional[float] = None
    sex: Optional[str] = None

    class Config:
        from_attributes = True  # replaces orm_mode in Pydantic v2


# ---------- SUPPLEMENTS ----------
class SupplementCreate(BaseModel):
    name: str
    description: str
    price: float


class SupplementUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    price: Optional[float] = None


class SupplementOut(BaseModel):
    id: int
    name: str
    description: str
    price: float
    image_url: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True


# ---------- FAVORITES ----------
class FavoriteOut(BaseModel):
    id: int
    user_id: int
    supplement_id: int

    class Config:
        from_attributes = True


# ---------- USER UPDATE ----------
class UserUpdate(BaseModel):
    first_name: Optional[str] = None
    age: Optional[int] = None
    height_cm: Optional[float] = None
    weight_kg: Optional[float] = None
    goal: Optional[str] = None
    # Email removed - not needed for profile updates


# ---------- WORKOUT LOGS ----------
class WorkoutLogBase(BaseModel):
    exercise_name: str
    category: str
    sets: int
    reps: int
    weight_kg: Optional[float] = None
    duration_minutes: Optional[int] = None
    notes: Optional[str] = None


class WorkoutLogCreate(WorkoutLogBase):
    user_id: int


class WorkoutLogOut(WorkoutLogBase):
    id: int
    user_id: int
    created_at: datetime

    class Config:
        from_attributes = True


# ---------- PROGRESS ENTRIES ----------
class ProgressEntryBase(BaseModel):
    weight_kg: float
    bmi: Optional[float] = None
    body_fat_percentage: Optional[float] = None
    muscle_mass_kg: Optional[float] = None
    notes: Optional[str] = None


class ProgressEntryCreate(ProgressEntryBase):
    user_id: int


class ProgressEntryOut(BaseModel):
    id: int
    user_id: int
    weight_kg: float
    bmi: Optional[float] = None
    body_fat_percentage: Optional[float] = None
    muscle_mass_kg: Optional[float] = None
    notes: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True


# ---------- MEAL PLANS (manual) ----------
class MealPlanBase(BaseModel):
    goal: str
    calories: float
    protein: float
    carbs: Optional[float] = None
    fat: Optional[float] = None


class MealPlanCreate(MealPlanBase):
    user_id: int


class MealPlanOut(MealPlanBase):
    id: int
    user_id: int
    created_at: datetime

    class Config:
        from_attributes = True


# ---------- NOTIFICATIONS ----------
class NotificationOut(BaseModel):
    id: int
    user_id: int
    message: str
    status: str
    created_at: datetime

    class Config:
        from_attributes = True


class NotificationUpdate(BaseModel):
    status: str


# ---------- AI MEAL PLAN (GPT-5.1-mini) ----------
class AIMealFlags(BaseModel):
    diabetes: bool = False
    obesity: bool = False


class AIMealPreferences(BaseModel):
    diet_style: Optional[str] = None  # e.g. "normal", "low_carb"
    allergies: Optional[str] = None
    cuisine: Optional[str] = None  # e.g. "mediterranean"

    # ماذا يحب/يكره أن يأكل
    liked_foods: Optional[str] = None  # مثال: "chicken, rice, manoushe, eggs"
    disliked_foods: Optional[str] = None  # مثال: "fish, liver, spicy food"


class AIMealPlanRequest(BaseModel):
    user_id: int
    flags: AIMealFlags = AIMealFlags()
    preferences: Optional[AIMealPreferences] = None

    # لغة الخطة
    # "en" → English, "ar" → Arabic
    language: str = "en"


class DailyTargets(BaseModel):
    calories: float
    protein: float
    carbs: float
    fat: float
    water_liters: float


class DayPlan(BaseModel):
    day: str
    breakfast: str
    lunch: str
    dinner: str
    snacks: str
    tips: List[str]
    macros: DailyTargets


class AIMealPlanResponse(BaseModel):
    daily_targets: DailyTargets
    week: List[DayPlan]


# ---------- AI WORKOUT PLAN (GPT-4.1-mini) ----------
class AIWorkoutPreferences(BaseModel):
    experience: Literal["beginner", "intermediate", "advanced"] = "beginner"
    days_per_week: int = 4  # 3–6
    split: Literal["full_body", "upper_lower", "push_pull_legs", "bro_split"] = "push_pull_legs"
    equipment: Literal["gym", "home", "both"] = "gym"
    focus: Literal[
        "strength",
        "muscle_gain",
        "fat_loss",
        "athletic",
        "general_fitness",
    ] = "muscle_gain"
    injuries: Optional[str] = None
    language: Literal["en", "ar"] = "en"  # لغة الخطة كاملة


class AIWorkoutPlanRequest(BaseModel):
    user_id: int
    prefs: AIWorkoutPreferences


class WorkoutExercise(BaseModel):
    name: str
    sets: str
    reps: str
    rest: str
    notes: Optional[str] = None


class WorkoutDay(BaseModel):
    label: str               # ex: "Day 1 – Push"
    focus: str               # ex: "Chest, shoulders, triceps"
    exercises: List[WorkoutExercise]
    notes: List[str] = []    # tips / reminders


class WorkoutWeek(BaseModel):
    week_number: int
    goal_focus: str
    days: List[WorkoutDay]


class AIWorkoutPlanResponse(BaseModel):
    meta: Dict[str, Any]
    weeks: List[WorkoutWeek]
