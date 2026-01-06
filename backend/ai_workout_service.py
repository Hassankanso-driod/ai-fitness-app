# ai_workout_service.py
import os
import json
import io
from datetime import datetime, timezone
from typing import Dict, Any, Optional, List

from sqlalchemy.orm import Session
from dotenv import load_dotenv
from openai import OpenAI

from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib.units import cm

import models
import schemas

# Load .env (OPENAI_API_KEY, OPENAI_WORKOUT_MODEL)
load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

PROMPT_VERSION = "workout_weekly_v1.1"


def _utc_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _as_int(x: Any, default: int = 0) -> int:
    try:
        return int(x)
    except Exception:
        return default


def _clamp(n: int, lo: int, hi: int) -> int:
    return max(lo, min(hi, n))


def _ensure_list_str(v: Any) -> List[str]:
    if isinstance(v, list):
        out = []
        for item in v:
            if item is None:
                continue
            out.append(str(item))
        return out
    if v is None:
        return []
    return [str(v)]


def _schema_min_validate(plan: Dict[str, Any]) -> None:
    """
    Minimal structural checks to prevent saving unusable JSON.
    (Not a full JSON-schema validator, but enough to avoid garbage.)
    """
    if not isinstance(plan, dict):
        raise ValueError("AI output must be a JSON object.")
    if "meta" not in plan or "weeks" not in plan:
        raise ValueError("AI output schema mismatch: missing meta/weeks.")

    weeks = plan.get("weeks")
    if not isinstance(weeks, list) or len(weeks) != 1:
        raise ValueError("AI must return exactly 1 week in weeks[].")
    week = weeks[0]
    if not isinstance(week, dict) or week.get("week_number") != 1:
        raise ValueError("Week number must be 1 for weekly plan.")

    days = week.get("days")
    if not isinstance(days, list) or len(days) == 0:
        raise ValueError("AI week.days must be a non-empty array.")

    # Check each day has exercises array
    for d in days:
        if not isinstance(d, dict):
            raise ValueError("Each day must be an object.")
        exs = d.get("exercises")
        if not isinstance(exs, list) or len(exs) == 0:
            raise ValueError("Each day.exercises must be a non-empty array.")
        for ex in exs:
            if not isinstance(ex, dict):
                raise ValueError("Each exercise must be an object.")
            # Must have substitutions array (2)
            subs = ex.get("substitutions")
            if not isinstance(subs, list) or len(subs) < 2:
                raise ValueError("Each exercise must include at least 2 substitutions.")


def generate_weekly_workout_plan(
    db: Session,
    payload: schemas.AIWorkoutPlanRequest,
) -> Dict[str, Any]:
    """
    Generate a ONE-WEEK workout plan (JSON) using OpenAI and save it in workout_plans table.

    Keeps:
    - experience
    - language
    - days_per_week
    - split
    - equipment
    - focus
    - injuries

    Saves:
    - WorkoutPlan row with plan_json
    Returns:
    - dict (JSON plan)
    """
    # 1) Get user
    user = db.query(models.User).filter(models.User.id == payload.user_id).first()
    if not user:
        raise ValueError("User not found")

    prefs = payload.prefs

    # Normalize days_per_week sanity
    days_per_week = _clamp(_as_int(getattr(prefs, "days_per_week", 3), 3), 1, 7)

    # 2) Professional system prompt (STRICT JSON + stronger coaching rules)
    system_prompt = r"""
You are a professional Strength & Conditioning coach designing a SAFE, realistic, app-friendly weekly workout plan.

IMPORTANT OUTPUT RULE:
- You MUST respond with VALID JSON ONLY (no markdown, no explanation, no extra text).
- Return JSON that matches EXACTLY this schema (keys + nesting). Optional fields allowed ONLY where shown.

SCHEMA:
{
  "meta": {
    "split": "push_pull_legs | full_body | upper_lower | bro_split",
    "days_per_week": number,
    "experience": "beginner | intermediate | advanced",
    "focus": "strength | muscle_gain | fat_loss | athletic | general_fitness",
    "equipment": "gym | home | both",
    "language": "en | ar",
    "created_at": "ISO-8601 string",
    "prompt_version": "string",
    "model": "string",
    "disclaimer": "string"
  },
  "weeks": [
    {
      "week_number": 1,
      "goal_focus": "string",
      "progression_notes": ["string", "string", "string"],
      "days": [
        {
          "label": "Day 1 - Push",
          "focus": "string",
          "estimated_time_min": number,
          "warmup": ["string", "string", "string"],
          "exercises": [
            {
              "name": "string",
              "sets": "string",
              "reps": "string",
              "rest": "string",
              "tempo": "string",
              "intensity": "string",
              "notes": "string",
              "substitutions": ["string", "string"]
            }
          ],
          "finisher_optional": ["string"],
          "cooldown": ["string", "string"],
          "day_notes": ["string", "string"]
        }
      ]
    }
  ]
}

HARD RULES (must follow):
1) Generate EXACTLY 1 week only:
   - weeks must contain exactly one item with week_number = 1.
2) For the week, generate EXACTLY meta.days_per_week training days.
   - Do NOT output rest days as separate days.
   - Put rest/recovery instructions inside progression_notes or day_notes.
3) Split consistency:
   - If split = push_pull_legs, labels must reflect it.
   - If split = upper_lower, labels must reflect it.
   - If split = full_body, every day is full-body.
4) Equipment filtering:
   - home: avoid machines; use bodyweight + bands + dumbbells if reasonable.
   - gym: allow machines and free weights.
   - both: mix intelligently.
5) Safety & injuries:
   - No diagnosis. Respect injuries/limitations: avoid painful patterns and offer alternatives.
6) Each day must include:
   - warmup (3 items),
   - cooldown (2 items),
   - estimated_time_min,
   - day_notes (2 items).
7) Each exercise must include:
   - sets, reps, rest, tempo, intensity, notes,
   - substitutions EXACTLY 2 items (equipment alternatives).
8) Plan realism:
   - Start with main compound movement(s) then accessories.
   - Keep total session volume appropriate to experience level.
   - Avoid excessive complexity; use simple exercise names.

COACHING QUALITY RULES:
- Use RPE/RIR style intensity for every exercise (example: "RPE 7 (2–3 reps in reserve)").
- Tempo format example: "3-1-1" (eccentric-pause-concentric) or "controlled".
- Rest: strength compounds 2–3 min, hypertrophy 60–90 sec, fat-loss circuits 30–60 sec.
- Provide clear notes: setup cues, range-of-motion, or form reminders (short).

FOCUS LOGIC:
- strength: prioritize compound lifts; lower reps; longer rest; fewer accessories.
- muscle_gain: 6–12 reps mostly; moderate rest; add accessories.
- fat_loss: moderate loads; shorter rest; optional finisher; maintain strength.
- athletic: include power/plyos early (if safe) + conditioning; keep quality.
- general_fitness: balanced mix, moderate intensity, sustainable volume.

LANGUAGE RULES:
- If meta.language = "ar": all user-facing text in Modern Standard Arabic (فصحى).
  You may keep exercise names as "English (Arabic)" e.g., "Bench Press (ضغط صدر)".
- If meta.language = "en": clear simple English.
""".strip()

    # 3) Language handling
    lang_is_ar = (prefs.language == "ar")
    lang_label = "Arabic" if lang_is_ar else "English"

    # 4) User prompt (more professional + more constraints)
    injuries_text = getattr(prefs, "injuries", "") or ""
    injuries_text = str(injuries_text).strip()
    injuries_text = injuries_text if injuries_text else "none"

    user_prompt = f"""
Create a ONE-WEEK plan for this user.

USER PROFILE (do not invent data):
- ID: {user.id}
- Name: {user.first_name}
- Age: {user.age}
- Sex: {user.sex}
- Height: {user.height_cm} cm
- Weight: {user.weight_kg} kg
- Goal: {user.goal}

PREFERENCES (must follow):
- Experience: {prefs.experience}
- Days per week: {days_per_week}
- Split: {prefs.split}
- Equipment: {prefs.equipment}
- Focus: {prefs.focus}
- Injuries/limitations: {injuries_text}
- Output language: {lang_label}

PLAN REQUIREMENTS:
- Use EXACT schema from system message.
- weeks must contain exactly one item (week_number=1).
- Generate exactly {days_per_week} days in week.days.
- Do not include rest days as separate day objects.
- Keep day labels consistent with split style.
- Warmup must be 3 items. Cooldown must be 2 items.
- day_notes must be exactly 2 short bullet strings.
- Every exercise must have exactly 2 substitutions.
- Ensure exercises match equipment and the user's experience level.

COACHING DETAILS (make it app-friendly):
- Include estimated_time_min for each day (realistic).
- For each exercise:
  - sets + reps appropriate to focus + experience
  - rest time
  - tempo
  - intensity using RPE/RIR wording
  - a short actionable notes field (1 sentence)

META FIELDS (must set):
- meta.created_at = current UTC ISO time
- meta.prompt_version = "{PROMPT_VERSION}"
- meta.model = the model name used
- meta.disclaimer = 1 short safety sentence

Return VALID JSON only.
""".strip()

    # 5) Call OpenAI (force JSON)
    model_name = os.getenv("OPENAI_WORKOUT_MODEL", "gpt-4o-mini")
    completion = client.chat.completions.create(
        model=model_name,
        response_format={"type": "json_object"},
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        temperature=0.7,
        max_tokens=3200,
    )

    content = completion.choices[0].message.content

    # 6) Parse JSON safely
    try:
        data = json.loads(content)
    except json.JSONDecodeError:
        raise ValueError("AI did not return valid JSON for workout plan.")

    # 7) Validate minimal structure (avoid saving garbage)
    _schema_min_validate(data)

    # 7.1) Enforce meta and expected day count
    meta = data.get("meta") or {}
    week = (data.get("weeks") or [{}])[0]
    days = week.get("days") or []

    # Ensure requested day count matches output
    if len(days) != days_per_week:
        raise ValueError(f"AI must return exactly {days_per_week} training days, got {len(days)}.")

    meta.setdefault("created_at", _utc_iso())
    meta.setdefault("prompt_version", PROMPT_VERSION)
    meta.setdefault("model", model_name)

    # Normalize meta fields to prefs where missing
    meta.setdefault("split", getattr(prefs, "split", "full_body"))
    meta.setdefault("days_per_week", days_per_week)
    meta.setdefault("experience", getattr(prefs, "experience", "beginner"))
    meta.setdefault("focus", getattr(prefs, "focus", "general_fitness"))
    meta.setdefault("equipment", getattr(prefs, "equipment", "gym"))
    meta.setdefault("language", getattr(prefs, "language", "en"))
    meta.setdefault(
        "disclaimer",
        "Train safely and stop if you feel sharp pain or dizziness."
        if not lang_is_ar
        else "تدرّب بأمان وتوقّف إذا شعرت بألم حاد أو دوار."
    )

    data["meta"] = meta

    # 8) Save to DB
    try:
        db_plan = models.WorkoutPlan(
            user_id=user.id,
            split=meta.get("split", getattr(prefs, "split", "")),
            days_per_week=meta.get("days_per_week", days_per_week),
            experience=meta.get("experience", getattr(prefs, "experience", "")),
            goal_focus=meta.get("focus", getattr(prefs, "focus", "")),
            language=meta.get("language", getattr(prefs, "language", "")),
            plan_json=json.dumps(data, ensure_ascii=False),
        )
        db.add(db_plan)
        db.commit()
        db.refresh(db_plan)
    except Exception as e:
        print("Warning: failed to save AI workout plan:", e)

    return data


def workout_plan_json_to_pdf_bytes(plan: Dict[str, Any], title: Optional[str] = None) -> bytes:
    """
    Build a clean PDF from a weekly workout JSON plan using ReportLab.
    Returns PDF bytes.
    """
    buffer = io.BytesIO()
    c = canvas.Canvas(buffer, pagesize=A4)
    W, H = A4

    margin_x = 1.6 * cm
    y = H - 1.6 * cm

    def line(txt: str, size: int = 10, bold: bool = False, gap: float = 0.45 * cm):
        nonlocal y
        if y < 2.0 * cm:
            c.showPage()
            y = H - 1.6 * cm

        c.setFont("Helvetica-Bold" if bold else "Helvetica", size)
        c.drawString(margin_x, y, (txt or "")[:1200])
        y -= gap

    meta = plan.get("meta") or {}
    weeks = plan.get("weeks") or []
    week = weeks[0] if weeks else {}

    header = title or "Workout Plan (Week 1)"
    line(header, size=16, bold=True, gap=0.8 * cm)

    sub = (
        f"Split: {meta.get('split','')} | Days/Week: {meta.get('days_per_week','')} | "
        f"Exp: {meta.get('experience','')} | Focus: {meta.get('focus','')} | Equip: {meta.get('equipment','')}"
    )
    line(sub, size=10, bold=False, gap=0.6 * cm)

    created_at = meta.get("created_at", "")
    model = meta.get("model", "")
    version = meta.get("prompt_version", "")
    line(f"Generated: {created_at}   •   Model: {model}   •   Version: {version}", size=9, gap=0.7 * cm)

    # Progression notes
    prog = _ensure_list_str(week.get("progression_notes"))
    if prog:
        line("Progression Notes:", bold=True, gap=0.55 * cm)
        for p in prog:
            line(f"• {p}", size=10, gap=0.45 * cm)
        y -= 0.2 * cm

    days = week.get("days") or []
    for d in days:
        line(d.get("label", "Day"), size=13, bold=True, gap=0.65 * cm)
        if d.get("focus"):
            line(f"Focus: {d.get('focus')}", size=10, gap=0.45 * cm)
        if d.get("estimated_time_min"):
            line(f"Estimated time: {d.get('estimated_time_min')} min", size=10, gap=0.55 * cm)

        warm = _ensure_list_str(d.get("warmup"))
        if warm:
            line("Warm-up:", bold=True, gap=0.5 * cm)
            for w in warm:
                line(f"• {w}", size=10, gap=0.45 * cm)

        exs = d.get("exercises") or []
        if exs:
            y -= 0.1 * cm
            line("Exercises:", bold=True, gap=0.5 * cm)
            for ex in exs:
                name = ex.get("name", "")
                sets = ex.get("sets", "")
                reps = ex.get("reps", "")
                rest = ex.get("rest", "")
                tempo = ex.get("tempo", "")
                intensity = ex.get("intensity", "")
                notes = ex.get("notes", "")

                line(f"- {name}", size=11, bold=True, gap=0.48 * cm)
                line(f"  Sets: {sets} | Reps: {reps} | Rest: {rest}", size=10, gap=0.42 * cm)
                if tempo or intensity:
                    line(f"  Tempo: {tempo} | Intensity: {intensity}", size=9, gap=0.42 * cm)
                if notes:
                    line(f"  Notes: {notes}", size=9, gap=0.42 * cm)

                subs = ex.get("substitutions") or []
                if subs:
                    line(f"  Substitutions: {' • '.join([str(s) for s in subs])}", size=9, gap=0.5 * cm)

        fin = _ensure_list_str(d.get("finisher_optional"))
        if fin:
            line("Optional Finisher:", bold=True, gap=0.5 * cm)
            for f in fin:
                line(f"• {f}", size=10, gap=0.45 * cm)

        cool = _ensure_list_str(d.get("cooldown"))
        if cool:
            line("Cool-down:", bold=True, gap=0.5 * cm)
            for cc in cool:
                line(f"• {cc}", size=10, gap=0.45 * cm)

        notes = _ensure_list_str(d.get("day_notes"))
        if notes:
            line("Day Notes:", bold=True, gap=0.5 * cm)
            for n in notes:
                line(f"• {n}", size=10, gap=0.45 * cm)

        y -= 0.4 * cm

    disclaimer = meta.get("disclaimer") or "Train safely. Stop if pain occurs."
    y -= 0.2 * cm
    line("Disclaimer:", bold=True, gap=0.5 * cm)
    line(disclaimer, size=9, gap=0.45 * cm)

    c.save()
    pdf = buffer.getvalue()
    buffer.close()
    return pdf
