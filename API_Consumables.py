import requests
import os
import sys

class DofusConsumableFetcher:
    def __init__(self, base_url):
        self.base_url = base_url

    def get_item(self, level_min, level_max):
        params = {
            "sort[level]": "asc",
            "filter[min_level]": level_min,
            "filter[max_level]": level_max,
        }
        response = requests.get(f"{self.base_url}/dofus2/fr/items/consumables/all", params=params)
        if response.status_code == 200:
            return (response.json().get("items", []))
        
        else:
            print(f"Error fetching items of type: {response.status_code}, {response.text}")
            return []

    def write_items_to_file(self, items, consumable_type):
        if not items:
            print(f"No items to process for type {consumable_type}")
            return
        
        if not os.path.exists("CONSUMABLE"):
                os.makedirs("CONSUMABLE")
                print(f"Directory {"CONSUMABLE"} created.")
        
        filtered_items = [item for item in items if item['type']['name'] == consumable_type]

        try:
            with open(f"CONSUMABLE/{consumable_type}.txt", "w", encoding="utf-8") as file:
                for item in filtered_items:
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

def main_consumable():
    base_url = "https://api.dofusdu.de"
    filter_check = False
    user_filter = input("Specific level or 'all' ? ")
    if user_filter != "all":
        try:
            level_min = int(input('Choose min level (1-199): '))
            level_max = int(input('Choose max level (2-200): '))

            if level_max < level_min:
                sys.exit("Level Max can't be inferior to Level Min")
            if not (1 <= level_min <= 199) or not (2 <= level_max <= 200):
                sys.exit("Level Min must be between 1 and 199, and Level Max must be between 2 and 200.")
        except ValueError:
            sys.exit("Please enter valid integers for levels.")
    
    elif user_filter.lower() == "all":
        level_min = 1
        level_max = 200

    consumable_types = ['Bouataklône', "Pierre d'âme", 'Cadeau', 'Document', 
                        'Figurine', 'Sac de ressources', 'Filet de capture', 
                        "Parchemin d'ornement", 'Objet utilisable de Temporis', 
                        "Pierre d'âme pleine", 'Bourse', "Parchemin d'attitude", 
                        'Viande primitive', 'Tatouage de la Foire du Trool', 
                        'Parchemin de sortilège', 'Potion', 'Mots de haïku', 
                        'Potion de téléportation', 'Boîte de fragments', 'Ballon', 
                        'Pierre magique', 'Friandise', 'Pain', 'Parchemin de caractéristique', 
                        'Conteneur', 'Objet de dons', 'Poisson comestible', 'Parchemin de titre', 
                        'Viande comestible', "Objet d'élevage", 'Prisme', "Fée d'artifice", "Potion d'attitude", 
                        'Potion de monture', 'Popoche de Havre-Sac', "Parchemin d'émoticônes", 
                        'Objet utilisable', 'Objet de mission', "Parchemin d'expérience", 'Mimibiote', 
                        'Ressources obsolètes', 'Boisson', "Relique d'Incarnation", 'Bière', 'Coffre', 
                        'Potion de conquête', 'Monture domptée']

    fetcher = DofusConsumableFetcher(base_url)
    items = fetcher.get_item(level_min, level_max)  # Fetch items only once
    for consumable_type in consumable_types:  
        fetcher.write_items_to_file(items, consumable_type)
        
if __name__ == "__main__":
    main_consumable()
