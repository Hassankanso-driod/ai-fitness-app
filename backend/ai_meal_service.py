# ai_meal_service.py
import os
import json
from typing import Dict, Any, Optional

from sqlalchemy.orm import Session
from dotenv import load_dotenv
from openai import OpenAI

import models
import schemas

# تحميل .env (حتى نقرأ OPENAI_API_KEY بسهولة)
load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


def generate_weekly_meal_plan(
    db: Session,
    payload: schemas.AIMealPlanRequest
) -> Dict[str, Any]:
    """
    Uses GPT-4.1-mini to generate a 7-day meal plan
    based on an existing user in the DB.
    - Reads user from users table
    - Sends profile + flags + preferences to OpenAI
    - Stores summary in mealplans table (plan_json)
    - Returns JSON ready for AIMealPlanResponse
    """
    # 1) Get user
    user = db.query(models.User).filter(models.User.id == payload.user_id).first()
    if not user:
        raise ValueError("User not found")

    flags = payload.flags
    prefs = payload.preferences
    language = (payload.language or "en").lower()

    # 2) Language instruction
    if language == "ar":
        language_instruction = (
            "All meal names, descriptions, tips, focus and overview MUST be written in MODERN STANDARD ARABIC. "
            "Do NOT use Arabic written with Latin letters. Use clear Arabic sentences."
        )
    else:
        language_instruction = (
            "All meal names, descriptions, tips, focus and overview MUST be written in CLEAR, SIMPLE ENGLISH."
        )

    # 3) System prompt: define JSON format
    system_prompt = f"""
You are a professional sports nutrition coach for a fitness app.
You MUST respond with valid JSON only, no extra text.

JSON format:
{{
  "daily_targets": {{
    "calories": number,
    "protein": number,
    "carbs": number,
    "fat": number,
    "water_liters": number
  }},
  "week": [
    {{
      "day": "Monday",
      "focus": "string, short description of the main focus of the day (e.g. 'High protein, moderate carbs for muscle gain')",
      "overview": "string, 1–2 sentences summarizing the logic of the whole day",
      "breakfast": "string",
      "lunch": "string",
      "dinner": "string",
      "snacks": "string",
      "tips": ["string", "..."],
      "special_considerations": [
        "string, explain how this day respects diabetes/obesity/allergies/preferences if relevant",
        "string, more notes if needed"
      ],
      "macros": {{
        "calories": number,
        "protein": number,
        "carbs": number,
        "fat": number,
        "water_liters": number
      }}
    }},
    ...
  ]
}}

Rules:
- Exactly 7 days in "week".
- Use simple, realistic foods that are easy to find.
- Adjust calories/macros based on goal (bulk/cut/maintain) and basic activity.
- If diabetes is true -> prioritize low-GI carbs, avoid sugary drinks/desserts, and spread carbs through the day.
- If obesity is true -> prioritize calorie control, high protein, high fiber, and portion control.
- Water_liters should usually be between ~2.0 and 3.5 for a healthy adult, unless slightly adjusted by goal/activity.
- Strongly prefer foods from "liked foods" and completely avoid foods from "disliked foods".
- For each day, 'special_considerations' MUST highlight how the plan respects diabetes/obesity/allergies/preferences when relevant.
- {language_instruction}
"""

    liked_foods = getattr(prefs, "liked_foods", None) if prefs else None
    disliked_foods = getattr(prefs, "disliked_foods", None) if prefs else None

    # 4) User prompt with actual data
    user_prompt = f"""
User profile:
- ID: {user.id}
- Name: {user.first_name}
- Age: {user.age}
- Sex: {user.sex}
- Height: {user.height_cm} cm
- Weight: {user.weight_kg} kg
- Goal: {user.goal}
- BMI: {user.bmi}
- BMR: {user.bmr}
- Recommended water intake (L): {user.water_intake_l}

Flags:
- Diabetes: {flags.diabetes}
- Obesity: {flags.obesity}

Preferences:
- Diet style: {getattr(prefs, 'diet_style', None) if prefs else None}
- Allergies: {getattr(prefs, 'allergies', None) if prefs else None}
- Cuisine: {getattr(prefs, 'cuisine', None) if prefs else None}
- Liked foods: {liked_foods}
- Disliked foods: {disliked_foods}

Plan language: {"Arabic" if language == "ar" else "English"}.

Generate a 7-day meal plan in the EXACT JSON format specified in the system message.
Do not include any explanation outside the JSON.
"""

    completion = client.chat.completions.create(
        model="gpt-4.1-mini",  # ✅ cheap model
        response_format={"type": "json_object"},
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        temperature=0.7,
    )

    content = completion.choices[0].message.content
    data = json.loads(content)  # dict

    # 5) Save plan as MealPlan summary + JSON in DB
    try:
        week = data.get("week", [])
        if week:
            # Take macros from first day as a simple summary
            m = week[0].get("macros", {})
            new_plan = models.MealPlan(
                user_id=user.id,
                goal=user.goal,
                calories=m.get("calories"),
                protein=m.get("protein"),
                carbs=m.get("carbs"),
                fat=m.get("fat"),
                plan_json=json.dumps(data),
            )
            db.add(new_plan)
            db.commit()
    except Exception as e:
        print("Warning: failed to save AI meal plan:", e)

    return data


def get_latest_weekly_meal_plan(
    db: Session,
    user_id: int
) -> Optional[Dict[str, Any]]:
    """
    Returns the latest saved AI meal plan JSON for a user
    (the one saved in MealPlan.plan_json), or None if not found.
    """
    plan = (
        db.query(models.MealPlan)
        .filter(models.MealPlan.user_id == user_id, models.MealPlan.plan_json != None)
        .order_by(models.MealPlan.created_at.desc())
        .first()
    )

    if not plan or not plan.plan_json:
        return None

    return json.loads(plan.plan_json)
