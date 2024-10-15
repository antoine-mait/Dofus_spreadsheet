from API_Items import get_item
from API_Mounts import get_mount
from API_Ressources import get_ressources


def main():
    user_choice = input("""What do you want to do 
                        (1: actualize_item/recipes
                         2: actualize_mounts
                         3: actualize_ressources ? """)

    if user_choice == "actualize_item":
        get_item()
    elif user_choice == "actualize_mounts":
        get_ressources()    
    elif user_choice == "actualize_ressources":
        get_ressources()

if __name__ == "__main__":
    main()