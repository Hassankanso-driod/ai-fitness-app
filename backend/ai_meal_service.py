# ai_meal_service.py
import os
import json
from datetime import datetime
from typing import Dict, Any, Optional

from dotenv import load_dotenv
from openai import OpenAI
from sqlalchemy.orm import Session

import models
import schemas

load_dotenv()

_client: Optional[OpenAI] = None

def get_openai_client() -> OpenAI:
    """
    Lazy OpenAI client init.
    Avoids failing at import time in CI where OPENAI_API_KEY is not set.
    """
    global _client
    if _client is None:
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise RuntimeError("OPENAI_API_KEY is not set")
        _client = OpenAI(api_key=api_key)
    return _client

PROMPT_VERSION = "v2.0-mealplan-options-json"


def _normalize_csv(value: Optional[str]) -> str:
    if not value:
        return ""
    return ", ".join([x.strip() for x in value.split(",") if x.strip()])


def generate_and_save_weekly_meal_plan(db: Session, payload: schemas.AIMealPlanRequest) -> Dict[str, Any]:
    """
    - Uses GPT to generate a 7-day meal plan in the EXACT structure used by MealPlanningScreen.tsx
    - Saves the FULL response JSON into mealplans.plan_json
    - Marks older mealplans for this user as inactive
    - Returns the JSON (same as saved)
    """
    user = db.query(models.User).filter(models.User.id == payload.user_id).first()
    if not user:
        raise ValueError("User not found")

    prefs = payload.preferences or schemas.MealPlanPreferences()
    flags = payload.flags or {}
    language = (payload.language or "en").lower()

    model_name = payload.model or "gpt-4.1"

    liked = _normalize_csv(prefs.liked_foods)
    disliked = _normalize_csv(prefs.disliked_foods)
    allergies = (prefs.allergies or "").strip()
    diet_style = (prefs.diet_style or "").strip()
    cuisine = (prefs.cuisine or "").strip()

    meals_per_day = int(prefs.meals_per_day or 4)
    cooking_time = (prefs.cooking_time or "quick").strip().lower()     # quick | medium | advanced
    budget_level = (prefs.budget_level or "medium").strip().lower()    # low | medium | high

    # if user set goal in prefs, prefer it; else use user.goal
    goal = (prefs.goal or user.goal or "").strip()

    if language == "ar":
        lang_rule = (
            "اكتب كل شيء باللغة العربية الفصحى (بدون عربليزي). "
            "اكتب أسماء الوجبات والشرح والنصائح باللغة العربية."
        )
        disclaimer = "هذه الخطة للاسترشاد العام وليست نصيحة طبية. استشر مختصاً إذا لديك حالة صحية."
        day_names = "Use Arabic day labels مثل: الاثنين، الثلاثاء..."
    else:
        lang_rule = "Write everything in clear simple English."
        disclaimer = "This plan is general guidance, not medical advice. Consult a professional if you have a condition."
        day_names = "Use English day labels: Monday...Sunday"

    # system: enforce EXACT JSON structure (matching MealPlanningScreen types)
    system_prompt = f"""
You are a professional sports nutrition coach for a fitness app.
Return VALID JSON ONLY. No markdown. No extra text.

You MUST return this exact JSON shape:

{{
  "meta": {{
    "language": "en|ar",
    "created_at": "ISO-8601 string",
    "model": "string",
    "prompt_version": "string",
    "disclaimer": "string"
  }},
  "daily_targets": {{
    "calories": number,
    "protein": number,
    "carbs": number,
    "fat": number,
    "water_liters": number
  }},
  "week": [
    {{
      "day": "string",
      "why_this_day_works": "string",
      "meals": {{
        "breakfast": [MealOption, MealOption],
        "lunch": [MealOption, MealOption],
        "dinner": [MealOption, MealOption],
        "snacks": [MealOption, MealOption]
      }},
      "totals": {{
        "calories": number,
        "protein_g": number,
        "carbs_g": number,
        "fat_g": number
      }},
      "tips": ["string", "string"]
    }}
  ],
  "grocery_list": {{
    "proteins": ["..."],
    "carbs": ["..."],
    "vegetables_fruits": ["..."],
    "dairy": ["..."],
    "fats": ["..."],
    "extras": ["..."]
  }},
  "meal_prep_plan": ["string", "string"]
}}

MealOption shape:
{{
  "title": "string",
  "ingredients": ["string", "..."],
  "portions": "string",
  "steps": ["string", "..."],
  "macros": {{
    "calories": number,
    "protein_g": number,
    "carbs_g": number,
    "fat_g": number
  }},
  "swaps": ["string", "..."]
}}

Hard Rules:
- week MUST have EXACTLY 7 days.
- For each day:
  - breakfast/lunch/dinner/snacks MUST each include 2 options (2 MealOption objects).
- Make meals realistic and available in normal groceries.
- Respect dislikes and allergies strictly (avoid them completely).
- Strongly prefer liked foods when possible.
- Diabetes true => prioritize low-GI carbs, avoid sugar drinks/desserts, spread carbs.
- Obesity true => calorie control, high protein, high fiber, portion control.
- cooking_time rule:
  - quick: steps should be short, total cook time <= 20 minutes.
  - medium: <= 35 minutes.
  - advanced: <= 60 minutes (still practical).
- budget_level rule:
  - low: prefer cheaper protein (eggs, tuna, chicken, legumes).
  - high: can include more salmon/steak etc.
- Water liters typically between 2.0 and 3.5 (adjust to body size and goal).
- {day_names}
- {lang_rule}
"""

    user_prompt = f"""
User Profile:
- id: {user.id}
- name: {user.first_name}
- sex: {user.sex}
- age: {user.age}
- height_cm: {user.height_cm}
- weight_kg: {user.weight_kg}
- goal: {goal}
- bmi: {user.bmi}
- bmr: {user.bmr}
- recommended_water_liters: {user.water_intake_l}

Health Flags:
- diabetes: {bool(flags.get("diabetes"))}
- obesity: {bool(flags.get("obesity"))}

Meal Plan Inputs (from app screen):
- language: {language}
- meals_per_day: {meals_per_day}
- cooking_time: {cooking_time}
- budget_level: {budget_level}
- diet_style: {diet_style or "none"}
- cuisine: {cuisine or "no preference"}
- allergies/intolerances: {allergies or "none"}
- liked_foods: {liked or "none"}
- disliked_foods: {disliked or "none"}

Generate the plan NOW.
Meta requirements:
- meta.language = "{language}"
- meta.created_at = current ISO-8601 time
- meta.model = "{model_name}"
- meta.prompt_version = "{PROMPT_VERSION}"
- meta.disclaimer = "{disclaimer}"
"""

    completion = client.chat.completions.create(
        model=model_name,
        response_format={"type": "json_object"},
        messages=[
            {"role": "system", "content": system_prompt.strip()},
            {"role": "user", "content": user_prompt.strip()},
        ],
        temperature=0.7,
    )

    raw = completion.choices[0].message.content
    data = json.loads(raw)

    # Ensure meta exists (in case model forgets)
    data.setdefault("meta", {})
    data["meta"].setdefault("language", language)
    data["meta"].setdefault("created_at", datetime.utcnow().isoformat() + "Z")
    data["meta"].setdefault("model", model_name)
    data["meta"].setdefault("prompt_version", PROMPT_VERSION)
    data["meta"].setdefault("disclaimer", disclaimer)

    # Save: mark old plans inactive, save new plan as active
    db.query(models.MealPlan).filter(models.MealPlan.user_id == user.id).update({"is_active": False})
    db.commit()

    daily = data.get("daily_targets", {}) or {}

    new_plan = models.MealPlan(
        user_id=user.id,
        goal=goal or user.goal,
        diet_style=diet_style or None,
        cuisine=cuisine or None,
        meals_per_day=meals_per_day,
        cooking_time=cooking_time,
        budget_level=budget_level,
        likes=liked or None,
        dislikes=disliked or None,
        allergies=allergies or None,
        medical_flags=json.dumps({"diabetes": bool(flags.get("diabetes")), "obesity": bool(flags.get("obesity"))}),
        language=language,
        plan_duration_days=7,
        calories=float(daily.get("calories", 0) or 0),
        protein=float(daily.get("protein", 0) or 0),
        carbs=float(daily.get("carbs", 0) or 0),
        fat=float(daily.get("fat", 0) or 0),
        water_liters=float(daily.get("water_liters", 0) or 0),
        plan_json=json.dumps(data, ensure_ascii=False),
        prompt_version=PROMPT_VERSION,
        model=model_name,
        is_active=True,
        version=1,
    )

    db.add(new_plan)
    db.commit()
    db.refresh(new_plan)

    return data


def get_latest_weekly_meal_plan(db: Session, user_id: int) -> Optional[Dict[str, Any]]:
    plan = (
        db.query(models.MealPlan)
        .filter(models.MealPlan.user_id == user_id, models.MealPlan.plan_json != None)
        .order_by(models.MealPlan.created_at.desc())
        .first()
    )
    if not plan or not plan.plan_json:
        return None
    return json.loads(plan.plan_json)
