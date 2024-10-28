from API_TO_TXT import api_to_txt
from API_TO_GSHEET import main_API
from HDV_SCREENSHOT_Bot import HDV_Screenshot,HDV_Reader


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
        ingame()
    elif user_choice == "3":
        to_gsheet()
    elif user_choice == "4":
        main_screenshot_reader()

def text_file():

    api_to_txt()

def ingame():

    HDV_Screenshot()

def to_gsheet():

    main_API()

if __name__ == "__main__":
    main()