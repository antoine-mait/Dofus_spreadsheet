import requests
import os
import re

class DofusMountfetcher:
    def __init__(self, base_url):
        self.base_url = base_url

    def get_mount(self, user_filter):
        params = {
            "sort[level]": "asc",
            "filter[type_enum]": user_filter,
        }

        response = requests.get(f"{self.base_url}/dofus2/fr/mounts/all", params=params)
        if response.status_code == 200:
            return response.json().get("mounts", [])
        else:
            print(f"Error fetching items of type {user_filter}: {response.status_code}, {response.text}")
            return []

    def write_mount_to_file(self, mounts, mount_type):
        if not mounts:
            print(f"No items to process for type {mount_type}")
            return
        
        mount_title = mount_type.upper()
        if not os.path.exists("MOUNTS"):
                os.makedirs("MOUNTS")
                print(f"Directory {"MOUNTS"} created.")
        try:
            with open(f"MOUNTS/{mount_title}.txt", "w", encoding='utf-8') as file:
                for mount in mounts:
                    self.write_details(file, mount, mount_type)
        except Exception as e:
            print(f"Error writing items to file: {e}")
            
    def write_details(self, file, mount, user_filter):
        if mount['family_name'].capitalize() == user_filter.capitalize():
            file.write(f"NAME : {mount['name']}\n")
            file.write(f"ID : {mount['ankama_id']}\n")
            file.write(f"IMAGE URL : {mount['image_urls']['icon']}\n")
            self.write_effects(file, mount.get("effects", ))
            file.write("\n")
            
            self.download_item_image(mount)

    def download_item_image(self, mount):
        
        item_type = mount['family_name'].upper()
        directory_path = f"MOUNTS/IMAGES/{item_type}"
        if not os.path.exists(directory_path):
                os.makedirs(directory_path)
                print(f"Directory {directory_path} created.")
        name = mount['name']
        id = mount['ankama_id']
        name_id = f"{name}_{id}"
        name_id = re.sub(r'[<>:"/\\|?*]', '_', name_id)
        image_path = f"{directory_path}/{name_id}.png"

        if not os.path.exists(image_path):
            try: 
                image_url = mount['image_urls']['sd']
                response = requests.get(image_url)
                response.raise_for_status()
                with open(f"{directory_path}/{name_id}.png", "wb") as image_file:
                    image_file.write(response.content)
            except requests.exceptions.RequestException as e:
                print(f"Error downloading image: {e}")

    def write_effects(self, file, effects):
        if effects:
            file.write("EFFECTS:\n")
            for effect in effects:
                file.write(f"  - {effect['formatted']}\n")
        else:
            file.write("EFFECTS: None\n")
        

def main_mount(filter_check=False):
    base_url = "https://api.dofusdu.de" 
    fetcher = DofusMountfetcher(base_url)

    if not filter_check:
        while True:
            user_filter = input("""Choose the filter:
dragodinde
muldo
volkorne
or type 'all': """)
            if user_filter not in ["dragodinde", "muldo", "volkorne", "all"]:
                print("Wrong Filter")
            else:
                filter_check = True
                break

    if filter_check == True :
        user_filter = "all"
    if user_filter == "all":
        mounts_types = [
            "dragodinde",
            "muldo",
            "volkorne"
            ]
        for mount_type in mounts_types:
            mount = fetcher.get_mount(mount_type)
            fetcher.write_mount_to_file(mount, mount_type)
    else:
        mount = fetcher.get_mount(user_filter)
        fetcher.write_mount_to_file(mount, user_filter)
    

if __name__ == "__main__":
    main_mount()
