from api_to_txt import api_to_txt
from hdv_screenshot_bot import HDV_Screenshot
from data_to_gsheet import main_API,hdv_price


def main():
    """
    Main function to control the execution of various data update processes for the Dofus project.

    The user is prompted to choose an option to:
    1. Update API data and download images.
    2. Update game prices using screenshots.
    3. Transfer data from the Dofus API to Google Sheets.
    4. Transfer game prices to Google Sheets.

    Based on user input, the corresponding function is called to perform the selected action.
    """
        
    user_choice = input("""What do you want to actualize ?
1: API TO TEXT file & IMAGE DOWNLOAD
2: UPDATE GAME PRICE
3: DOFUS API TO GSHEET
4: GAME PRICE TO GSHEET
                   """)
    
    # Call the appropriate function based on user choice
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