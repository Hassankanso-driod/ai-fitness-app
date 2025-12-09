"""
meal_plan_generator.py - Meal Plan Generation Logic

This module handles the generation of meal plans. It can be extended to integrate
with AI services like OpenAI GPT-4, Ollama, or other meal planning APIs.

Currently implements mock data generation for development/testing.
In production, this should be replaced with actual AI integration.
"""

from typing import List
import random
from datetime import datetime
import schemas


def generate_meal_plan(
    preferences: schemas.MealPlanPreferences,
    targets: schemas.MealPlanTargets,
    duration: int = 7
) -> schemas.MealPlanData:
    """
    Generate a complete meal plan for the specified duration.
    
    In production, this should call an AI service (OpenAI GPT-4, Ollama, etc.)
    to generate realistic meal plans based on preferences and targets.
    """
    days: List[schemas.DayPlan] = []
    
    for day_num in range(1, duration + 1):
        day_plan = generate_single_day(day_num, preferences, targets)
        days.append(day_plan)
    
    shopping_list = generate_shopping_list(days, preferences)
    
    return schemas.MealPlanData(
        preferences=preferences,
        days=days,
        shoppingList=shopping_list,
        generatedAt=datetime.now().isoformat()
    )


def generate_single_day(
    day_number: int,
    preferences: schemas.MealPlanPreferences,
    targets: schemas.MealPlanTargets
) -> schemas.DayPlan:
    """
    Generate meals for a single day.
    
    This is a mock implementation. In production, integrate with AI service
    to generate realistic meals that match preferences and hit macro targets.
    """
    # Determine meal types based on meals per day
    meal_types = ["Breakfast", "Lunch", "Dinner"]
    if preferences.mealsPerDay >= 4:
        meal_types.append("Snack")
    if preferences.mealsPerDay >= 5:
        meal_types.append("Snack 2")
    
    meals: List[schemas.Meal] = []
    total_calories = 0
    total_protein = 0
    total_carbs = 0
    total_fat = 0
    
    # Generate meals
    for meal_type in meal_types:
        # Calculate target macros per meal (with some variance)
        target_cal_per_meal = targets.calories / preferences.mealsPerDay
        target_protein_per_meal = targets.protein / preferences.mealsPerDay
        target_carbs_per_meal = targets.carbs / preferences.mealsPerDay
        target_fat_per_meal = targets.fat / preferences.mealsPerDay
        
        # Add some variance (±10%)
        variance = 0.1
        calories = int(target_cal_per_meal * (1 + random.uniform(-variance, variance)))
        protein = int(target_protein_per_meal * (1 + random.uniform(-variance, variance)))
        carbs = int(target_carbs_per_meal * (1 + random.uniform(-variance, variance)))
        fat = int(target_fat_per_meal * (1 + random.uniform(-variance, variance)))
        
        meal = schemas.Meal(
            name=f"{meal_type} Option {day_number}",
            mealType=meal_type,
            calories=calories,
            protein=protein,
            carbs=carbs,
            fat=fat,
            ingredients=generate_ingredients(meal_type, preferences),
            instructions=generate_instructions(meal_type, preferences),
            substitutions=generate_substitutions(meal_type, preferences)
        )
        
        meals.append(meal)
        total_calories += calories
        total_protein += protein
        total_carbs += carbs
        total_fat += fat
    
    # Adjust to match targets more closely (simple normalization)
    if total_calories != 0:
        scale_factor = targets.calories / total_calories
        for meal in meals:
            meal.calories = int(meal.calories * scale_factor)
            meal.protein = int(meal.protein * scale_factor)
            meal.carbs = int(meal.carbs * scale_factor)
            meal.fat = int(meal.fat * scale_factor)
        
        total_calories = sum(m.calories for m in meals)
        total_protein = sum(m.protein for m in meals)
        total_carbs = sum(m.carbs for m in meals)
        total_fat = sum(m.fat for m in meals)
    
    return schemas.DayPlan(
        day=day_number,
        targetCalories=targets.calories,
        targetProtein=targets.protein,
        targetCarbs=targets.carbs,
        targetFat=targets.fat,
        actualCalories=total_calories,
        actualProtein=total_protein,
        actualCarbs=total_carbs,
        actualFat=total_fat,
        meals=meals
    )


def generate_ingredients(meal_type: str, preferences: schemas.MealPlanPreferences) -> List[schemas.Ingredient]:
    """Generate mock ingredients based on meal type and preferences"""
    # Base ingredients (can be expanded based on preferences)
    base_ingredients = {
        "Breakfast": [
            ("Eggs", "2 pieces"),
            ("Whole grain bread", "2 slices"),
            ("Greek yogurt", "150g"),
        ],
        "Lunch": [
            ("Chicken breast", "150g"),
            ("Brown rice", "100g"),
            ("Mixed vegetables", "200g"),
        ],
        "Dinner": [
            ("Salmon", "150g"),
            ("Sweet potato", "200g"),
            ("Broccoli", "150g"),
        ],
        "Snack": [
            ("Apple", "1 medium"),
            ("Almonds", "30g"),
            ("Protein shake", "1 serving"),
        ],
        "Snack 2": [
            ("Banana", "1 medium"),
            ("Peanut butter", "1 tbsp"),
        ],
    }
    
    ingredients_list = base_ingredients.get(meal_type, base_ingredients["Lunch"])
    
    # Filter based on preferences
    filtered_ingredients = []
    for name, amount in ingredients_list:
        # Skip if in dislike list or allergies
        if name.lower() in [f.lower() for f in preferences.foodsDislike]:
            continue
        if any(allergy.lower() in name.lower() for allergy in preferences.allergies):
            continue
        filtered_ingredients.append(schemas.Ingredient(name=name, amount=amount))
    
    return filtered_ingredients[:5]  # Limit to 5 ingredients


def generate_instructions(meal_type: str, preferences: schemas.MealPlanPreferences) -> List[str]:
    """Generate mock cooking instructions"""
    cooking_times = {
        "10-15": "Quick",
        "20-30": "Moderate",
        "45+": "Detailed",
    }
    
    time_desc = cooking_times.get(preferences.cookingTime, "Moderate")
    
    return [
        f"Prepare all ingredients according to {preferences.cuisine} style",
        f"Follow {time_desc} cooking method ({preferences.cookingTime} minutes)",
        "Season to taste and serve hot",
    ]


def generate_substitutions(meal_type: str, preferences: schemas.MealPlanPreferences) -> List[str]:
    """Generate substitution suggestions"""
    substitutions = []
    
    if preferences.dietStyle == "Vegetarian":
        substitutions.append("Replace meat with tofu or tempeh")
    
    if preferences.dietStyle == "Low-carb":
        substitutions.append("Replace grains with cauliflower rice")
    
    if preferences.cuisine == "Lebanese":
        substitutions.append("Can substitute with other Middle Eastern options")
    
    return substitutions if substitutions else None


def generate_shopping_list(
    days: List[schemas.DayPlan],
    preferences: schemas.MealPlanPreferences
) -> List[schemas.ShoppingListCategory]:
    """Generate a consolidated shopping list from all days"""
    # Collect all ingredients from all meals
    all_ingredients = {}
    
    for day in days:
        for meal in day.meals:
            for ingredient in meal.ingredients:
                if ingredient.name not in all_ingredients:
                    all_ingredients[ingredient.name] = []
                all_ingredients[ingredient.name].append(ingredient.amount)
    
    # Categorize ingredients
    categories = {
        "Protein": ["chicken", "beef", "pork", "fish", "salmon", "tuna", "eggs", "tofu", "tempeh"],
        "Vegetables": ["broccoli", "spinach", "carrots", "bell pepper", "tomato", "onion", "garlic", "vegetables"],
        "Carbs": ["rice", "pasta", "bread", "potato", "quinoa", "oats"],
        "Dairy": ["milk", "cheese", "yogurt", "butter"],
        "Pantry": ["oil", "spices", "salt", "pepper", "flour", "sugar"],
    }
    
    categorized = {cat: [] for cat in categories.keys()}
    categorized["Other"] = []
    
    for ingredient_name, amounts in all_ingredients.items():
        # Combine amounts (simplified)
        total_amount = "1x" if len(amounts) > 0 else amounts[0]
        
        # Find category
        categorized_item = False
        ingredient_lower = ingredient_name.lower()
        
        for category, keywords in categories.items():
            if any(keyword in ingredient_lower for keyword in keywords):
                categorized[category].append(
                    schemas.ShoppingListItem(name=ingredient_name, amount=total_amount)
                )
                categorized_item = True
                break
        
        if not categorized_item:
            categorized["Other"].append(
                schemas.ShoppingListItem(name=ingredient_name, amount=total_amount)
            )
    
    # Convert to response format, only include non-empty categories
    shopping_list = []
    for category, items in categorized.items():
        if items:
            shopping_list.append(
                schemas.ShoppingListCategory(category=category, items=items)
            )
    
    return shopping_list

