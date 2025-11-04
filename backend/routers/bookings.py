from flask import Blueprint, jsonify, request


bookings_blueprint = Blueprint('bookings', __name__)


@bookings_blueprint.route('/create', methods=['POST'])
def create_booking():
    data = request.json
    # Here you would add logic to create a booking with the provided data
    return jsonify({"message": "Booking created", "data": data}), 201