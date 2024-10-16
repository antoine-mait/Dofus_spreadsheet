import requests
import os

class DofusResourcesFetcher:

    def __init__(self, base_url):
        self.base_url = base_url

    def get_resources(self, user_levelmin, user_levelmax):
        params = {
            "sort[level]": "asc",  
            "filter[min_level]": user_levelmin, 
            "filter[max_level]": user_levelmax
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

def main_resources():
    base_url = "https://api.dofusdu.de" 
    user_levelmin = 1
    user_levelmax = 200  

    fetcher = DofusResourcesFetcher(base_url)
    resources = fetcher.get_resources(user_levelmin, user_levelmax)
    fetcher.write_resources(resources)

if __name__ == "__main__":
    main_resources()