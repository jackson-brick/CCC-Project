from flask import Flask, request, render_template, redirect, url_for
import recipes
import groceries
import mealPlanner
import importlib
import csv
import json

importlib.reload(recipes)

app = Flask(__name__)

app.jinja_env.globals.update(zip=zip)


@app.route('/')
def index():
  return redirect(url_for('view_recipes'))

  

@app.route('/view_recipes')
def view_recipes():
    rec = recipes.get_recipes()

    with open('./data/mealPlan.csv', 'r') as file:
      reader = csv.DictReader(file)
      meal_plan_raw = list(reader)[0]

    meal_plan = {}
    for day, val in meal_plan_raw.items():
      try:
          meal_plan[day] = json.loads(val)
      except json.JSONDecodeError as e:
          print(f"Error decoding JSON for {day}: {val}")
          meal_plan[day] = ["", "", ""]  # fallback default
    return render_template('index.html', recipes=rec, meal_plan=meal_plan)

@app.route('/submit', methods=['POST'])
def submit():
  name = request.form['name']
  ingredients = [i.strip() for i in request.form.getlist('ingredients') if i.strip()]
  measurements = [m.strip() for m in request.form.getlist('measurements') if m.strip()]
  steps = [s.strip() for s in request.form.getlist('steps') if s.strip()]

  if len(ingredients) != len(measurements):
      return "Ingredient and measurement count mismatch", 400
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
def planner():
  day = request.form["day"]
  meal = request.form["meal"]  # breakfast/lunch/dinner
  recipe = request.form["recipe"]
  mealPlanner.add_meal(day, meal, recipe)
  return redirect(url_for("index") + '#view')

@app.route('/clear_day', methods=['POST'])
def clear_day():
    day = request.form['day'].lower()

    with open('./data/mealPlan.csv', 'r') as file:
        reader = csv.DictReader(file)
        meal_plan = list(reader)[0]

    meal_plan[day] = json.dumps(["", "", ""])  # Clear all 3 meals

    with open('./data/mealPlan.csv', 'w', newline='') as file:
        writer = csv.DictWriter(file, fieldnames=meal_plan.keys())
        writer.writeheader()
        writer.writerow(meal_plan)

    return redirect(url_for('index') + '#meal')

@app.route('/reset_week', methods=['POST'])
def reset_week():
    initial_meal_plan = {
        "monday": json.dumps(["", "", ""]),
        "tuesday": json.dumps(["", "", ""]),
        "wednesday": json.dumps(["", "", ""]),
        "thursday": json.dumps(["", "", ""]),
        "friday": json.dumps(["", "", ""]),
        "saturday": json.dumps(["", "", ""]),
        "sunday": json.dumps(["", "", ""]),
    }

    with open('./data/mealPlan.csv', 'w', newline='') as file:
        writer = csv.DictWriter(file, fieldnames=initial_meal_plan.keys())
        writer.writeheader()
        writer.writerow(initial_meal_plan)
    return redirect(url_for('index') + '#meal')

@app.route('/add_grocery', methods=['POST'])
def grocery():
    item = [i.strip() for i in request.form.getlist('item') if i.strip()]
    amount = [i.strip() for i in request.form.getlist('amount') if i.strip()]
    store = [i.strip() for i in request.form.getlist('store') if i.strip()]
    groceries.add_grocery(item, amount, store)
    return redirect(url_for('index') + '#grocery')
    

if __name__ == '__main__':
  app.run(host='0.0.0.0', port=3000)