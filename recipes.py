import csv
import json
from fractions import Fraction
import re



def add_recipe(name, ingredients, measurements, mealType, description, servings, time, numOfSteps, notes, freezerMealTF, steps):  #this function adds a recipe to the recipe storage
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
      'steps': json.dumps(steps),  # Convert list to JSON string
      'ratings': json.dumps([]),  # Store individual ratings as JSON array
      'average_rating': 0.0  # Store calculated average
  }
  recipes.append(new_recipe)
  with open('./data/recipeStorage.csv', 'w', newline='') as file:
    writer = csv.DictWriter(file, fieldnames=recipes[0].keys())
    writer.writeheader()
    for line in recipes:
      writer.writerow(line)

def get_recipes():  #this function gets all recipes from the recipe storage

  with open('./data/recipeStorage.csv', 'r', newline='') as file:
    reader = csv.DictReader(file)
    recipes = list(reader)
  
  if not recipes:
    return {}

  # Sort recipes by average rating (highest first)
  recipes.sort(key=lambda x: float(x.get('average_rating', 0) or 0), reverse=True)

  data = {}
  for i, rec in enumerate(recipes):
    for key in ['name', 'ingredients', 'measurements', 'mealType', 'description', 'servings', 'time', 'numOfSteps', 'notes', 'freezerMealTF', 'steps', 'ratings', 'average_rating']:
      if key not in data:
        data[key] = []
    
    data['name'].append(rec['name'])
    data['ingredients'].append(json.loads(rec['ingredients']))
    data['measurements'].append(json.loads(rec['measurements']))
    data['mealType'].append(rec['mealType'])
    data['description'].append(rec['description'])
    try:
        data['servings'].append(int(rec['servings']))
    except (ValueError, TypeError):
        data['servings'].append(1)
    data['time'].append(rec['time'])
    try:
        data['numOfSteps'].append(int(rec['numOfSteps']))
    except (ValueError, TypeError):
        data['numOfSteps'].append(1)
    data['notes'].append(rec['notes'])
    data['freezerMealTF'].append(rec['freezerMealTF'])
    data['steps'].append(json.loads(rec['steps']))
    # Handle ratings field - ensure it's valid JSON
    ratings_str = rec.get('ratings', '[]')
    if not ratings_str or ratings_str.strip() == '':
        ratings_str = '[]'
    try:
        ratings = json.loads(ratings_str)
    except json.JSONDecodeError:
        ratings = []
    data['ratings'].append(ratings)
    
    # Handle average_rating field
    avg_rating = rec.get('average_rating', 0)
    if not avg_rating or avg_rating == '':
        avg_rating = 0
    data['average_rating'].append(float(avg_rating))
  
  return data



def get_recipe_by_name(recipe_name):
  """Get a single recipe by name"""
  with open('./data/recipeStorage.csv', 'r') as file:
      reader = csv.DictReader(file)
      recipes = list(reader)

  for recipe in recipes:
      if recipe['name'] == recipe_name:
          recipe['ingredients'] = json.loads(recipe.get('ingredients', '[]') or '[]')
          recipe['measurements'] = json.loads(recipe.get('measurements', '[]') or '[]')
          recipe['steps'] = json.loads(recipe.get('steps', '[]') or '[]')
          ratings_str = recipe.get('ratings', '[]')
          if not ratings_str or ratings_str.strip() == '':
              ratings_str = '[]'
          recipe['ratings'] = json.loads(ratings_str)
          recipe['average_rating'] = float(recipe.get('average_rating', 0.0) or 0.0)
          return recipe
  return None


def update_recipe(old_name, name, ingredients, measurements, mealType, description, servings, time, numOfSteps, notes, freezerMealTF, steps):
    # Read existing recipes from CSV
    with open('./data/recipeStorage.csv', 'r') as file:
        reader = csv.DictReader(file)
        recipes = list(reader)
    
    # Find and update the recipe
    updated = False
    for recipe in recipes:
        if recipe['name'] == old_name:
            recipe.update({
                'name': name,
                'ingredients': json.dumps(ingredients),
                'measurements': json.dumps(measurements),
                'mealType': mealType,
                'description': description,
                'servings': servings,
                'time': time,
                'numOfSteps': numOfSteps,
                'notes': notes,
                'freezerMealTF': freezerMealTF,
                'steps': json.dumps(steps)
                # Preserve existing ratings and average_rating
            })
            updated = True
            break
    
    # Write back to CSV
    if updated:
        with open('./data/recipeStorage.csv', 'w', newline='') as file:
            if recipes:
                writer = csv.DictWriter(file, fieldnames=recipes[0].keys())
                writer.writeheader()
                for line in recipes:
                    writer.writerow(line)
        return True
    else:
        return False

def add_rating(recipe_name, rating):
  """Add a rating to a recipe and update the average"""
  with open('./data/recipeStorage.csv', 'r') as file:
      reader = csv.DictReader(file)
      recipes = list(reader)

  updated = False
  for recipe in recipes:
      if recipe['name'] == recipe_name:
        ratings_str = recipe.get('ratings', '[]')
        if not ratings_str.strip():
          ratings_str = '[]'  # Assign an empty list if true
        current_ratings = json.loads(ratings_str)
        current_ratings.append(rating)
        average_rating = sum(current_ratings) / len(current_ratings)
        recipe['ratings'] = json.dumps(current_ratings)
        recipe['average_rating'] = str(round(average_rating, 2))
        updated = True
        break

  if updated:
      with open('./data/recipeStorage.csv', 'w', newline='') as file:
          writer = csv.DictWriter(file, fieldnames=recipes[0].keys())
          writer.writeheader()
          for line in recipes:
              writer.writerow(line)
      return True
  return False

def delete_recipe(recipe_name):
    # Load all recipes as a list of dicts
    with open('./data/recipeStorage.csv', 'r') as file:
        reader = csv.DictReader(file)
        recipes = list(reader)

    # Filter out the recipe with the matching name
    updated_recipes = [r for r in recipes if r['name'] != recipe_name]

    # If no recipe was removed, return False
    if len(updated_recipes) == len(recipes):
        return False

    # Save the updated list
    save_recipes(updated_recipes)
    return True

def save_recipes(recipe_list):
    """Save a list of recipe dictionaries to the CSV file"""
    if not recipe_list:
        return

    with open('./data/recipeStorage.csv', 'w', newline='') as file:
        writer = csv.DictWriter(file, fieldnames=recipe_list[0].keys())
        writer.writeheader()
        for recipe in recipe_list:
            writer.writerow(recipe)

def scale_measurement(measurement, factor):
    """
    Attempt to scale the numeric portion of a measurement.
    Handles integers, decimals, and simple fractions.
    Appends message if unable to scale.
    """
    # Regex to extract a number (including fractions) from the start of the string
    match = re.match(r'^([\d\s\/\.]+)', measurement.strip())
    if not match:
        return f"{measurement} (x{factor} - could not increment)"

    numeric_part = match.group(1).strip()
    rest = measurement[len(numeric_part):].strip()

    try:
        # Convert to float or fraction
        if ' ' in numeric_part:
            # Handle mixed number like "1 1/2"
            whole, frac = numeric_part.split()
            scaled = (int(whole) + float(Fraction(frac))) * factor
        else:
            scaled = float(Fraction(numeric_part)) * factor

        # Simplify to proper format
        scaled_frac = Fraction(scaled).limit_denominator()
        if scaled_frac.denominator == 1:
            result = f"{scaled_frac.numerator}"
        else:
            result = f"{scaled_frac.numerator}/{scaled_frac.denominator}"
        return f"{result} {rest}".strip()
    except Exception:
        return f"{measurement} (x{factor} - could not increment)"