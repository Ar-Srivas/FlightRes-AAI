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
            "status": f.status,
            "departure_time": f.departure_time,
            "arrival_time": f.arrival_time,
            "aircraft_type": f.aircraft_type,
            "max_capacity": f.max_capacity,
            "current_bookings": len(f.bookings)
        }
        
        if latest_status:
            flight_data["latest_status"] = {
                "status": latest_status.status,
                "delay_minutes": latest_status.delay_minutes,
                "reason": latest_status.reason,
                "updated_at": latest_status.updated_at.isoformat()
            }
        
        result.append(flight_data)
    
    return jsonify(result)

@flights_blueprint.route('/add', methods=['POST'])
def add_flight():
    """Add a new flight to the system"""
    try:
        data = request.json
        
        # Validate required fields
        required_fields = ['flight_number', 'source_id', 'destination_id', 'duration', 'price']
        for field in required_fields:
            if field not in data:
                return jsonify({"error": f"Missing required field: {field}"}), 400
        
        # Check if flight number already exists
        existing = Flight.query.filter_by(flight_number=data['flight_number']).first()
        if existing:
            return jsonify({"error": "Flight number already exists"}), 400
        
        # Validate airports exist
        source_airport = Airport.query.get(data['source_id'])
        dest_airport = Airport.query.get(data['destination_id'])
        
        if not source_airport or not dest_airport:
            return jsonify({"error": "Invalid airport ID"}), 400
        
        new_flight = Flight(**data)
        db.session.add(new_flight)
        db.session.commit()
        
        # Rebuild network to include new flight
        flight_network.build_network()
        
        return jsonify({
            "message": "Flight added successfully",
            "flight": {
                "id": new_flight.id,
                "flight_number": new_flight.flight_number,
                "source": source_airport.code,
                "destination": dest_airport.code
            }
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500

@flights_blueprint.route('/<flight_number>', methods=['GET'])
def get_flight_details(flight_number):
    """Get detailed information about a specific flight"""
    flight = Flight.query.filter_by(flight_number=flight_number).first()
    
    if not flight:
        return jsonify({"error": "Flight not found"}), 404
    
    # Get status history
    status_history = FlightStatus.query.filter_by(flight_id=flight.id).order_by(
        FlightStatus.updated_at.desc()
    ).all()
    
    result = {
        "flight_number": flight.flight_number,
        "source": {
            "code": flight.source.code,
            "name": flight.source.name,
            "city": flight.source.city
        },
        "destination": {
            "code": flight.destination.code,
            "name": flight.destination.name,
            "city": flight.destination.city
        },
        "duration": flight.duration,
        "price": flight.price,
        "delay_prob": flight.delay_prob,
        "status": flight.status,
        "departure_time": flight.departure_time,
        "arrival_time": flight.arrival_time,
        "aircraft_type": flight.aircraft_type,
        "max_capacity": flight.max_capacity,
        "current_bookings": len(flight.bookings),
        "availability": flight.max_capacity - len(flight.bookings),
        "status_history": [
            {
                "status": status.status,
                "delay_minutes": status.delay_minutes,
                "reason": status.reason,
                "updated_at": status.updated_at.isoformat()
            } for status in status_history
        ]
    }
    
    return jsonify(result)

@flights_blueprint.route('/<flight_number>/status', methods=['POST'])
def update_flight_status(flight_number):
    """Update flight status (delay, cancellation, etc.)"""
    try:
        data = request.json
        flight = Flight.query.filter_by(flight_number=flight_number).first()
        
        if not flight:
            return jsonify({"error": "Flight not found"}), 404
        
        status = data.get('status')  # delayed, cancelled, on_time
        delay_minutes = data.get('delay_minutes', 0)
        reason = data.get('reason', '')
        
        if not status:
            return jsonify({"error": "Status is required"}), 400
        
        # Create status update record
        status_update = FlightStatus(
            flight_id=flight.id,
            status=status,
            delay_minutes=delay_minutes,
            reason=reason
        )
        db.session.add(status_update)
        
        # Update flight status
        flight.status = status
        
        db.session.commit()
        
        # Handle network updates for delays/cancellations
        if status == 'cancelled':
            flight_network.handle_flight_cancellation(flight_number)
        elif status == 'delayed':
            flight_network.handle_flight_delay(flight_number, delay_minutes)
        
        return jsonify({
            "message": f"Flight {flight_number} status updated to {status}",
            "flight_number": flight_number,
            "new_status": status,
            "delay_minutes": delay_minutes
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500

@flights_blueprint.route('/search', methods=['GET'])
def search_flights():
    """Search flights by various criteria"""
    source = request.args.get('source')
    destination = request.args.get('destination')
    max_price = request.args.get('max_price', type=float)
    max_duration = request.args.get('max_duration', type=float)
    status = request.args.get('status')
    
    query = Flight.query
    
    if source:
        query = query.join(Flight.source).filter(Airport.code == source.upper())
    
    if destination:
        query = query.join(Flight.destination).filter(Airport.code == destination.upper())
    
    if max_price:
        query = query.filter(Flight.price <= max_price)
    
    if max_duration:
        query = query.filter(Flight.duration <= max_duration)
    
    if status:
        query = query.filter(Flight.status == status)
    
    flights = query.all()
    
    result = [
        {
            "flight_number": f.flight_number,
            "source": f.source.code,
            "destination": f.destination.code,
            "duration": f.duration,
            "price": f.price,
            "delay_prob": f.delay_prob,
            "status": f.status,
            "availability": f.max_capacity - len(f.bookings)
        } for f in flights
    ]
    
    return jsonify({
        "flights": result,
        "count": len(result),
        "search_criteria": {
            "source": source,
            "destination": destination,
            "max_price": max_price,
            "max_duration": max_duration,
            "status": status
        }
    })

@flights_blueprint.route('/airports', methods=['GET'])
def get_airports():
    """Get all airports in the system"""
    airports = Airport.query.all()
    result = [
        {
            "id": a.id,
            "code": a.code,
            "name": a.name,
            "city": a.city,
            "latitude": a.latitude,
            "longitude": a.longitude,
            "timezone": a.timezone
        } for a in airports
    ]
    return jsonify(result)

@flights_blueprint.route('/airports/add', methods=['POST'])
def add_airport():
    """Add a new airport to the system"""
    try:
        data = request.json
        required_fields = ['code', 'name', 'city']
        
        for field in required_fields:
            if field not in data:
                return jsonify({"error": f"Missing required field: {field}"}), 400
        
        # Check if airport code already exists
        existing = Airport.query.filter_by(code=data['code'].upper()).first()
        if existing:
            return jsonify({"error": "Airport code already exists"}), 400
        
        data['code'] = data['code'].upper()
        new_airport = Airport(**data)
        db.session.add(new_airport)
        db.session.commit()
        
        # Rebuild network to include new airport
        flight_network.build_network()
        
        return jsonify({
            "message": "Airport added successfully",
            "airport": {
                "id": new_airport.id,
                "code": new_airport.code,
                "name": new_airport.name,
                "city": new_airport.city
            }
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500
