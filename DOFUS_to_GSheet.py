from API_TO_TXT import api_to_txt
from DATA_TO_GSHEET import main_API,hdv_price
from HDV_SCREENSHOT_Bot import HDV_Screenshot


def main():
    user_choice = input("""What do you want to actualize ?
1: TEXT file 
2: IN GAME HDV SCREENSHOT
3: API TO GSHEET
4: GAME TO GSHEET
                   """)
    if user_choice == "1":
        api_to_txt()
    elif user_choice == "2":
        HDV_Screenshot()
    elif user_choice == "3":
        main_API()
    elif user_choice == "4":
        hdv_price()
   
if __name__ == "__main__":
    main()