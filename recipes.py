import pandas as pd
import csv
import json



def add_recipe(name, ingredients, measurements, mealType, description, servings, time, numOfSteps, notes, freezerMealTF, steps):
  with open('./data/recipeStorage.csv', 'r') as file:
    reader = csv.DictReader(file)
    recipes = list(reader)
  for recipe in recipes:
    if recipe['name'] == name:
      return "Recipe with the same name already exists"
  new_recipe = {
      'name': name,
      'ingredients': json.dumps(ingredients),  # Convert list to JSON string
      'measurements': json.dumps(measurements),  # Convert list to JSON string
      'mealType': mealType,
      'description': description,
      'servings': servings,
      'time': time,
      'numOfSteps': numOfSteps,
      'notes': notes,
      'freezerMealTF': freezerMealTF,
      'steps': json.dumps(steps)  # Convert list to JSON string
  }
  recipes.append(new_recipe)
  with open('./data/recipeStorage.csv', 'w', newline='') as file:
    writer = csv.DictWriter(file, fieldnames=recipes[0].keys())
    writer.writeheader()
    for line in recipes:
      writer.writerow(line)

def get_recipes():

  with open('./data/recipeStorage.csv', 'r', newline='') as file:
    reader = csv.DictReader(file)
    recipes = list(reader)
  
  if not recipes:
    
    return pd.DataFrame(columns=['name', 'ingredients', 'measurements', 'mealType', 'description','servings', 'time', 'numOfSteps', 'notes', 'freezerMealTF', 'steps'])

  data = []
  for rec in recipes:
    data.append({
        'name': rec['name'],
        'ingredients': json.loads(rec['ingredients']),
        'measurements': json.loads(rec['measurements']),
        'mealType': rec['mealType'],
        'description': rec['description'],
        'servings': int(rec['servings']),
        'time': rec['time'],
        'numOfSteps': int(rec['numOfSteps']),
        'notes': rec['notes'],
        'freezerMealTF': rec['freezerMealTF'],
        'steps': json.loads(rec['steps']),
    })
  return pd.DataFrame(data)