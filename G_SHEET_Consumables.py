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
SAMPLE_RANGE_NAME = "API_Consumable!B2"  # Update this line with the correct sheet name

def getApiData():
    url = "https://api.dofusdu.de"
    scope_api = "/dofus2/fr/items/consumables/all"
    item_types_response = requests.get(f"{url}{scope_api}")
    item_types = item_types_response.json().get("items", [])
    myValues = []
    type_of_consumable = set()

    for resource_type in item_types:
        type_name = resource_type['type']['name']
        type_of_consumable.add(type_name)
    
    type_of_consumable = list(type_of_consumable)
    
    for consumable in type_of_consumable:
        params = {
                "sort[level]": "asc",
                "filter[type_name]" : consumable,
                "filter[min_level]": 1,
                "filter[max_level]": 200,
            }
        payload = {}
        headers = {}
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

def main():
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
        valueData = getApiData()
        # valueData = [['Pickles'],['Chocolate']]
        sheet = service.spreadsheets()
        
        # Call the Sheets API to update values
        result = (sheet.values().update(
            spreadsheetId=SAMPLE_SPREADSHEET_ID, 
            range=SAMPLE_RANGE_NAME,
            valueInputOption="USER_ENTERED",
            body={"values": valueData}
        ).execute())

        print("Update successful:", result)

    except HttpError as err:
        print("An error occurred:", err)

if __name__ == "__main__":
    main()
    