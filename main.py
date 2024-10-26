# from TXT_Items import main_item
# from TXT_Mounts import main_mount
# from TXT_Ressources import main_resources
# from TXT_Consumables import main_consumable
from API_TO_GSHEET import main_API
from HDV_SCREENSHOT_Bot import main_bot
from HDV_Reader import  main_screenshot_reader

def main():
    user_choice = input("""What do you want to actualize ?
1: TEXT file 
2: IN GAME HDV SCREENSHOT
3: API TO GSHEET
4: GAME TO GSHEET
                   """)
    if user_choice == "1":
        text_file()
    elif user_choice == "2":
        main_bot()
    elif user_choice == "3":
        main_API()
    elif user_choice == "4":
        main_screenshot_reader()

def text_file():

    user_choice = input("""TEXT FILE 
What do you want to do ?
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