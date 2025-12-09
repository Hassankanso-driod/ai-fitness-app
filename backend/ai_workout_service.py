# ai_workout_service.py
import os
import json
from datetime import datetime, timedelta
from typing import Dict, Any

from sqlalchemy.orm import Session
from dotenv import load_dotenv
from openai import OpenAI

import models
import schemas

# تحميل .env لقراءة OPENAI_API_KEY
load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


def generate_monthly_workout_plan(
    db: Session,
    payload: schemas.AIWorkoutPlanRequest,
) -> Dict[str, Any]:
    """
    Uses GPT-4.1-mini to generate a 4-week workout plan.

    - Reads user from users table
    - Uses workout preferences from payload.prefs
    - Generates a 4-week structured plan (JSON)
    - Tries to save in workout_plans table (plan_json)
    - Returns JSON ready for AIWorkoutPlanResponse
    """

    # 1) Get user
    user = db.query(models.User).filter(models.User.id == payload.user_id).first()
    if not user:
        raise ValueError("User not found")

    prefs = payload.prefs

    # 2) Check if user already has a workout plan (only once, as requested)
    existing_plan = (
        db.query(models.WorkoutPlan)
        .filter(models.WorkoutPlan.user_id == user.id)
        .order_by(models.WorkoutPlan.created_at.desc())
        .first()
    )

    if existing_plan:
        # لو بدك تسمح مرة كل شهر بدل مرة وحدة بس، ممكن تستعمل الشرط التالي:
        # if existing_plan.created_at >= datetime.utcnow() - timedelta(days=30):
        #     raise ValueError("You already generated a workout plan in the last 30 days.")
        raise ValueError("You already generated a workout plan. Only one plan is allowed.")

    # 3) System prompt: define JSON format
    system_prompt = """
You are a professional fitness coach for a mobile app.
You MUST respond with valid JSON only, no extra text.

JSON format:
{
  "meta": {
    "split": "push_pull_legs | full_body | upper_lower | bro_split",
    "days_per_week": number,
    "experience": "beginner | intermediate | advanced",
    "focus": "strength | muscle_gain | fat_loss | athletic | general_fitness",
    "equipment": "gym | home | both",
    "language": "en | ar"
  },
  "weeks": [
    {
      "week_number": 1,
      "goal_focus": "string",
      "days": [
        {
          "label": "Day 1 - Push",
          "focus": "Chest, shoulders, triceps",
          "exercises": [
            {
              "name": "Bench Press",
              "sets": "4",
              "reps": "6-8",
              "rest": "90 sec",
              "notes": "Keep shoulder blades tight."
            }
          ],
          "notes": [
            "Warm up 5–10 minutes before starting.",
            "Focus on good form over heavy weight."
          ]
        }
      ]
    }
  ]
}

Rules:
- Always generate exactly 4 weeks (week_number = 1, 2, 3, 4).
- For each week, generate exactly meta.days_per_week training days.
- You may mention rest days only in notes, not as separate days.
- Adapt difficulty, volume, and exercise selection to experience level.
- Full-body / PPL / upper-lower / bro split must be consistent across all weeks.
- Focus:
  - strength       -> lower reps, heavier sets, core compounds.
  - muscle_gain    -> 8–12 reps, moderate volume.
  - fat_loss       -> full-body circuits, shorter rest, some cardio.
  - athletic       -> explosive work, agility, mixed strength/cardio.
  - general_fitness-> balanced mix of strength and conditioning.
- Use simple names for exercises that are easy to understand.
"""

    # 4) Language / user prompt
    lang_label = "Arabic" if prefs.language == "ar" else "English"

    language_instruction = """
If language is "ar":
- Write all labels, focus, notes, and exercise descriptions in Modern Standard Arabic.
- You may keep international exercise names partially in English + Arabic, e.g., "Bench Press (ضغط صدر)".
If language is "en":
- Write everything in clear, simple English.
"""

    user_prompt = f"""
User profile:
- ID: {user.id}
- Name: {user.first_name}
- Age: {user.age}
- Sex: {user.sex}
- Height: {user.height_cm} cm
- Weight: {user.weight_kg} kg
- Goal: {user.goal}

Workout preferences:
- Experience level: {prefs.experience}
- Days per week: {prefs.days_per_week}
- Split style: {prefs.split}
- Equipment: {prefs.equipment}
- Focus: {prefs.focus}
- Injuries or limitations: {prefs.injuries}
- Output language: {lang_label}

{language_instruction}

Generate a structured 4-week plan in the EXACT JSON format specified in the system message.
Do not include any explanation outside the JSON.
"""

    # 5) Call OpenAI (force JSON output)
    completion = client.chat.completions.create(
        model="gpt-4.1-mini",
        response_format={"type": "json_object"},  # ✅ مهم حتى ما يرجع نص خارج JSON
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        temperature=0.8,
        max_tokens=3500,
    )

    content = completion.choices[0].message.content

    # 6) Parse JSON safely
    try:
        data = json.loads(content)
    except json.JSONDecodeError:
        # لو صار أي لعب بالـ JSON من الموديل
        raise ValueError("AI did not return valid JSON for workout plan.")

    # 7) Save to DB (but don't crash if DB has an issue)
    try:
        meta = data.get("meta", {}) or {}
        db_plan = models.WorkoutPlan(
            user_id=user.id,
            split=meta.get("split", prefs.split),
            days_per_week=meta.get("days_per_week", prefs.days_per_week),
            experience=meta.get("experience", prefs.experience),
            goal_focus=meta.get("focus", prefs.focus),
            language=meta.get("language", prefs.language),
            plan_json=json.dumps(data),
        )
        db.add(db_plan)
        db.commit()
        db.refresh(db_plan)
    except Exception as e:
        # ما منوقف الريكوست، بس منطبع و منكمل نرجّع الخطة للـ frontend
        print("Warning: failed to save AI workout plan:", e)

    return data
