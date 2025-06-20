from flask import Flask, request, render_template, redirect, url_for, flash  #Flask handles requests and responses between html and python in this case
import recipes  #imports recipes.py
import groceries  # imports groceries.py
import mealPlanner  # imports mealPlanner.py
import importlib  #used to reload recipes.py
import csv  #used to read and write csv files
import json  #used to convert python lists to json strings
import webScraper #imports webScraper.py

meal_types = ["breakfast", "lunch", "dinner", "side dish", "dessert", "snack"]
importlib.reload(recipes)  #reloads recipes.py

app = Flask(__name__)
app.secret_key = 'recipebookforjane'

app.jinja_env.globals.update(zip=zip)  #allows for zipping of lists in html


@app.route('/')
def index():  #this is the main page
    rec = recipes.get_recipes()

    with open('./data/mealPlan.csv', 'r') as file:
      reader = csv.DictReader(file)
      meal_plan_raw = list(reader)[0]

    meal_plan = {}
    for day in ['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday']:
        val = meal_plan_raw.get(day, "")
        try:
            parsed = json.loads(val) if isinstance(val, str) and val else ["", "", "", "", "", ""]
            # Ensure structure is 2D list for consistency
            meal_plan[day] = [[r] if not isinstance(r, list) else r for r in parsed]
        except (json.JSONDecodeError, TypeError):
            # fallback to 6 empty meal slots
            meal_plan[day] = [[""] for _ in range(6)]
    return render_template('index.html', recipes=rec, meal_plan=meal_plan,meal_types=meal_types)
    

@app.route('/submit', methods=['POST'])
def submit():  #this is the route for submitting a new recipe
  name = request.form['name']
  ingredients = [i.strip() for i in request.form.getlist('ingredients') if i.strip()]
  measurements = [m.strip() for m in request.form.getlist('measurements') if m.strip()]
  steps = [s.strip() for s in request.form.getlist('steps') if s.strip()]

  if len(ingredients) != len(measurements):
      flash("Ingredient and measurement count mismatch. Please check and try again.", "error")
      return redirect(url_for('index') + '#submit')
  mealType = request.form['mealType']
  description = request.form.get('description',"A yummy dish, or so I am told!")
  try:
    servings = int(request.form.get('servings', 1))
  except ValueError:
    servings = 1
  time = request.form.get('time',"Unknown")
  numOfSteps = request.form['numOfSteps']
  notes = request.form.get('notes',"")
  freezerMealTF = request.form['freezerMealTF']
  steps = request.form.getlist('steps')
  recipes.add_recipe(name, ingredients, measurements, mealType, description, servings, time, numOfSteps, notes, freezerMealTF, steps)
  return redirect(url_for('index') + '#view')

@app.route('/planner',methods=['POST'])
def planner():  #this is the route for submitting a new meal to the meal planner
  day = request.form["day"]
  meal = request.form["meal"]  # breakfast/lunch/dinner
  recipe = request.form["recipe"]
  mealPlanner.add_meal(day, meal, recipe)
  return redirect(url_for("index") + '#view')

@app.route('/clear_day', methods=['POST'])
def clear_day():  #this is the route for clearing a day in the meal planner
    day = request.form['day'].lower()

    with open('./data/mealPlan.csv', 'r') as file:
        reader = csv.DictReader(file)
        meal_plan = list(reader)[0]

    meal_plan[day] = json.dumps(["", "", "", "", "",""])  # Clear all 3 meals

    with open('./data/mealPlan.csv', 'w', newline='') as file:
        writer = csv.DictWriter(file, fieldnames=meal_plan.keys())
        writer.writeheader()
        writer.writerow(meal_plan)

    return redirect(url_for('index') + '#meal')

@app.route('/reset_week', methods=['POST'])
def reset_week():  #this is the route for resetting the entire meal planner
    initial_meal_plan = {
        "monday": json.dumps(["", "", "","","",""]),  #json.dumps converts a python list to a json string to be stored in a csv file
        "tuesday": json.dumps(["", "", "", "", "",""]),
        "wednesday": json.dumps(["", "", "", "", "", ""]),
        "thursday": json.dumps(["", "", "", "", "", ""]),
        "friday": json.dumps(["", "", "", "", "", ""]),
        "saturday": json.dumps(["", "", "", "", "", ""]),
        "sunday": json.dumps(["", "", "", "", "", ""]),
    }

    with open('./data/mealPlan.csv', 'w', newline='') as file:
        writer = csv.DictWriter(file, fieldnames=initial_meal_plan.keys())
        writer.writeheader()
        writer.writerow(initial_meal_plan)
    return redirect(url_for('index') + '#meal')

@app.route('/add_grocery', methods=['POST'])
def grocery():  #this is the route for adding a grocery item
    items = request.form.getlist('item')
    amounts = request.form.getlist('amount')
    stores = request.form.getlist('store')
    types = request.form.getlist('type')
    
    # Create list of grocery items
    grocery_items = []
    for i in range(len(items)):
        if items[i].strip():  # Only add non-empty items
            # Handle store selection (dropdown vs text input)
            store_select = request.form.getlist('store_select')
            if i < len(store_select) and store_select[i] and store_select[i] != 'Other':
                store = store_select[i]
            else:
                store = stores[i] if i < len(stores) else ''
            
            # Handle type selection (dropdown vs text input)
            type_select = request.form.getlist('type_select')
            if i < len(type_select) and type_select[i] and type_select[i] != 'Other':
                grocery_type = type_select[i]
            else:
                grocery_type = types[i] if i < len(types) else ''
            
            grocery_items.append({
                'item': items[i].strip(),
                'quantity': amounts[i].strip() if i < len(amounts) else '',
                'store': store.strip(),
                'type': grocery_type.strip()
            })
    
    if grocery_items:
        groceries.add_grocery(grocery_items)
    
    return redirect(url_for('index') + '#grocery')

@app.route('/scrape_url', methods=['POST'])
def scrape_url():
    data = request.get_json()
    url = data.get('url', '')
    if not url.startswith("http"):
        return {"error": "Invalid URL"}, 400
    try:
        scraped = webScraper.scrape(url)
        return {
            "name": scraped[0],
            "ingredients": scraped[1],
            "measurements": scraped[2],
            "mealType": scraped[3],
            "description": scraped[4],
            "servings": scraped[5],
            "time": scraped[6],
            "numOfSteps": scraped[7],
            "notes": scraped[8],
            "freezerMealTF": scraped[9],
            "steps": scraped[10]
        }
    except Exception as e:
        return {"error": str(e)}, 500
    


@app.route('/clear_meal', methods=['POST'])
def clear_meal():
    day = request.form['day'].lower()
    meal = request.form['meal'].lower()

    with open('./data/mealPlan.csv', 'r') as file:
        reader = csv.DictReader(file)
        mealPlanner = list(reader)[0]

    # Load meals
    meals = {}
    for d, val in mealPlanner.items():
        try:
            meals[d] = json.loads(val)
        except json.JSONDecodeError:
            meals[d] = ["", "", "", "", "", ""]

    meal_index = {
        "breakfast": 0,
        "lunch": 1,
        "dinner": 2,
        "side dish": 3,
        "dessert": 4,
        "snack": 5
    }

    if day in meals and meal in meal_index:
        idx = meal_index[meal]
        # Clear that specific meal slot (empty list)
        meals[day][idx] = []

    with open('./data/mealPlan.csv', 'w', newline='') as file:
        writer = csv.DictWriter(file, fieldnames=meals.keys())
        writer.writeheader()
        writer.writerow({k: json.dumps(v) for k, v in meals.items()})

    return redirect(url_for('index') + '#meal')

@app.route('/edit_recipe/<recipe_name>', methods=['GET', 'POST'])
def edit_recipe(recipe_name):
    if request.method == 'GET':
        rec = recipes.get_recipe_by_name(recipe_name)
        if not rec:
            flash(f"Recipe '{recipe_name}' not found.", "error")
            return redirect(url_for('index') + '#view')
        return render_template('edit_recipe.html', recipe=rec)
    
    elif request.method == 'POST':
        # Extract form data (similar to your submit route)
        name = request.form['name']
        ingredients = [i.strip() for i in request.form.getlist('ingredients') if i.strip()]
        measurements = [m.strip() for m in request.form.getlist('measurements') if m.strip()]
        steps = [s.strip() for s in request.form.getlist('steps') if s.strip()]
        mealType = request.form['mealType']
        description = request.form.get('description', "A yummy dish, or so I am told!")
        try:
            servings = int(request.form.get('servings', 1))
        except ValueError:
            servings = 1
        time = request.form.get('time', "Unknown")
        notes = request.form.get('notes', "")
        # Calculate numOfSteps based on actual steps provided
        numOfSteps = len([s for s in steps if s.strip()])
        freezerMealTF = request.form['freezerMealTF']

        # You need to implement update_recipe function that updates the recipe in storage
        success = recipes.update_recipe(
            old_name=recipe_name,
            name=name,
            ingredients=ingredients,
            measurements=measurements,
            mealType=mealType,
            description=description,
            servings=servings,
            time=time,
            numOfSteps=numOfSteps,
            notes=notes,
            freezerMealTF=freezerMealTF,
            steps=steps
        )

        if success:
            flash(f"Recipe '{name}' updated successfully!", "success")
        else:
            flash(f"Failed to update recipe '{name}'.", "error")

        return redirect(url_for('index') + '#view')



@app.route('/get_grocery_lists', methods=['GET'])
def get_grocery_lists():
    # Return all grocery items as a single list for now
    items = groceries.get_all_groceries()
    return {'lists': [{'name': 'Current Grocery List', 'items': items}]}

@app.route('/delete_grocery_item', methods=['POST'])
def delete_grocery_item():
    item_index = int(request.form['item_index'])
    groceries.delete_grocery_item(item_index)
    return redirect(url_for('index') + '#grocery')

@app.route('/add_rating', methods=['POST'])
def add_rating():
    recipe_name = request.form['recipe_name']
    rating = int(request.form['rating'])
    
    if 1 <= rating <= 5:
        success = recipes.add_rating(recipe_name, rating)
        if success:
            flash("Rating added successfully!", "success")
        else:
            flash("Failed to add rating.", "error")
    else:
        flash("Invalid rating. Please rate between 1 and 5 stars.", "error")
    
    return redirect(url_for('index') + '#view')

@app.route('/delete_recipe', methods=['POST'])
def delete_recipe():
    recipe_name = request.form.get('recipe_name', '')
    if recipe_name:
        success = recipes.delete_recipe(recipe_name)
        if success:
            flash(f"Recipe '{recipe_name}' deleted successfully!", "success")
        else:
            flash(f"Failed to delete recipe '{recipe_name}'.", "error")
    else:
        flash("No recipe specified for deletion.", "error")
    return redirect(url_for('index') + '#view')

@app.route('/scale_recipe', methods=['POST'])
def scale_recipe():
    recipe_name = request.form['recipe_name']
    factor = float(request.form['scale_factor'])

    recipe = get_recipe_by_name(recipe_name)
    if not recipe:
        flash("Recipe not found.")
        return redirect(url_for('index'))

    scaled_ingredients = []
    scaled_measurements = []

    for ing, meas in zip(recipe['ingredients'], recipe['measurements']):
        scaled = scale_measurement(meas, factor)
        scaled_measurements.append(scaled)
        scaled_ingredients.append(ing)  # ingredient stays the same

    recipe['measurements'] = scaled_measurements
    recipe['ingredients'] = scaled_ingredients
    recipe['servings'] = int(recipe['servings']) * factor

    update_recipe(
        old_name=recipe['name'],
        name=recipe['name'],
        ingredients=recipe['ingredients'],
        measurements=recipe['measurements'],
        mealType=recipe['mealType'],
        description=recipe['description'],
        servings=recipe['servings'],
        time=recipe['time'],
        numOfSteps=recipe['numOfSteps'],
        notes=recipe['notes'],
        freezerMealTF=recipe['freezerMealTF'],
        steps=recipe['steps']
    )

    flash(f"Scaled {recipe_name} by {factor}x.")
    return redirect(url_for('index'))

@app.route('/clear_grocery_list', methods=['POST'])
def clear_grocery_list():
    groceries.clear_all_groceries()
    return redirect(url_for('index') + '#grocery')

if __name__ == '__main__':
  app.run(host='0.0.0.0', port=3000)