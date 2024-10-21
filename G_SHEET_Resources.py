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
SAMPLE_RANGE_NAME = "API_Resources!B2"

def getApiData():
    url = "https://api.dofusdu.de"
    scope_api = "/dofus2/fr/items/resources/all"

    item_types_response = requests.get(f"{url}{scope_api}")
    item_types = item_types_response.json().get("items", [])
    myValues = []
    type_of_resource = set()
    for resource_type in item_types:
        type_name = resource_type['type']['name']
        type_of_resource.add(type_name)
    
    type_of_resource = list(type_of_resource)
    
    for resource in type_of_resource:
        params = {
                "sort[level]": "asc",
                "filter[type_name]" : resource,
                "filter[min_level]": 1,
                "filter[max_level]": 200,
            }

        
        payload = {}
        headers = {}
        response = requests.get(f"{url}{scope_api}", params=params, headers=headers, data=payload)
        
        data = response.json().get("items", [])
        for item in data:
            myValues.append([item['type']['name'],
                            item['ankama_id'],
                            item['name'],
                            item['level'],
                            item['image_urls']['sd'],
                            ])
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
    