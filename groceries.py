import csv

def add_grocery(item, amount, store):
  with open('./data/groceryList.csv', 'r') as file:
    reader = csv.DictReader(file)
    groceries = list(reader)

  for i in item:
    groceries.append({'item': i, 'amount': amount, 'store': store})