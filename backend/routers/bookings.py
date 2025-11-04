from flask import Blueprint, jsonify, request
from models import db, Booking

bookings_blueprint = Blueprint('bookings', __name__, url_prefix='/bookings')

@bookings_blueprint.route('/', methods=['GET'])
def get_bookings():
    bookings = Booking.query.all()
    result = [
        {
            "id": b.id,
            "user_name": b.user_name,
            "flight_id": b.flight_id,
            "status": b.status
        } for b in bookings
    ]
    return jsonify(result)

@bookings_blueprint.route('/add', methods=['POST'])
def add_booking():
    data = request.json
    booking = Booking(**data)
    db.session.add(booking)
    db.session.commit()
    return jsonify({"message": "Booking created"}), 201
