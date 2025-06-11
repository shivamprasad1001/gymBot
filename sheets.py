import gspread
from oauth2client.service_account import ServiceAccountCredentials

def init_sheet(sheet_name):
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    creds = ServiceAccountCredentials.from_json_keyfile_name("credentials.json", scope)
    client = gspread.authorize(creds)

    print("✅ Connected to Google Sheets as:", creds.service_account_email)

    try:
        sheet = client.open(sheet_name).sheet1
        print(f"✅ Opened sheet: {sheet_name}")
        return sheet
    except Exception as e:
        print("❌ Failed to open sheet:", e)
        raise e


def save_lead(sheet, name, contact, goal):
    sheet.append_row([name, contact, goal])
