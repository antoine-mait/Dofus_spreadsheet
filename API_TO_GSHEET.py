import os.path
import os
import requests

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from dotenv import load_dotenv

load_dotenv()
SCOPES = eval(os.environ.get("SCOPES"))
SAMPLE_SPREADSHEET_ID = os.environ.get("SAMPLE_SPREADSHEET_ID")

def main_API():
    for name in ["consumables", "equipment", "resources"]:
        SAMPLE_RANGE_NAME = f"API_{name.capitalize()}!B2"  # Update this line with the correct sheet name             
        GSheetAPI(name, SAMPLE_RANGE_NAME)

def getApiData(name):
    url = "https://api.dofusdu.de"
    scope_api = f"/dofus2/fr/items/{name}/all"
    myValues = []
    payload = {}
    headers = {}

    if name == "equipment" :
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
            response = requests.get(f"{url}{scope_api}", params=params, headers=headers, data=payload)
            data = response.json().get("items", [])

            for item in data:
                item_details= [
                    item['type']['name'],
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

        return myValues

    if name in ["consumables","resources"]:
        item_types_response = requests.get(f"{url}{scope_api}")
        item_types = item_types_response.json().get("items", [])

        type_of_object = set()

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

def GSheetAPI(name, SAMPLE_RANGE_NAME):
    creds = None
    # The file token.json stores the user's access and refresh tokens.
    # It is created automatically when the authorization flow completes for the first time.
    if os.path.exists("token.json"):
        creds = Credentials.from_authorized_user_file("token.json", SCOPES)
    
    # If there are no (valid) credentials available, let the user log in.
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
        # Build the service
        service = build("sheets", "v4", credentials=creds)
        # Prepare the data to be updated
        valueData = getApiData(name)
        # valueData = [['Pickles'],['Chocolate']]
        sheet = service.spreadsheets()
        # Call the Sheets API to update values
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
    main_API()