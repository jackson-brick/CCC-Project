from urllib.request import urlopen
from bs4 import BeautifulSoup
import json

#https://realpython.com/python-web-scraping-practical-introduction/

measurement_types = ["cup", "cups", "teaspoon", "teaspoons", "tsp", "tablespoon", "tablespoons", "tbsp", "ounce", "ounces", "oz", "pound", "pounds", "lb", "lbs", "gram", "grams", "g", "milliliter", "milliliters", "ml", "liter", "liters", "l", "pint", "pints", "pt", "quart", "quarts", "qt", "gallon", "gallons", "gal", "fluid ounce", "fluid ounces", "fl oz", "pinch", "pinches", "dash", "dashes", "drop", "drops", "kilogram", "kilograms", "kg", "milligram", "milligrams", "mg"]



def scrape(url):
  page = urlopen(url)
  html_bytes = page.read()
  html = html_bytes.decode("utf-8")
  soup = BeautifulSoup(html,"html.parser")
  
  soupList_raw = soup.get_text().split("\n")
  soupList = []
  
  for i in range(len(soupList_raw)):
    if soupList_raw[i] == "" or soupList_raw[i] == " ":
      pass
    else:
      soupList.append(soupList_raw[i])
  
  counter = []
  for i in soupList:
    try:
      if i.split(" ")[0].isdigit() and "Photo" in i.split(" ")[1]:
        counter.append(i)
    except:
      pass
  
  
  
  title = soupList[0]
  ingredients = []
  measurements = []
  instructions = []
  description = soupList[soupList.index(counter[0]) + 1]
  for i in soupList[soupList.index("Oops! Something went wrong. Our team is working on it.") + 3:soupList.index("Directions")]: 
    try:
      if i.split(" ")[1] in measurement_types:
        measurements.append("".join(i.split(" ")[0] + " " + i.split(" ")[1]))
        ingredients.append(" ".join(i.split(" ")[2:]))
      elif i.split(" ")[2] in measurement_types:
        measurements.append("".join(i.split(" ")[0] + " " + i.split(" ")[1] + " " + i.split(" ")[2]))
        ingredients.append(" ".join(i.split(" ")[3:]))
      else:
        if i.split(" ")[0].isdigit():
          measurements.append("".join(i.split(" ")[0]))
          ingredients.append((" ".join(i.split(" ")[1:])))
        else:
          measurements.append("")
          ingredients.append(i)
    except IndexError:
      while True:
        print(f"Is {i} an ingredient? Type yes/y if it should be added or no/n if it is not an ingredient.")
        yesOrNo = input()
        if yesOrNo.lower() == "yes" or yesOrNo.lower() == "y":
          measurements.append("")
          ingredients.append(i)
          break
        elif yesOrNo.lower() == "no" or yesOrNo.lower() == "n":
          break
  
  for i in soupList[soupList.index("Directions") + 1:soupList.index(" I Made It")-2]:
    instructions.append(i.strip())
  
  servings = soupList[soupList.index("Servings:") + 1]
  time = soupList[soupList.index("Total Time:") + 1]
  numOfSteps = len(instructions)



  return [title, ingredients, measurements, "Unknown", description, servings, time, numOfSteps, "", "False",instructions]
