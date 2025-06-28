# import the necessary libraries
from flask import Blueprint, request, jsonify
from models import Patron
from app import db

# create a blueprint for all user related routes
patrons_bp = Blueprint('patrons', __name__)

# route to look up a patron by name and phone number in the database
@patrons_bp.route('/identify', methods=['POST', 'OPTIONS'])
def identify_patron():
    if request.method == 'OPTIONS':
        return '', 204

    # get the name and phone number from the request body
    data = request.get_json()
    # making sure that if the name value is not a string, it sets it to an empty string
    name = data.get('name') if isinstance(data.get('name'), str) else ""
    # making sure that if phone value is not a string, it sets it to an empty string
    phone = data.get('phone') if isinstance(data.get('phone'), str) else ""

    # input validation
    # if name value is null, return an error
    if not name.strip():
        return jsonify({"error": "Name can not be empty"}), 400
    
    # if phone value is null, return an error
    if not phone.strip():
        return jsonify({"error": "Phone can not be empty"}), 400
    
    # use name and phone number to look up patron in the database
    patron = Patron.query.filter_by(name=name, phone_number=phone).first()
    
    # if not found, return false
    if not patron:
        return jsonify({
            "existing": False
        }), 200
    
    # if match is found, return true
    return jsonify({
        "existing": True,
        "patron": {
            "id": patron.id,
            "name": patron.name,
            "phone": patron.phone_number
        }
    }), 200

# route to add a new patron to the database
@patrons_bp.route('/create', methods=['POST'])
def create_patron():
    # get the name, phone number, and email from the request body
    data = request.get_json()
    # making sure that if the name value is not a string, it sets it to an empty string
    name = data.get('name') if isinstance(data.get('name'), str) else ""
    # making sure that if phone value is not a string, it sets it to an empty string
    phone = data.get('phone') if isinstance(data.get('phone'), str) else ""
    # making sure that if email value is not a string, it sets it to an empty string
    email = data.get('email') if isinstance(data.get('email'), str) else ""

    # input validation
    # if name value is null, return an error
    if not name.strip():
        return jsonify({"error": "Name can not be empty"}), 400
    
    # if phone value is null, return an error
    if not phone.strip():
        return jsonify({"error": "Phone can not be empty"}), 400
    
    # if email value is null, return an error
    if not email.strip():
        return jsonify({"error": "Email can not be empty"}), 400
    
    # insert the new patron into the patrons table
    new_patron = Patron(
        name=name,
        phone_number=phone,
        email=email
    )
    db.session.add(new_patron)
    db.session.commit()

    # return the patron_id of the new patron
    return jsonify({
        "id": new_patron.id,
        "name": new_patron.name,
        "email": new_patron.email,
        "phone": new_patron.phone_number
    }), 201