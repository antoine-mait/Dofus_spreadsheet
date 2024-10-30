# Dofus Auction House Scraper price Scripts

This project consists of a set of Python scripts designed to automate various tasks related to the Dofus game, including fetching data from the Dofus API, taking screenshots of in-game prices, and transferring data to Google Sheets.

## Requirements

To run the scripts, you will need the following:

- Python 3.10 (or compatible version)
- Required Python packages (see `requirements.txt` for a complete list)
- Create an `.env` file with those information : 
```
SCOPES=["https://www.googleapis.com/auth/spreadsheets"] # or any other scope

SAMPLE_SPREADSHEET_ID="YOUR_SPREADSHEET_ID"

MAIN_IMG_FOLDER=C:\\path\\to\\your\\HDV_IMG\\ # Feel free to change the directory as you please

folder_dir_tmp =C:\\path\\to\\your\\tmp\images\\tmp_screenshot\\

DOFUS_API="https://api.dofusdu.de"
```
- Google Sheets API credentials for accessing your Google Sheets
  - [Click here to watch a tutorial](https://www.youtube.com/watch?v=X-L1NKoEi10&ab_channel=DanielOtto)

## Overview of Scripts

### 1. API_TO_TXT
- Fetches data from the Dofus API and saves it to a text file.
- Retrieves item information and crafting recipes from the API.
- Downloads game item images.
- Designed for learning purposes with the API, not for Google Sheets integration.

### 2. HDV_SCREENSHOT_Bot
- Takes screenshots of in-game prices from the HDV interface.
- Utilizes Tesseract OCR for text recognition to capture price data.
- Selects all item types, takes screenshots, scrolls down, and moves to the next auction house.

### 3. DATA_TO_GSHEET
- Transfers data from the Dofus API to Google Sheets.
- Contains functions to update game prices and import data from text files.
- Some item names may need correction due to their length in the auction house or because of misinterpretation during text recognition.
  - Create a `correction.py` file in the tmp folder 
   ```
   correction_dict = {
                        "Bouiglours": "Boulglours",
                        "Clef de la Chambre de Tal K: …": "Clef de la Chambre de Tal Kasha",
                        # Add other common errors here
                     }
  ```

### 4. Main Controller Script
- Serves as the main entry point for the project.
- Allows users to choose tasks based on input.

## Usage

1. **Clone the repository** (or download the scripts).
2. **Install required packages**:
   ```
   pip install -r requirements.txt
   ```
3. **Run the main script:**
   ```
   python main.py
   ```
4. **Follow the on-screen prompts to select the desired operation:**

- 1: API TO TEXT file & IMAGE DOWNLOAD
- 2: UPDATE GAME PRICE
- 3: DOFUS API TO GSHEET
- 4: GAME PRICE TO GSHEET

## Notes

- Ensure you have the necessary permissions set up in your Google Sheets API for the `DATA_TO_GSHEET` script to function correctly.
- The `HDV_SCREENSHOT_Bot` may require proper configuration for screen resolution and image capture settings.


## License

This project is licensed under the MIT License. See the [License](MIT.txt) file for details.


## Disclaimer

This program is intended for educational purposes only. Use it at your own risk. The author does not condone the use of this software for violating the terms of service of any game or service.

