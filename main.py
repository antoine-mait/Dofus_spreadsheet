from API_Items import main_item
from API_Mounts import main_mount
from API_Ressources import main_resources


def main():
    user_choice = input("""What do you want to do ?
1: actualize_item/recipes
2: actualize_mounts
3: actualize_ressources
4: actualize_all 
5: actualize_SpreadSheet """)

    if user_choice == "1":
        main_item()
    elif user_choice == "2":
        main_mount()    
    elif user_choice == "3":
        main_resources()
    elif user_choice == "4":
        main_resources() 
        main_item()
        main_mount()
        

if __name__ == "__main__":
    main()