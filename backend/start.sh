#!/bin/bash
# What this file does:
# 1. initializes the database by running db_init.py
# 2. imports book data by running import_books.py
# 3. starts the flask backend app

# Run database setup
echo "[INIT] Initializing database..."
python scripts/db_init.py

# Import books
echo "[IMPORT] Importing books from Google Sheets..."
python scripts/import_books.py

# Start the Flask server
echo "[START] Starting Flask backend..."
python app.py