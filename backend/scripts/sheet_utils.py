# this file handles everything related to the google sheets api. it has functions that can be used
# across the project
import uuid
import os, sys
import gspread # library that lets us interact with google sheets

from google.oauth2.service_account import Credentials

# define path to credentials.json
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
CREDS_PATH = os.path.join(BASE_DIR, 'credentials', 'credentials.json')

# getting access to the ID of the spreadsheet we wish to access
# to find the sheet ID, go to the URL of the google spreadsheet and copy everything between /d/ and /edit
SHEET_ID = "1Tk8k8W4zTch4JL60cdplrAPOGN3GwDzKMttf1tV4QxU"

# the different things i can do when accessing a specific file using the google api
# in this case i only want access to the Library Project Data spreadsheet
SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]

# function to create a new set of credentials and then authorize those credentials
def get_client():
    # create a new set of credentials using the JSON credentials that were downloaded
    creds = Credentials.from_service_account_file(CREDS_PATH, scopes=SCOPES)

    # authorize ourselves
    return gspread.authorize(creds)


# function to get the worksheet we want to use from google sheets
def get_worksheet():
    # call the get_client() function so that we can access the sheet
    client = get_client()

    # open the spreadsheet using the sheet ID
    sheet = client.open_by_key(SHEET_ID)

    # open the first worksheet (Book Inventory)
    return sheet.get_worksheet(0)

# function to find a book by barcode within the spreadsheet
# takes the worksheet and the book's barcode as arguments
def find_row_by_barcode(worksheet, barcode):
    # look up the barcode within the spreadsheet and return the row it belongs to
    try:
        cell = worksheet.find(barcode)
        return cell.row
    # if the barcode is not found, return an error
    except gspread.exceptions.CellNotFound:
        return None
    
# function to update the book's in_library value
# takes the worksheet, the row we want to update, and the in_library value as arguments
def update_value(worksheet, row, in_library):
    value = "1" if in_library else "0"
    worksheet.update_cell(row, 4, value) # value is in column D so D=4

# function to sync the db changes with the spreadsheet
def sync_to_google_sheets(book):
    # call the get_worksheet() function
    worksheet = get_worksheet()

    # find the row we want to update and store it in a variable
    row = find_row_by_barcode(worksheet, book.barcode)

    # if that barcode exists, update the row
    if row:
        update_value(worksheet, row, book.in_library)
    # if barcode doesn't exist, return an error
    else:
        print(f"[Sync] Barcode {book.barcode} not found in sheet")