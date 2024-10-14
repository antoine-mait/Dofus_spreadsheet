import requests

base_url = "https://api.dofusdu.de"  # Confirm the correct base URL
user_levelmin = input('Choose min level : ')
user_levelmax = input('Choose min level : ')

def get_ressources(base_url, user_levelmin, user_levelmax ):
    # Parameters for sorting and filtering
    params = {
        "sort[level]": "asc",  # Sort by level in ascending order
        "filter[min_level]": user_levelmin,  # Minimum level of 50
        "filter[max_level]": user_levelmax  # Maximum level of 100
    }

    # Get items with the specified filters
    response = requests.get(f"{base_url}/dofus2/fr/items/resources/all", params=params)

    if response.status_code == 200:
        response_data = response.json()
        ressources = response_data['items']

        ressource_ids = [ressource['ankama_id'] for ressource in ressources]
        ressource_names = [ressource['name'] for ressource in ressources]
        ressource_types = [ressource['type']['name'] for ressource in ressources]
        ressource_levels = [ressource['level'] for ressource in ressources]
        ressource_images = [ressource['image_urls']['icon'] for ressource in ressources]
        ressource_descriptions = [ressource['description'] for ressource in ressources]

    else:
        print(f"Error: {response.status_code}, Message: {response.text}")

    for ressource in ressources:

            with open("RESSOURCES/RESSOURCES_Item.txt", "w", encoding='utf-8') as file:
                for ressource in ressources:
                    file.write(f"NAME : {ressource['name']}\n")
                    file.write(f"ID : {ressource['ankama_id']}\n")
                    file.write(f"TYPE : {ressource['type']['name']}\n")
                    file.write(f"LEVEL : {ressource['level']}\n")
                    file.write(f"IMAGE URL : {ressource['image_urls']['icon']}\n")
                    file.write(f"DESCRIPTION : {ressource['description']}\n")
                    file.write("\n")


if __name__ == "__main__":
    get_ressources(base_url,user_levelmin, user_levelmax)