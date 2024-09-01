import os.path

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
import dotenv
import re
dotenv.load_dotenv()

GOOGLE_SHEET_ID = os.getenv("GOOGLE_SPREADSHEET_ID")

def get_google_sheets_service():
    SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]
    creds = None
    if os.path.exists("token.json"):
        creds = Credentials.from_authorized_user_file("token.json")
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                "credentials.json", SCOPES
            )
            creds = flow.run_local_server(port=0)
        with open("token.json", "w") as token:
            token.write(creds.to_json())
    return build("sheets", "v4", credentials=creds)

# only read the sheet with tab name "Status Follow Up(ALL)" and column A for status and K,L,M for phone numbers
def read_google_sheet(service):
    sheet = service.spreadsheets()
    result = (
        sheet.values()
        .get(spreadsheetId=GOOGLE_SHEET_ID, range="Status Follow Up(ALL)!A:Z")
        .execute()
    )
    values = result.get("values", [])
    return values

def read_status_and_phones(values):
    status_and_phones = []
    for row in values[1:]:
        if row and row[0] and any(row[1:]):
            status = row[0]
            phone_numbers = row[10:13]
            for phone in phone_numbers:
                if phone:
                    match = re.match(r"^\d{10}$", phone)
                    if match:
                        status_and_phones.append((status, phone))
    return status_and_phones

def main():
    service = get_google_sheets_service()
    values = read_google_sheet(service)
    status_and_phones = read_status_and_phones(values)
    print(status_and_phones)

if __name__ == "__main__":
    main()