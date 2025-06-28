import os, sys

from flask import Flask
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from db import db

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

def create_app():
    app = Flask(__name__)
    CORS(app, resources={r"/*": {"origins": "*"}}, automatic_options=True)

    # MySQL connection string
    app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get("SQLALCHEMY_DATABASE_URI")
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    # initialize db with app
    db.init_app(app)

    # import models from models.py so they register with SQLAlchemy
    from models import Book, Patron, Transaction

    # import and register API route blueprints
    from routes.books import books_bp
    app.register_blueprint(books_bp, url_prefix='/books')

    from routes.patrons import patrons_bp
    app.register_blueprint(patrons_bp, url_prefix='/patrons')

    @app.route('/')
    def home():
        return "Library system backend is running!"
    
    return app

if __name__ == '__main__':
    app = create_app()
    app.run(host='0.0.0.0', port=8000, debug=True)