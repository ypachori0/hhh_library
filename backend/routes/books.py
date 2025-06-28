# import the necessary libraries
import gspread

from flask import Blueprint, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from models import Book, Transaction
from db import db
from datetime import datetime
from scripts.sheet_utils import sync_to_google_sheets

# create a blueprint for book related routes
books_bp = Blueprint('books', __name__)

# route to fetch all the books in the database
@books_bp.route('/', methods=['GET'])
def get_books():
    # fetch all books
    books = Book.query.all()
    # return metadata
    return jsonify([{
        'barcode': b.barcode,
        'title': b.title,
        'author': b.author,
        'in_library': b.in_library
    } for b in books])

# route to fetch book based on barcode
@books_bp.route('/<barcode>', methods=['GET'])
def get_book_by_barcode(barcode):
    # get the book's barcode to use in the url
    book = Book.query.get(barcode)

    # if barcode doesn't exist, return error
    if not book:
        return jsonify({'error: Book not found'}), 404
    
    # return the book information
    return jsonify({
        'barcode': book.barcode,
        'title': book.title,
        'author': book.author,
        'in_library': book.in_library
    })

# route for changing the book's status (checked out or not)
@books_bp.route('/<barcode>/toggle', methods=['PATCH'])
def toggle_book_status(barcode):
    # get action and patron_id from response body
    data = request.get_json()
    action = data.get("action")
    patron_id = data.get("patron_id")

    # input validation for the data from the response body
    # making sure there is an action
    if not action:
        return jsonify({"error": "No action (checkout or return)"}), 400
    
    # making sure there is a patron_id
    if not patron_id:
        return jsonify({"error": "No patron_id"}, 400)

    # look up book by barcode
    book = Book.query.get(barcode)

    # make sure that the book exists
    if not book:
        return jsonify({"error": "Book not found"}), 404
    

    # update in_library status based on correct action
    if action == "checkout":
        # validation of action
        if not book.in_library:
            return jsonify({"error": "Book is already checked out"}), 400
        
        # update the in_library status
        book.in_library = False

        # add a new transaction in the transactions table
        transaction = Transaction(
            barcode=barcode,
            patron_id=patron_id,
            checked_out_at=datetime.now()
        )
        db.session.add(transaction)
        db.session.commit()

    elif action == "return":
        # validation of action
        if book.in_library:
            return jsonify({"error": "Book is already in the library"}), 400
       
        # update status
        book.in_library = True

        # update the transactions table
        transaction = Transaction.query.filter_by(
            barcode=barcode,
            patron_id=patron_id,
            returned_at=None
        ).first()

        # check to make sure the transaction exists
        if not transaction:
            return jsonify({"error": "No active checkout transaction found"}), 400


        transaction.returned_at = datetime.now()
        db.session.commit()

    # sync db changes with google spreadsheet by calling the sync_to_google_sheets() function from the sheet_utils.py file
    sync_to_google_sheets(book)
    
    # return confirmation JSON
    return jsonify({
        "message": f"Book successfully {'checked out' if action == 'checkout' else 'returned'}",
        "barcode": book.barcode,
        "in_library": book.in_library
    }), 200