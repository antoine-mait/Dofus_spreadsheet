import requests
import os
import re
import sys

class DofusResourcesFetcher:

    def __init__(self, base_url):
        self.base_url = base_url

    def get_resources(self, level_min, level_max):
        params = {
            "sort[level]": "asc",  
            "filter[min_level]": level_min, 
            "filter[max_level]": level_max
                }

        response = requests.get(f"{self.base_url}/dofus2/fr/items/resources/all", params=params)
        if response.status_code == 200:
            return response.json().get("items", [])
        else:
            print(f"Error: {response.status_code}, Message: {response.text}")
            return []
              
    def write_resources(self, resources):
        if not os.path.exists("RESOURCES"):
                os.makedirs("RESOURCES")
                print(f"Directory {"RESOURCES"} created.")

        if resources:
            with open("RESOURCES/RESOURCES_Item.txt", "w", encoding='utf-8') as file:
                for resource in resources:
                    file.write(f"NAME : {resource['name']}\n")
                    file.write(f"ID : {resource['ankama_id']}\n")
                    file.write(f"TYPE : {resource['type']['name']}\n")
                    file.write(f"LEVEL : {resource['level']}\n")
                    file.write(f"IMAGE URL : {resource['image_urls']['icon']}\n")
                    file.write(f"DESCRIPTION : {resource['description']}\n")
                    file.write("\n")
                    self.download_item_image(resource)

    def download_item_image(self, resources):

        item_type = resources['type']['name'].upper()
        directory_path = f"RESOURCES/IMAGES/{item_type}"

        if not os.path.exists(directory_path):
                os.makedirs(directory_path)
                print(f"Directory {directory_path} created.")

        name = resources['name']
        id = resources['ankama_id']
        name_id = f"{name}_{id}"
        name_id = re.sub(r'[<>:"/\\|?*]', '_', name_id)
        image_path = f"{directory_path}/{name_id}.png"

        if not os.path.exists(image_path):
            try: 
                image_url = resources['image_urls']['sd']
                response = requests.get(image_url)
                response.raise_for_status()
                with open(f"{directory_path}/{name_id}.png", "wb") as image_file:
                    image_file.write(response.content)
                    print(f"Download Image : {directory_path}/{name_id}.png")
            except requests.exceptions.RequestException as e:
                print(f"Error downloading image: {e}")


def main_resources(filter_check=False):
    base_url = "https://api.dofusdu.de" 
    if not filter_check:
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

    else:
        level_min = 1
        level_max = 200

    fetcher = DofusResourcesFetcher(base_url)
    resources = fetcher.get_resources(level_min, level_max)
    fetcher.write_resources(resources)

if __name__ == "__main__":
    main_resources()