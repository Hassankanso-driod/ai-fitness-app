"""
schemas.py - Pydantic schemas for request/response validation

Defines data structures for API requests and responses.
"""

from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime


# User Schemas
class UserBase(BaseModel):
    first_name: str
    age: int
    height_cm: float
    weight_kg: float
    goal: str  # gain, lose, maintain
    sex: str  # male, female


class UserCreate(UserBase):
    password: str
    role: str = "user"


class UserUpdate(BaseModel):
    age: Optional[int] = None
    height_cm: Optional[float] = None
    weight_kg: Optional[float] = None
    goal: Optional[str] = None
    sex: Optional[str] = None


class UserResponse(UserBase):
    user_id: int
    role: str
    active: bool
    bmi: Optional[float] = None
    bmr: Optional[float] = None
    water_intake_l: Optional[float] = None
    created_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


# Supplement Schemas
class SupplementBase(BaseModel):
    name: str
    description: Optional[str] = None
    price: float


class SupplementCreate(SupplementBase):
    pass


class SupplementUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    price: Optional[float] = None


class SupplementResponse(SupplementBase):
    id: int
    image_url: Optional[str] = None
    created_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


# Favorite Schemas
class FavoriteResponse(BaseModel):
    id: int
    user_id: int
    supplement_id: int
    supplement: Optional[SupplementResponse] = None
    created_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


# Authentication Schemas
class LoginRequest(BaseModel):
    first_name: str
    password: str


class LoginResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    first_name: str
    user_id: int
    role: str


# Admin Schemas
class UserStatusUpdate(BaseModel):
    active: bool


# Meal Plan Schemas
class MealPlanPreferences(BaseModel):
    mealsPerDay: int
    cookingTime: str
    dietStyle: str
    cuisine: str
    foodsLike: List[str] = []
    foodsDislike: List[str] = []
    allergies: List[str] = []
    budgetLevel: str = ""


class MealPlanTargets(BaseModel):
    calories: int
    protein: int
    carbs: int
    fat: int


class MealPlanGenerateRequest(BaseModel):
    userId: int
    preferences: MealPlanPreferences
    targets: MealPlanTargets
    duration: int = 7


class MealPlanRegenerateDayRequest(BaseModel):
    userId: int
    dayNumber: int
    preferences: MealPlanPreferences
    targets: MealPlanTargets


class Ingredient(BaseModel):
    name: str
    amount: str


class Meal(BaseModel):
    name: str
    mealType: str
    calories: int
    protein: int
    carbs: int
    fat: int
    ingredients: List[Ingredient]
    instructions: List[str]
    substitutions: Optional[List[str]] = []


class DayPlan(BaseModel):
    day: int
    targetCalories: int
    targetProtein: int
    targetCarbs: int
    targetFat: int
    actualCalories: int
    actualProtein: int
    actualCarbs: int
    actualFat: int
    meals: List[Meal]
    notes: Optional[str] = None


class ShoppingListItem(BaseModel):
    name: str
    amount: str


class ShoppingListCategory(BaseModel):
    category: str
    items: List[ShoppingListItem]


class MealPlanData(BaseModel):
    preferences: MealPlanPreferences
    days: List[DayPlan]
    shoppingList: List[ShoppingListCategory]
    generatedAt: str
