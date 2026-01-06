# meal_plan_router.py
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from database import SessionLocal
import schemas
import ai_meal_service

router = APIRouter(prefix="/ai/meal-plan", tags=["AI Meal Plan"])


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.post("/weekly", response_model=schemas.AIMealPlanResponse)
def generate_weekly_plan(payload: schemas.AIMealPlanRequest, db: Session = Depends(get_db)):
    """
    Generates + SAVES the plan in DB (mealplans table), returns the saved JSON.
    """
    try:
        data = ai_meal_service.generate_and_save_weekly_meal_plan(db, payload)
        return data
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        print("AI meal plan error:", e)
        raise HTTPException(status_code=500, detail="Failed to generate meal plan")


@router.get("/weekly/latest/{user_id}", response_model=schemas.AIMealPlanResponse)
def latest_weekly_plan(user_id: int, db: Session = Depends(get_db)):
    data = ai_meal_service.get_latest_weekly_meal_plan(db, user_id)
    if not data:
        raise HTTPException(status_code=404, detail="No meal plan found")
    return data
