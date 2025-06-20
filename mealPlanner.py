
import csv

import json

def add_meal(day, mealType, recipe):
    with open('./data/mealPlan.csv', 'r') as file:
        reader = csv.DictReader(file)
        mealPlanner = list(reader)[0]

    meals = {}
    for d, val in mealPlanner.items():
        if isinstance(val, str) and val.strip():
            try:
                meals[d] = json.loads(val)
            except json.JSONDecodeError:
                meals[d] = ["", "", "", "", "", ""]
        else:
            meals[d] = ["", "", "", "", "", ""]

    meal_index = {
        "breakfast": 0,
        "lunch": 1,
        "dinner": 2,
        "side dish": 3,
        "dessert": 4,
        "snack": 5
    }

    day = day.lower()
    mealType = mealType.lower()

    if day in meals and mealType in meal_index:
        idx = meal_index[mealType]

        # Ensure it's a list of recipes, not nested lists
        current = meals[day][idx]
        if isinstance(current, list):
            # If already a list, just append
            meals[day][idx].append(recipe)
        elif isinstance(current, str):
            # Convert string to list
            meals[day][idx] = [current] if current else []
            meals[day][idx].append(recipe)
        else:
            # Unexpected type - reset to list with the new recipe
            meals[day][idx] = [recipe]

    with open('./data/mealPlan.csv', 'w', newline='') as file:
        writer = csv.DictWriter(file, fieldnames=meals.keys())
        writer.writeheader()
        # Convert back to JSON strings to write
        writer.writerow({k: json.dumps(v) for k, v in meals.items()})

def get_meal_plan():
    try:
        with open('./data/mealPlan.csv', 'r') as file:
            reader = csv.DictReader(file)
            return list(reader)
    except FileNotFoundError:
        return []
