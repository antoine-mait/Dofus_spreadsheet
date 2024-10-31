import os.path
import os
import requests

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from dotenv import load_dotenv

# Load environment variables for Google Sheets API
load_dotenv()
SCOPES = eval(os.environ.get("SCOPES"))
SAMPLE_SPREADSHEET_ID = os.environ.get("SAMPLE_SPREADSHEET_ID")

def main_API():
    """
    Main entry point to fetch and update data for different item categories in Google Sheets.
    
    Iterates over specified item categories (consumables, equipment, resources),
    defining the target sheet range for each, and updating the Google Sheet.
    """
    for name in ["consumables", "equipment", "resources"]:
        SAMPLE_RANGE_NAME = f"API_{name.capitalize()}!B2"  # Range for each category's sheet
        GSheetAPI(name, SAMPLE_RANGE_NAME)

def parse_txt_file(file_path):
    """
    Reads a .txt file and extracts item names and prices.
    
    Args:
        file_path (str): Path to the text file with item data.
    
    Returns:
        list: A list of [name, price] pairs for each item in the file.
    """
    items = []
    with open(file_path, 'r', encoding='utf-8') as file:
        for line in file:
            # Split each line at ', ' to separate name and price
            parts = line.strip().split(', ')
            # Only process valid lines with two parts
            if len(parts) == 2:
                name = parts[0]
                price = int(parts[1])
                items.append([name, price])
    return items

def hdv_price():
    """
    Reads the HDV_Price.txt file and uploads its content to Google Sheets.
    
    Utilizes `parse_txt_file` to parse item data and then calls `GSheetAPI`
    to update the Google Sheet.
    """
    file_path = os.path.join("tmp", "HDV_Price.txt")
    items_data = parse_txt_file(file_path)

    SAMPLE_RANGE_NAME = "HDV_Price!B2"  # Define target range for HDV prices
    GSheetAPI("HDV_price", SAMPLE_RANGE_NAME, items_data)

def getApiData(name):
    """
    Retrieves item data from the Dofus API for the specified category.

    Args:
        name (str): Category of items (e.g., "equipment", "consumables", "resources").

    Returns:
        list: A list of item details, including type, ID, name, level, image URL, and recipes (if any).
    """
    url = "https://api.dofusdu.de"
    scope_api = f"/dofus2/fr/items/{name}/all"
    myValues = []
    payload = {}
    headers = {}

    if name == "equipment" :
         # Loop over different equipment types and fetch items for each
        for item_type in ["Amulet", "Ring", "Boots", "Shield", 
                          "Cloak", "Belt", "Hat", "Dofus", 
                          "Trophy", "Prysmaradite", "Pet", "Petsmount"
                            ] :
            params = {
                    "sort[level]": "asc",
                    "filter[type_enum]": item_type,
                    "filter[min_level]": 1,
                    "filter[max_level]": 200,
                }
            # Fetch item data from API
            response = requests.get(f"{url}{scope_api}", params=params, headers=headers, data=payload)
            data = response.json().get("items", [])

            for item in data:
                # Extract core item details
                item_details= [
                    item['type']['name'],
                    item['ankama_id'],
                    item['name'],
                    item['level'],
                    item['image_urls']['sd'],
                    ]
                
                row = item_details.copy()
                # Append recipe details if available
                recipe_list = item.get('recipe', [])
                for recipe_item in recipe_list[:8]:
                    resource_id = recipe_item['item_ankama_id']
                    quantity = recipe_item['quantity']
                    row.append(resource_id)
                    row.append(quantity)

                myValues.append(row)

        return myValues

    if name in ["consumables","resources"]:
         # Fetch item types within category
        item_types_response = requests.get(f"{url}{scope_api}")
        item_types = item_types_response.json().get("items", [])

        type_of_object = set()
        # Collect unique types
        for resource_type in item_types:
            type_name = resource_type['type']['name']
            type_of_object.add(type_name)
        
        type_of_object = list(type_of_object)
        
        for object in type_of_object:
            params = {
                    "sort[level]": "asc",
                    "filter[type_name]" : object,
                    "filter[min_level]": 1,
                    "filter[max_level]": 200,
                }
            
            response = requests.get(f"{url}{scope_api}", params=params, headers=headers, data=payload)

            data = response.json().get("items", [])
            if name == "consumables" : 
                # Extract data differently for consumable
                for item in data:
                    item_details= [ item['type']['name'],
                                    item['ankama_id'],
                                    item['name'],
                                    item['level'],
                                    item['image_urls']['sd'],
                                    ]
                    
                    row = item_details.copy()

                    recipe_list = item.get('recipe', [])

                    for recipe_item in recipe_list[:8]:
                        resource_id = recipe_item['item_ankama_id']
                        quantity = recipe_item['quantity']
                        row.append(resource_id)
                        row.append(quantity)

                    myValues.append(row)
            if name == " resources" :
                for item in data:
                    myValues.append([item['type']['name'],
                                    item['ankama_id'],
                                    item['name'],
                                    item['level'],
                                    item['image_urls']['sd'],
                                    ])
    
        return myValues

def GSheetAPI(name, SAMPLE_RANGE_NAME, values):
    """
    Updates a Google Sheet with provided item data, authenticating with the Google Sheets API.

    Args:
        name (str): Category name for the items.
        SAMPLE_RANGE_NAME (str): Google Sheets range to update.
        values (list): Data to write to Google Sheets; if None, fetches data using `getApiData`.
    """
    creds = None
    # The file token.json stores the user's access and refresh tokens.
    # It is created automatically when the authorization flow completes for the first time.
    if os.path.exists("token.json"):
        creds = Credentials.from_authorized_user_file("token.json", SCOPES)
    
    # Handle credential refresh if needed
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file("credentials.json", SCOPES)
            creds = flow.run_local_server(port=8080)  # Starts the local server to handle the authorization flow
            # Save the credentials for the next run
            with open("token.json", "w") as token:
                token.write(creds.to_json())
                print("Token saved to token.json")

    try:
        # Initialize Sheets API service
        service = build("sheets", "v4", credentials=creds)
        if name == "HDV_price":
            valueData = values
        else:
            valueData = getApiData(name)
        sheet = service.spreadsheets()
        
        # Update Google Sheet with data
        result = (sheet.values().update(
            spreadsheetId=SAMPLE_SPREADSHEET_ID, 
            range=SAMPLE_RANGE_NAME,
            valueInputOption="USER_ENTERED",
            body={"values": valueData}
        ).execute())

        print("Update successful:", SAMPLE_RANGE_NAME)

    except HttpError as err:
        print("An error occurred:", err)

if __name__ == "__main__":
    hdv_price()
