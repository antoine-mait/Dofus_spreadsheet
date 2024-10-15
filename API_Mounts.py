import requests

base_url = "https://api.dofusdu.de"  # Confirm the correct base URL
user_filter = input("""Choose the filter:
dragodinde
muldo
volkorne
                    
or type 'all': """)

def get_mount(base_url, user_filter):
    if user_filter != "all":
        params = {
            "sort[level]": "asc",  # Sort by level in ascending order
            "filter[type_enum]": user_filter,  # Filter for items of type "hat"
        }

        # Get items with the specified filters
        response = requests.get(f"{base_url}/dofus2/fr/mounts/all", params=params)

        if response.status_code == 200:
            response_data = response.json()
            mounts = response_data['mounts']
            
        else:
            print(f"Error: {response.status_code}, Message: {response.text}")

        mount_title =  user_filter.upper()
        try:
            with open(f"MOUNTS/{mount_title}.txt", "w", encoding='utf-8') as file:
                for mount in mounts:
                    if mount['family_name'] == user_filter.capitalize():
                        file.write(f"NAME : {mount['name']}\n")
                        file.write(f"ID : {mount['ankama_id']}\n")
                        file.write(f"IMAGE URL : {mount['image_urls']['icon']}\n")

                        effects = mount.get("effects", [])
                        if effects:
                            file.write("EFFECTS:\n")
                            for effect in effects:
                                file.write(f"  - {effect['formatted']}\n")

                            file.write("\n")
                        else:
                            file.write("EFFECTS: None\n")
                            file.write("\n")

        except UnboundLocalError:
            print("No mount in level Range")
        

if user_filter == "all":
    mounts_types = [
        "dragodinde",
        "muldo",
        "volkorne"
        ]
    for mount_type in mounts_types:
        user_filter = mount_type
        
        get_mount(base_url, user_filter)

if __name__ == "__main__":
    get_mount(base_url,user_filter)