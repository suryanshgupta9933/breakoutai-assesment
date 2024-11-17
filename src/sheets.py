# Importing Dependencies
import os
import logging
import gspread
from dotenv import load_dotenv

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()
SERVICE_ACCOUNT_KEY = os.getenv("SERVICE_ACCOUNT_KEY")

# Authenticate with Google Sheets
def authenticate_google_sheets():
    try:
        gc = gspread.service_account(filename=SERVICE_ACCOUNT_KEY)
        logger.info("Authenticated with Google Sheets")
        return gc
    except Exception as e:
        logger.error(f"Failed to authenticate with Google Sheets: {e}")
        return None

# Retrieve a spreadsheet from Google Sheets
def get_sheet_data(gc, sheet_id):
    try:
        sheet = gc.open_by_key(sheet_id)
        worksheet = sheet.get_worksheet(0)
        logger.info(f"Retrieved spreadsheet: {sheet.title}")
        return worksheet.get_all_records()
    except Exception as e:
        logger.error(f"Failed to retrieve spreadsheet: {e}")
        return None

def update_worksheet(gc, sheet_id, data):
    try:
        sheet = gc.open_by_key(sheet_id)
        worksheet = sheet.get_worksheet(0)
        worksheet.clear()
        worksheet.append_row(data)
        logger.info(f"Updated spreadsheet: {sheet.title}")
        return True
    except Exception as e:
        logger.error(f"Failed to update spreadsheet: {e}")
        return False