import requests
import os
import re
import sys
import time
import concurrent.futures
from dotenv import load_dotenv

load_dotenv()
DOFUS_API = os.environ.get("DOFUS_API")

class DofusItemFetcher:
    def __init__(self, base_url):
        self.base_url = base_url

    def get_item(self,categorie, item_type, level_min, level_max):

        params = {
                "sort[level]": "asc",
                "filter[min_level]": level_min,
                "filter[max_level]": level_max,
                }   
        if categorie in ["equipment", "mounts"]:
            params["filter[type_enum]"] = item_type

        response = requests.get(f"{self.base_url}/dofus2/fr/items/{categorie}/all", params=params)
        if response.status_code == 200:
            return response.json().get("items", [])            
        else:
            print(f"Error fetching items of type {item_type}: {response.status_code}, {response.text}")
            return

    def write_items_to_file(self,categorie, items, item_type):

        if not items:
            print(f"No items found for {categorie} type '{item_type}'. Skipping...")
            return
        
        dir_path = os.path.join("API_TO_TXT", categorie.upper())
        os.makedirs(dir_path, exist_ok=True)

        """Write .TXT if it doesn't exist"""

        if categorie in ["equipment", "mounts"]:
            
            item_title = item_type.upper()
            file_path = os.path.join(dir_path, f"{item_title}.txt")
            try:
                with open(file_path, "w", encoding="utf-8") as file:
                    with concurrent.futures.ThreadPoolExecutor() as executor:
                            futures = []
                            for item in items:
                                futures.append(executor.submit(self.write_item_details, categorie, file, item))
                                futures.append(executor.submit(self.download_item_image, categorie, item))
                            # Ensure all tasks are completed
                            concurrent.futures.wait(futures)
                print(f"TXT file '{file_path}' created.")
            except Exception as e:
                print(f"Error writing items to file for {categorie}: {e}")
        else:
            file_path = os.path.join(dir_path, f"{categorie}.txt")
            if not os.path.exists(dir_path):
                try:
                    with open(file_path, "w", encoding="utf-8") as file:
                        for item in items:
                            self.write_item_details(categorie, file, item)
                    print(f"TXT file '{file_path}' created.")
                except Exception as e:
                    print(f"Error writing items to file for {categorie}: {e}")

        
    def write_item_details(self,categorie, file, item):
        file.write("\n")
        if categorie == "mounts":
            file.write(f"NAME : {item['name']}\n")
            file.write(f"ID : {item['ankama_id']}\n")
            file.write(f"IMAGE URL : {item['image_urls']['sd']}\n")
            self.write_effects(file, item.get("effects", ))
        elif categorie == "resources":
            file.write(f"NAME : {item['name']}\n")
            file.write(f"ID : {item['ankama_id']}\n")
            file.write(f"TYPE : {item['type']['name']}\n")
            file.write(f"LEVEL : {item['level']}\n")
            file.write(f"IMAGE URL : {item['image_urls']['sd']}\n")
            file.write(f"DESCRIPTION : {item['description']}\n")
        else:
            file.write(f"NAME : {item['name']}\n")
            file.write(f"ID : {item['ankama_id']}\n")
            file.write(f"TYPE : {item['type']['name']}\n")
            file.write(f"LEVEL : {item['level']}\n")
            file.write(f"IMAGE URL : {item['image_urls']['sd']}\n")
            file.write(f"DESCRIPTION : {item['description']}\n")
            self.write_recipes(file, item.get("recipe", []))
            self.write_effects(file, item.get("effects", []))
            file.write(f"IS WEAPON: {item.get('is_weapon', False)}\n")

            if "parent_set" in item:
                file.write(f"PARENT SET ID: {item['parent_set']['id']}\n")
                file.write(f"PARENT SET NAME: {item['parent_set']['name']}\n")
            else:
                file.write("PARENT SET: None\n")

        self.download_item_image(categorie,item)

    def download_item_image(self,categorie, item):
        dir_path = os.path.join("API_TO_TXT", categorie.upper(),"IMAGES")
        item_type = item['type']['name'].upper()
        os.makedirs(dir_path, exist_ok=True)

        if categorie in ["resources","consumables"]:
            directory_path = dir_path
        else:
            directory_path = os.path.join(dir_path,item_type)
            
        os.makedirs(directory_path, exist_ok=True)

        name = item['name']
        id = item['ankama_id']
        name_id = f"{name}_{id}"
        name_id = re.sub(r'[<>:"/\\|?*]', '_', name_id)
        image_path = os.path.join(directory_path, f"{name_id}.png")
        if not os.path.exists(image_path):
            try:
                image_url = item['image_urls']['sd']
                response = requests.get(image_url)
                response.raise_for_status()
                with open(image_path, "wb") as image_file:
                    image_file.write(response.content)
                print(f"Image '{name_id}' saved.")
            except requests.RequestException as e:
                print(f"Error downloading image for {name}: {e}")
    time.sleep(2.5)

    def write_recipes(self, file, recipes):
        if recipes:
            file.write("RECIPES:\n")
            for recipe in recipes:
                recipe_id = recipe['item_ankama_id']
                name_id = self.find_resource_name(recipe_id)

                if name_id:
                    file.write(f"  - ID: {recipe_id} / {name_id}, Quantity: {recipe['quantity']}\n")
                else:
                    file.write(f"  - ID: {recipe_id}, Quantity: {recipe['quantity']}\n")
        else:
            file.write("RECIPES: None\n")


    def find_resource_name(self, recipe_id):
        with open("API_TO_TXT/RESOURCES/resources.txt", "r", encoding='utf-8') as resource_file:
            previous_line = None
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
    base_url = DOFUS_API
    if DOFUS_API is None:
        print("DOFUS_API environment variable not set!")
        sys.exit(1)

    fetcher = DofusItemFetcher(base_url)

    written_categories = set()
    #["resources","equipment","consumables"
    for categorie in ["mounts"]:
        if categorie in ["resources", "consumables"] and categorie in written_categories:
            print(f"Files for {categorie} have already been written. Skipping...")
            continue
        level_min = 1
        level_max = 200
        if categorie == "equipment":
            types = [
                        "Amulet", "Ring", "Boots", "Shield", 
                        "Cloak", "Belt", "Hat", "Dofus", 
                        "Trophy", "Prysmaradite", "Pet", "Petsmount"
                        ]
        if categorie == "mounts":
            types = [
                            "dragodinde",
                            "muldo",
                            "volkorne"
                            ]
        if categorie == "consumables":
            types = ['Bouataklône', "Pierre d'âme", 'Cadeau', 'Document', 
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
        if categorie == "resources":
            types = ["Emballage", "Cuir", "Clef", "Rune de forgemagie", "Bourgeon",
                    "Rabmablague", "Planche", "Caution", "Plume", "Bois",
                    "Laine", "Gravure de forgemagie", "Fleur", "Pierre brute",
                    "Aile", "Huile", "Minerai", "Peau", "Substrat",
                    "Métaria", "Galet", "Vêtement", "Souvenir", "Liquide",
                    "Rune de transcendance", "Champignon", "Fruit", "Alliage",
                    "Ressources de Temporis", "Essence de gardien de donjon", "Haïku",
                    "Teinture", "Coquille", "Racine", "Oreille", "Pierre précieuse",
                    "Ressource de combat", "Fragment de carte", "Poudre", "Écorce",
                    "Carapace", "Peluche", "Œuf", "Potion de forgemagie",
                    "Ressources des Anomalies Temporelles", "Matériel d'alchimie",
                    "Sève", "Nourriture pour familier", "Ressources des Songes",
                    "Nowel", "Gelée", "Patte", "Viande", "Rune astrale",
                    "Plante", "Céréale", "Poil", "Œil", "Orbe de forgemagie",
                    "Ressources diverses", "Préparation", "Ressources de Percepteur",
                    "Légume", "Graine", "Matériel d'exploration", "Carte",
                    "Os", "Queue", "Poisson", "Étoffe"
                    ]
        for item_type in types:
            items = fetcher.get_item(categorie,item_type, level_min, level_max)
            fetcher.write_items_to_file(categorie,items, item_type)
        if categorie in ["resources","consumables"]:
            written_categories.add(categorie)

if __name__ == "__main__":
    main_item()
    