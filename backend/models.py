from db import db

# create the books table
class Book(db.Model):
    __tablename__ = 'books'
    barcode = db.Column(db.String(20), primary_key=True)
    title = db.Column(db.String(255), nullable=False)
    author = db.Column(db.String(255), nullable=False)
    in_library = db.Column(db.Boolean, default=True)

# create the patrons table
class Patron(db.Model):
    __tablename__ = 'patrons'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    phone_number = db.Column(db.String(50), unique=True, nullable=False)

# create the transactions table
class Transaction(db.Model):
    __tablename__ = 'transactions'
    id = db.Column(db.Integer, primary_key=True)
    barcode = db.Column(db.String(20), db.ForeignKey('books.barcode'), nullable=False)
    patron_id = db.Column(db.Integer, db.ForeignKey('patrons.id'), nullable=False)
    checked_out_at = db.Column(db.DateTime, nullable=False)
    returned_at = db.Column(db.DateTime)