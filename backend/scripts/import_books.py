# here i am using the google sheets api to import the data from the google spreadsheet directly into the database
import os
import sys
import pandas as pd
import uuid # used to generate placeholder barcodes
import time
from sqlalchemy.exc import OperationalError

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import create_app
from db import db
from models import Book
from sheet_utils import get_worksheet

# define path to credentials.json
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
CREDS_PATH = os.path.join(BASE_DIR, 'credentials', 'credentials.json')

# the different things i can do when accessing a specific file using the google api
# in this case i only want access to the Library Project Data spreadsheet
scopes = [
    "https://www.googleapis.com/auth/spreadsheets"
]

# call the get_worksheet() function so that we can access the Book Inventory worksheet in the spreadsheet
worksheet = get_worksheet()

# get all the data in the worksheet and convert to a pandas dataframe
# df means dataframe and it comes from pandas library, it's basically a spreadsheet in python
# what i'm doing here is using pandas to read in the values from the google spreadsheet into a dataframe called df
data = worksheet.get_all_records()
df = pd.DataFrame(data)

# renaming the columns to match the column names used in the Book model
df.rename(columns={
    'Barcode #': 'barcode',
    'Title': 'title',
    'Author': 'author',
    'Value': 'in_library'
}, inplace=True)

# Retry logic for DB connection
max_attempts = 10
for attempt in range(max_attempts):
    try:
        app = create_app()
        with app.app_context():
            missing_barcode_count = 0

            for _, row in df.iterrows():
                raw_barcode = str(row['barcode']).strip()
                if not raw_barcode or raw_barcode.lower() == 'nan':
                    raw_barcode = f"MISSING_{uuid.uuid4().hex[:8]}"
                    missing_barcode_count += 1

                if Book.query.get(raw_barcode):
                    continue  # Skip if already exists

                new_book = Book(
                    barcode=raw_barcode,
                    title=row['title'],
                    author=row['author'],
                    in_library=bool(row['in_library'])
                )

                db.session.add(new_book)

            db.session.commit()
            print("Books imported successfully.")
            print(f"{missing_barcode_count} book(s) added with placeholder barcodes.")
        break
    except OperationalError as e:
        print(f"[IMPORT ERROR] Attempt {attempt + 1}/{max_attempts} — Database not ready: {e}")
        time.sleep(3)
else:
    print("Could not connect to the database after multiple attempts.")
    sys.exit(1)


### database insertion logic

# initialize flask application using create_app()
app = create_app()

# telling flask that when running this import script, use app.py as the current application context for everything inside this block
# otherwise it wouldn't know what to do since this script is running outside of the main app file
with app.app_context():
    # track how many books have missing barcodes
    missing_barcode_count = 0

    # iterate over the rows and add books
    for _, row in df.iterrows():
        # extract the barcodes and strip any whitespace
        raw_barcode = str(row['barcode']).strip()
        
        # if there is no barcode
        if not raw_barcode or raw_barcode.lower() == 'nan':
            # generate a unique placeholder barcode using uuid
            raw_barcode = f"MISSING_{uuid.uuid4().hex[:8]}"
            missing_barcode_count += 1

        # avoid duplicate barcodes
        if Book.query.get(str(row['barcode'])):
            continue # skip if barcode already exists

        # create a new Book object using the values from the row
        new_book = Book(
            barcode=str(row['barcode']),
            title=row['title'],
            author=row['author'],
            in_library=bool(row['in_library']) # 1 = in library, 0 = checked out
        )

        # stage the book to be added to the database
        db.session.add(new_book)

    # once all the books are added, commit the changes to persist them in the db
    db.session.commit()
    print("Books imported successfully")
    
    # i want to see how many books have missing barcodes
    print(f" {missing_barcode_count} book(s) added with placeholder barcodes")