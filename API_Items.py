import requests
import sys

class DofusItemFetcher:
    def __init__(self, base_url):
        self.base_url = base_url

    def get_item(self, item_type, level_min, level_max):
        params = {
            "sort[level]": "asc",
            "filter[type_enum]": item_type,
            "filter[min_level]": level_min,
            "filter[max_level]": level_max,
        }
        
        response = requests.get(f"{self.base_url}/dofus2/fr/items/equipment/all", params=params)
        if response.status_code == 200:
            return response.json().get("items", [])
        else:
            print(f"Error fetching items of type {item_type}: {response.status_code}, {response.text}")
            return []

    def write_items_to_file(self, items, item_type):
        if not items:
            print(f"No items to process for type {item_type}")
            return

        item_titles = [item['type']['name'] for item in items]
        item_title = item_titles[0].upper()
        try:
            with open(f"ITEMS/{item_title}_Item.txt", "w", encoding="utf-8") as file:
                for item in items:
                    self.write_item_details(file, item)
        except Exception as e:
            print(f"Error writing items to file: {e}")

    def write_item_details(self, file, item):
        file.write(f"NAME : {item['name']}\n")
        file.write(f"ID : {item['ankama_id']}\n")
        file.write(f"TYPE : {item['type']['name']}\n")
        file.write(f"LEVEL : {item['level']}\n")
        file.write(f"IMAGE URL : {item['image_urls']['icon']}\n")
        file.write(f"DESCRIPTION : {item['description']}\n")
        
        self.write_recipes(file, item.get("recipe", []))
        self.write_effects(file, item.get("effects", []))
        file.write(f"IS WEAPON: {item.get('is_weapon', False)}\n")

        if "parent_set" in item:
            file.write(f"PARENT SET ID: {item['parent_set']['id']}\n")
            file.write(f"PARENT SET NAME: {item['parent_set']['name']}\n")
        else:
            file.write("PARENT SET: None\n")

        file.write("\n")

    def write_recipes(self, file, recipes):
        if recipes:
            file.write("RECIPES:\n")
            for recipe in recipes:
                self.write_recipe(file, recipe)
        else:
            file.write("RECIPES: None\n")

    def write_recipe(self, file, recipe):
        recipe_id = recipe['item_ankama_id']
        name_id = self.find_resource_name(recipe_id)

        if name_id:
            file.write(f"  - ID: {recipe_id} / {name_id}, Quantity: {recipe['quantity']}\n")
        else:
            file.write(f"  - ID: {recipe_id}, Quantity: {recipe['quantity']}\n")

    def find_resource_name(self, recipe_id):
        previous_line = None
        with open("RESOURCES/RESOURCES_Item.txt", "r", encoding='utf-8') as resource_file:
            for line in resource_file:
                if f"ID : {recipe_id}" in line:
                    if previous_line and previous_line.startswith("NAME :"):
                        return previous_line.strip().replace("NAME :", "").strip()
                previous_line = line
        return None

    def write_effects(self, file, effects):
        if effects:
            file.write("EFFECTS:\n")
            for effect in effects:
                file.write(f"  - {effect['formatted']}\n")
        else:
            file.write("EFFECTS: None\n")

def main_item():
    base_url = "https://api.dofusdu.de"
    filter_check = False
    while not filter_check:
        user_filter = input("""Choose the filter:
hat
cloak
ring
amulet
sword
staff
wand
boots
shield
belt
trophy
prysmaradite
Dofus
pet
petsmount
or type 'all': """)
        if user_filter not in ["hat", "cloak", "ring", "amulet", "sword", "staff", 
                                "wand", "boots", "shield", "belt", "trophy", 
                                "prysmaradite", "Dofus", "pet", "petsmount", "all" ]:
            print("Wrong Filter")
        else:
            filter_check = True
    fetcher = DofusItemFetcher(base_url)
    if user_filter != "all":
        try:
            user_levelmin = int(input('Choose min level (1-199): '))
            user_levelmax = int(input('Choose max level (2-200): '))

            if user_levelmax < user_levelmin:
                sys.exit("Level Max can't be inferior to Level Min")
            if not (1 <= user_levelmin <= 199) or not (2 <= user_levelmax <= 200):
                sys.exit("Level Min must be between 1 and 199, and Level Max must be between 2 and 200.")
        except ValueError:
            sys.exit("Please enter valid integers for levels.")   

    elif user_filter == "all":
        user_levelmin = 1
        user_levelmax = 200
        item_types = [
                    "Amulet", "Ring", "Boots", "Shield", 
                    "Cloak", "Belt", "Hat", "Dofus", 
                    "Trophy", "Prysmaradite", "Pet", "Petsmount"
                     ]
        for item_type in item_types:
            items = fetcher.get_item(item_type, user_levelmin, user_levelmax)
            fetcher.write_items_to_file(items, item_type)
    else:
        items = fetcher.get_item(user_filter, user_levelmin, user_levelmax)
        fetcher.write_items_to_file(items, user_filter)

if __name__ == "__main__":
    main_item()
