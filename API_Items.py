import requests

base_url = "https://api.dofusdu.de"  # Confirm the correct base URL
user_filter = input('Choose the filter(hat/cape/ring/amulet/sword/staff/wand) :')
user_levelmin = input('Choose min level : ')
user_levelmax = input('Choose min level : ')

def get_item(base_url, user_filter,user_levelmin, user_levelmax):
    
    params = {
        "sort[level]": "asc",  # Sort by level in ascending order
        "filter[type_enum]": user_filter,  # Filter for items of type "hat"
        "filter[min_level]": user_levelmin,  # Minimum level of 50
        "filter[max_level]": user_levelmax  # Maximum level of 100
    }

    # Get items with the specified filters
    response = requests.get(f"{base_url}/dofus2/fr/items/equipment/all", params=params)

    if response.status_code == 200:
        response_data = response.json()
        items = response_data['items']

        item_ids = [item['ankama_id'] for item in items]
        item_names = [item['name'] for item in items]
        item_types = [item['type']['name'] for item in items]
        item_levels = [item['level'] for item in items]
        item_images = [item['image_urls']['icon'] for item in items]
        item_descriptions = [item['description'] for item in items]

        item_recipes = [item.get('recipe', []) for item in items]
        item_effects = [item.get('effects', []) for item in items]
        item_weapons = [item.get('is_weapon', False) for item in items]
        item_set_ids = [item['parent_set']['id'] for item in items if 'parent_set' in item]
        item_set_names = [item['parent_set']['name'] for item in items if 'parent_set' in item]

    else:
        print(f"Error: {response.status_code}, Message: {response.text}")


    user_filter = user_filter.upper()
    with open(f"ITEMS/{user_filter}_Item.txt", "w", encoding='utf-8') as file:
        for item in items:
            file.write(f"NAME : {item['name']}\n")
            file.write(f"ID : {item['ankama_id']}\n")
            file.write(f"TYPE : {item['type']['name']}\n")
            file.write(f"LEVEL : {item['level']}\n")
            file.write(f"IMAGE URL : {item['image_urls']['icon']}\n")
            file.write(f"DESCRIPTION : {item['description']}\n")

            recipes = item.get('recipe', [])
            if recipes:
                file.write("RECIPES:\n")
                for recipe in recipes:
                    file.write(f"  - ID: {recipe['item_ankama_id']}, Quantity: {recipe['quantity']}\n")
            else:
                file.write("RECIPES: None\n")

            effects = item.get('effects', [])
            if effects:
                file.write("EFFECTS:\n")
                for effect in effects:
                    file.write(f"  - {effect['formatted']}\n")
            else:
                file.write("EFFECTS: None\n")

            file.write(f"IS WEAPON: {item.get('is_weapon', False)}\n")
            
            if 'parent_set' in item:
                file.write(f"PARENT SET ID: {item['parent_set']['id']}\n")
                file.write(f"PARENT SET NAME: {item['parent_set']['name']}\n")
            else:
                file.write("PARENT SET: None\n")

            file.write("\n")

if __name__ == "__main__":
    get_item(base_url, user_filter,user_levelmin, user_levelmax)



    #'recipe': [{'item_ankama_id': 16511, 'item_subtype': 'resources', 'quantity': 2}, 
    #          {'item_ankama_id': 421, 'item_subtype': 'resources', 'quantity': 2}]