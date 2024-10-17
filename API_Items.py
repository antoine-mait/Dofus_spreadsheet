import requests
import sys
import os 
import re

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
        
        if not os.path.exists("ITEMS"):
                os.makedirs("ITEMS")
                print(f"Directory {"ITEMS"} created.")

        item_titles = [item['type']['name'] for item in items]
        item_title = item_titles[0].upper()
        
        try:
            with open(f"ITEMS/{item_title}.txt", "w", encoding="utf-8") as file:
                for item in items:
                    self.write_item_details(file, item)
        except Exception as e:
            print(f"Error writing items to file: {e}")

    def write_item_details(self, file, item, ):
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
        self.download_item_image(item)

    def download_item_image(self, item):

        item_type = item['type']['name'].upper()
        directory_path = f"ITEMS/IMAGES/{item_type}"

        if not os.path.exists(directory_path):
                os.makedirs(directory_path)
                print(f"Directory {directory_path} created.")
        name = item['name']
        id = item['ankama_id']
        name_id = f"{name}_{id}"
        name_id = re.sub(r'[<>:"/\\|?*]', '_', name_id)
        image_path = f"{directory_path}/{name_id}.png"

        if not os.path.exists(image_path):
            try: 
                image_url = item['image_urls']['sd']
                response = requests.get(image_url)
                response.raise_for_status()
                with open(f"{directory_path}/{name_id}.png", "wb") as image_file:
                    image_file.write(response.content)
            except requests.exceptions.RequestException as e:
                print(f"Error downloading image: {e}")

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

def main_item(filter_check=False):
    base_url = "https://api.dofusdu.de"
    fetcher = DofusItemFetcher(base_url)

    if not filter_check:
        while True:
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
                break

    if filter_check == True:
        user_filter = "all"
    if filter_check and user_filter.lower() != "all":
        try:
            level_min = int(input('Choose min level (1-199): '))
            level_max = int(input('Choose max level (2-200): '))

            if level_max < level_min:
                sys.exit("Level Max can't be inferior to Level Min")
            if not (1 <= level_min <= 199) or not (2 <= level_max <= 200):
                sys.exit("Level Min must be between 1 and 199, and Level Max must be between 2 and 200.")
        except ValueError:
            sys.exit("Please enter valid integers for levels.")   

    elif filter_check or user_filter.lower() == "all":
        level_min = 1
        level_max = 200
        item_types = [
                    "Amulet", "Ring", "Boots", "Shield", 
                    "Cloak", "Belt", "Hat", "Dofus", 
                    "Trophy", "Prysmaradite", "Pet", "Petsmount"
                     ]
        for item_type in item_types:
            items = fetcher.get_item(item_type, level_min, level_max)
            fetcher.write_items_to_file(items, item_type)
    else:
        items = fetcher.get_item(user_filter, level_min, level_max)
        fetcher.write_items_to_file(items, user_filter)

if __name__ == "__main__":
    main_item()
