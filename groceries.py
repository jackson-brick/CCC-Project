import csv
import os

groceriesFile = './data/groceryList.csv'
FIELDNAMES = ['item', 'amount', 'store', 'type']

# Add grocery items (list of items with all 4 fields)
def add_grocery(items):  
    groceries = []

    # Read existing groceries if file exists
    if os.path.exists(groceriesFile):
        with open(groceriesFile, 'r', newline='') as file:
            reader = csv.DictReader(file)
            groceries = list(reader)

    # Append new items
    for i in items:
        groceries.append({
            'item': i.get('item', ''),
            'amount': i.get('quantity', ''),
            'store': i.get('store', ''),
            'type': i.get('type', '')
        })

    # Write back to file
    with open(groceriesFile, 'w', newline='') as file:
        writer = csv.DictWriter(file, fieldnames=FIELDNAMES)
        writer.writeheader()
        writer.writerows(groceries)

# Read and return all grocery items
def get_all_groceries():
    if not os.path.exists(groceriesFile):
        return []

    with open(groceriesFile, 'r', newline='') as file:
        reader = csv.DictReader(file)
        return list(reader)

# Delete a grocery item by index
def delete_grocery_item(item_index):
    groceries = get_all_groceries()
    
    if 0 <= item_index < len(groceries):
        del groceries[item_index]
        
        # Write back to file
        with open(groceriesFile, 'w', newline='') as file:
            writer = csv.DictWriter(file, fieldnames=FIELDNAMES)
            writer.writeheader()
            writer.writerows(groceries)

def clear_all_groceries():
    # Clear the grocery CSV file or DB table; implementation depends on your storage
    with open('./data/groceryList.csv', 'w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(['item', 'quantity', 'store', 'type'])  # write only header