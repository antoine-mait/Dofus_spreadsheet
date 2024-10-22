from TXT_Items import main_item
from TXT_Mounts import main_mount
from TXT_Ressources import main_resources
from TXT_Consumables import main_consumable

def main():
    user_choice = input("""What do you want to do ?
1: actualize_item/recipes
2: actualize_mounts
3: actualize_ressources
4: actualize_consummable
5: actualize_all 
6: actualize_SpreadSheet """)

    if user_choice == "1":
        main_item()
    elif user_choice == "2":
        main_mount()    
    elif user_choice == "3":
        main_resources()
    elif user_choice == "4":
        main_consumable()
    elif user_choice == "5":
        main_resources(filter_check=True) 
        main_item(filter_check=True)
        main_mount(filter_check=True)
        main_consumable(filter_check=True)
        

if __name__ == "__main__":
    main()