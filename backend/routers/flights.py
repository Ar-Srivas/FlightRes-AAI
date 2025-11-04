from flask import Blueprint, jsonify, request
from models import db, Flight, Airport

flights_blueprint = Blueprint('flights', __name__, url_prefix='/flights')

@flights_blueprint.route('/', methods=['GET'])
def get_flights():
    flights = Flight.query.all()
    result = [
        {
            "flight_number": f.flight_number,
            "source": f.source.code,
            "destination": f.destination.code,
            "duration": f.duration,
            "price": f.price,
            "delay_prob": f.delay_prob
        } for f in flights
    ]
    return jsonify(result)

@flights_blueprint.route('/add', methods=['POST'])
def add_flight():
    data = request.json
    new_flight = Flight(**data)
    db.session.add(new_flight)
    db.session.commit()
    return jsonify({"message": "Flight added"}), 201
