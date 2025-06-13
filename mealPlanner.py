
import csv
import pandas as pd
import json

def add_meal(day, mealType, recipe):
    with open('./data/mealPlan.csv', 'r') as file:
        reader = csv.DictReader(file)
        mealPlanner = list(reader)[0]
    
    meals = {
        "monday": json.loads(mealPlanner["monday"]),
        "tuesday": json.loads(mealPlanner["tuesday"]),
        "wednesday": json.loads(mealPlanner["wednesday"]),
        "thursday": json.loads(mealPlanner["thursday"]),
        "friday": json.loads(mealPlanner["friday"]),
        "saturday": json.loads(mealPlanner["saturday"]),
        "sunday": json.loads(mealPlanner["sunday"])
    }
    
    day = day.lower()
    if day in meals:
        if mealType.lower() == "breakfast":
            meals[day][0] = recipe
        elif mealType.lower() == "lunch":
            meals[day][1] = recipe
        elif mealType.lower() == "dinner":
            meals[day][2] = recipe
    
    with open('./data/mealPlan.csv', 'w', newline='') as file:
        writer = csv.DictWriter(file, fieldnames=meals.keys())
        writer.writeheader()
        writer.writerow({k: json.dumps(v) for k, v in meals.items()})

def get_meal_plan():
    try:
        with open('./data/mealPlan.csv', 'r') as file:
            reader = csv.DictReader(file)
            return list(reader)
    except FileNotFoundError:
        return []
