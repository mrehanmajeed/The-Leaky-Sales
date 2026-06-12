import gspread
from google.oauth2.service_account import Credentials
import logging
from config import settings

logger = logging.getLogger(__name__)

def fetch_all_rows() -> list[dict]:
    try:
        scopes = [
            "https://spreadsheets.google.com/feeds", 
            "https://www.googleapis.com/auth/drive"
        ]
        creds = Credentials.from_service_account_file(
            settings.GOOGLE_SERVICE_ACCOUNT_FILE, 
            scopes=scopes
        )
        client = gspread.authorize(creds)
        
        sheet = client.open_by_key(settings.SHEETS_SPREADSHEET_ID).sheet1
        return sheet.get_all_records()
    except Exception as e:
        logger.error(f"Error fetching from Google Sheets: {e}")
        return []
