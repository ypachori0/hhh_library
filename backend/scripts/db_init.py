# helper script for initializing the database
import sys # used for manually adding parent folder to python's list of valid import locations
import os # used for getting the file path of the script, going up directory levels, and turning relative paths into absolute ones
import time
from sqlalchemy.exc import OperationalError

# ensure the project root is in sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# import from backend folder
from app import create_app
from db import db

# Retry logic in case the database container isn't ready yet
max_attempts = 10
for attempt in range(max_attempts):
    try:
        app = create_app()
        with app.app_context():
            db.create_all()
            print("All tables created successfully.")
        break  # Exit the retry loop on success
    except OperationalError as e:
        print(f"[INIT ERROR] Attempt {attempt + 1}/{max_attempts} — Database not ready: {e}")
        time.sleep(3)
else:
    print("Could not connect to the database after multiple attempts.")
    sys.exit(1)