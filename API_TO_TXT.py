import os
import re
import sys
import time
import logging
import requests
import concurrent.futures
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from dotenv import load_dotenv

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
logging.getLogger("urllib3").setLevel(logging.DEBUG)  # To capture urllib3 retry logs

load_dotenv()
DOFUS_API = os.environ.get("DOFUS_API")

class DofusItemFetcher:
    '''Fetches and processes item data from the Dofus API.

    This class provides methods for retrieving items of specified categories 
    and types, writing them to files, and downloading their images. 
    Multithreading is utilized for efficiency, especially in writing and 
    downloading operations.
    '''
    def __init__(self, base_url):
        self.base_url = base_url
        self.session = requests.Session()
        # Retry strategy with logging for each retry event
        retry_strategy = Retry(
            total=10,                    # Total number of retries
            backoff_factor=1,         # Delay factor for retries
            status_forcelist=[429, 500, 502, 503, 504],  # Retry on these HTTP codes
            allowed_methods=["GET"],     # Retry only for GET requests
            raise_on_status=False
        )
        
        # Create session and mount it with the retry adapter
        self.session = requests.Session()
        adapter = HTTPAdapter(max_retries=retry_strategy, pool_connections=50, pool_maxsize=50)
        self.session.mount("http://", adapter)
        self.session.mount("https://", adapter)

    def get_item(self,categorie, item_type, level_min, level_max):
        """
        Fetch items of a specific category and type from the Dofus API.
        
        Parameters:
            categorie (str): The category of items to fetch (e.g., 'equipment', 'mounts').
            item_type (str): The specific type of item within the category (e.g., 'Amulet').
            level_min (int): The minimum level of items to fetch.
            level_max (int): The maximum level of items to fetch.
            
        Returns:
            list: List of items if the request is successful, empty list otherwise.
            None: If the API request fails (logs an error message).
        """
        params = {
                "sort[level]": "asc",
                "filter[min_level]": level_min,
                "filter[max_level]": level_max,
                }   
        if categorie in ["equipment", "mounts"]:
            params["filter[type_enum]"] = item_type
        url = (f"{self.base_url}/dofus2/fr/{categorie}/all" 
               if categorie == "mounts" 
               else f"{self.base_url}/dofus2/fr/items/{categorie}/all")
        try :
            response = self.session.get(url, params=params)
            response.raise_for_status()  # Raises HTTPError if the status is 4xx or 5xx
             # Return the appropriate data
            if categorie == "mounts":
                return response.json().get("mounts", [])
            else : 
                return response.json().get("items", [])
        except requests.RequestException as e:
            print(f"Error fetching items of type {item_type}: {e}")
            return None

    def write_items_to_file(self,categorie, items, item_type):
        '''Writes the obtained data into a text file'''
        if not items:
            print(f"No items found for {categorie} type '{item_type}'. Skipping...")
            return

        dir_path = os.path.join("API_TO_TXT", categorie.upper())
        os.makedirs(dir_path, exist_ok=True)

        file_path = os.path.join(dir_path, f"{item_type.upper()}.txt")
        try:
            with open(file_path, "w", encoding="utf-8") as file:
                for item in items:
                    self.write_item_details(categorie, file, item)

            print(f"TXT file '{file_path}' created.")

        except Exception as e:
            print(f"Error writing items to file for {categorie}: {e}")

    def download_item_image(self, categorie, item):
        '''Download all the img from the API here, the SD quality is downloaded'''
        dir_path = os.path.join("API_TO_TXT", categorie.upper(), "IMAGES")
        os.makedirs(dir_path, exist_ok=True)

        # Directory path setup
        if categorie == "mounts":
            item_type = item['family_name'].upper()
        elif categorie == "equipment":
            item_type = item['type']['name'].upper()

        if categorie in ["resources","consumables"]:
            directory_path = dir_path
        else:
            directory_path = os.path.join(dir_path, item_type)
        os.makedirs(directory_path, exist_ok=True)

        # Setup image name
        name_id = re.sub(r'[<>:"/\\|?*]', '_', f"{item['name']}_{item['ankama_id']}")
        image_path = os.path.join(directory_path, f"{name_id}.png")

        if not os.path.exists(image_path):
            try:
                # Download SD quality , can be change for ICON (200pixel), HQ or HD (600/800pixel)
                image_url = item['image_urls']['sd']

                # Log each attempt and add delay
                if categorie in ["mounts","equipment"]:
                    time.sleep(0.5) 

                response = requests.get(image_url)
                response.raise_for_status()

                with open(image_path, "wb") as image_file:
                    image_file.write(response.content)
                print(f"Image '{name_id}' saved.")
                

            except requests.RequestException as e:
                print(f"Error downloading image for {item['name']}: {e}")
                
    
    def write_item_details(self,categorie, file, item):
        '''Format the writing in the Text file'''
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

    def write_recipes(self, file, recipes):
        '''Write the resources name'''
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
        '''Get the resources name from their ID'''
        with open("API_TO_TXT/RESOURCES/RESOURCES.txt", "r", encoding='utf-8') as resource_file:
            previous_line = None
            for line in resource_file:
                if f"ID : {recipe_id}" in line:
                    if previous_line and previous_line.startswith("NAME :"):
                        return previous_line.strip().replace("NAME :", "").strip()
                previous_line = line
        return None

    def write_effects(self, file, effects):
        '''Write the object effect'''
        if effects:
            file.write("EFFECTS:\n")
            for effect in effects:
                file.write(f"  - {effect['formatted']}\n")
        else:
            file.write("EFFECTS: None\n")

def api_to_txt():
    '''Set a .env file with the API ( follow the README file )'''
    base_url = DOFUS_API
    if DOFUS_API is None:
        print("DOFUS_API environment variable not set!")
        sys.exit(1)
    try:
        fetcher = DofusItemFetcher(base_url)

        written_categories = set()
        for categorie in ["resources","equipment","consumables","mounts"]:
            if categorie in ["resources", "consumables"] and categorie in written_categories:
                print(f"Files for {categorie} have already been written. Skipping...")
                continue
            level_min = 1
            level_max = 200
            # Set up the Item Type. Look into the API or IN Game for the correct Item type name and add/remove it
            if categorie == "equipment":
                types = [
                            "Amulet", "Ring", "Boots", "Shield", 
                            "Cloak", "Belt", "Hat", "Dofus", 
                            "Trophy", "Prysmaradite", "Pet", "Petsmount"
                            ]
            if categorie == "mounts":
                types = [
                                "Dragodinde",
                                "Muldo",
                                "Volkorne"
                                ]
            if categorie == "consumables":
                types = ["consumables"]
            if categorie == "resources":
                types = ["resources"]
            '''MultiThreading the Class for faster writing and downloading process'''
            with concurrent.futures.ThreadPoolExecutor() as executor:
                futures = [
                    executor.submit(fetch_and_write, categorie, item_type, level_min, level_max, fetcher)
                    for item_type in types
                ]
                
                # Wait for all threads to complete
                concurrent.futures.wait(futures)
            if categorie in ["resources","consumables"]:
                written_categories.add(categorie)
                
    except KeyboardInterrupt:
        print("\nScript stopped with Ctrl + C.")

def fetch_and_write(categorie, item_type, level_min, level_max, fetcher):

    items = fetcher.get_item(categorie,item_type, level_min, level_max)
    fetcher.write_items_to_file(categorie,items, item_type)
    for item in items:
        fetcher.download_item_image(categorie, item)
    # Slowdown to not overflow the API wih request
    time.sleep(1)

if __name__ == "__main__":
    try:
        api_to_txt()
    except KeyboardInterrupt:
        print("\nScript stopped with Ctrl + C.")