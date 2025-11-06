from flask import Blueprint, jsonify, request
from models import db, Flight, Airport, FlightStatus
from flight_network import flight_network
from datetime import datetime

flights_blueprint = Blueprint('flights', __name__, url_prefix='/flights')

@flights_blueprint.route('/', methods=['GET'])
def get_flights():
    """Get all flights with enhanced information"""
    flights = Flight.query.all()
    result = []
    
    for f in flights:
        # Get latest status
        latest_status = FlightStatus.query.filter_by(flight_id=f.id).order_by(
            FlightStatus.updated_at.desc()
        ).first()
        
        flight_data = {
            "id": f.id,
            "flight_number": f.flight_number,
            "source": {
                "code": f.source.code,
                "name": f.source.name,
                "city": f.source.city
            },
            "destination": {
                "code": f.destination.code,
                "name": f.destination.name,
                "city": f.destination.city
            },
            "duration": f.duration,
            "price": f.price,
            "delay_prob": f.delay_prob,
            "departure_time": f.departure_time,
            "arrival_time": f.arrival_time,
            "aircraft_type": f.aircraft_type,
            "max_capacity": f.max_capacity,
            "current_bookings": 0,  # TODO: Calculate from bookings
            "status": latest_status.status if latest_status else "on_time",
            "delay_minutes": latest_status.delay_minutes if latest_status else 0
        }
        
        result.append(flight_data)
    
    return jsonify(result)

@flights_blueprint.route('/airports', methods=['GET'])
def get_airports():
    """Get all airports"""
    airports = Airport.query.all()
    result = []
    
    for airport in airports:
        airport_data = {
            "id": airport.id,
            "code": airport.code,
            "name": airport.name,
            "city": airport.city,
            "latitude": airport.latitude,
            "longitude": airport.longitude,
            "timezone": airport.timezone
        }
        result.append(airport_data)
    
    return jsonify(result)

@flights_blueprint.route('/search', methods=['GET'])
def search_flights():
    """Search flights by source and destination"""
    source = request.args.get('source')
    destination = request.args.get('destination')
    
    query = Flight.query
    
    if source:
        source_airport = Airport.query.filter_by(code=source).first()
        if source_airport:
            query = query.filter_by(source_id=source_airport.id)
    
    if destination:
        dest_airport = Airport.query.filter_by(code=destination).first()
        if dest_airport:
            query = query.filter_by(destination_id=dest_airport.id)
    
    flights = query.all()
    result = []
    
    for f in flights:
        flight_data = {
            "id": f.id,
            "flight_number": f.flight_number,
            "source": {
                "code": f.source.code,
                "name": f.source.name,
                "city": f.source.city
            },
            "destination": {
                "code": f.destination.code,
                "name": f.destination.name,
                "city": f.destination.city
            },
            "duration": f.duration,
            "price": f.price,
            "delay_prob": f.delay_prob,
            "departure_time": f.departure_time,
            "arrival_time": f.arrival_time,
            "aircraft_type": f.aircraft_type
        }
        result.append(flight_data)
    
    return jsonify(result)

@flights_blueprint.route('/status/<flight_number>', methods=['GET'])
def get_flight_status(flight_number):
    """Get current status of a specific flight"""
    flight = Flight.query.filter_by(flight_number=flight_number).first()
    
    if not flight:
        return jsonify({"error": "Flight not found"}), 404
    
    # Get latest status
    latest_status = FlightStatus.query.filter_by(flight_id=flight.id).order_by(
        FlightStatus.updated_at.desc()
    ).first()
    
    if latest_status:
        return jsonify({
            "flight_number": flight.flight_number,
            "status": latest_status.status,
            "delay_minutes": latest_status.delay_minutes,
            "reason": latest_status.reason,
            "updated_at": latest_status.updated_at.isoformat()
        })
    else:
        return jsonify({
            "flight_number": flight.flight_number,
            "status": "on_time",
            "delay_minutes": 0,
            "reason": None,
            "updated_at": None
        })

@flights_blueprint.route('/simulate-delay', methods=['POST'])
def simulate_delay():
    """Simulate a flight delay for testing"""
    data = request.get_json()
    flight_number = data.get('flight_number')
    delay_minutes = data.get('delay_minutes', 30)
    reason = data.get('reason', 'Weather conditions')
    
    if not flight_number:
        return jsonify({"error": "Flight number is required"}), 400
    
    flight = Flight.query.filter_by(flight_number=flight_number).first()
    if not flight:
        return jsonify({"error": "Flight not found"}), 404
    
    # Create new status entry
    status = FlightStatus(
        flight_id=flight.id,
        status='delayed',
        delay_minutes=delay_minutes,
        reason=reason
    )
    
    db.session.add(status)
    db.session.commit()
    
    # Trigger re-routing for affected passengers
    flight_network.handle_disruption(flight_number, 'delayed', delay_minutes)
    
    return jsonify({
        "message": f"Simulated {delay_minutes} minute delay for flight {flight_number}",
        "status": "delayed",
        "delay_minutes": delay_minutes,
        "reason": reason
    })