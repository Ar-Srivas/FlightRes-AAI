from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class Airport(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(10), unique=True, nullable=False)
    name = db.Column(db.String(100), nullable=False)
    city = db.Column(db.String(100), nullable=False)
    latitude = db.Column(db.Float, default=0.0)
    longitude = db.Column(db.Float, default=0.0)
    timezone = db.Column(db.String(50), default='UTC')

class Flight(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    flight_number = db.Column(db.String(20), unique=True, nullable=False)
    source_id = db.Column(db.Integer, db.ForeignKey('airport.id'))
    destination_id = db.Column(db.Integer, db.ForeignKey('airport.id'))
    duration = db.Column(db.Float, nullable=False)  # in hours
    price = db.Column(db.Float, nullable=False)
    delay_prob = db.Column(db.Float, default=0.0)  # probability of delay (0-1)
    status = db.Column(db.String(20), default='scheduled')  # scheduled, delayed, cancelled
    departure_time = db.Column(db.String(10), default='08:00')  # HH:MM format
    arrival_time = db.Column(db.String(10), default='10:00')    # HH:MM format
    aircraft_type = db.Column(db.String(50), default='Boeing 737')
    max_capacity = db.Column(db.Integer, default=180)

    source = db.relationship('Airport', foreign_keys=[source_id])
    destination = db.relationship('Airport', foreign_keys=[destination_id])

class FlightStatus(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    flight_id = db.Column(db.Integer, db.ForeignKey('flight.id'))
    status = db.Column(db.String(20), nullable=False)  # on_time, delayed, cancelled
    delay_minutes = db.Column(db.Integer, default=0)
    reason = db.Column(db.String(200))
    updated_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    flight = db.relationship('Flight', backref='status_updates')

class Route(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    source_airport_code = db.Column(db.String(10), nullable=False)
    destination_airport_code = db.Column(db.String(10), nullable=False)
    route_type = db.Column(db.String(20), nullable=False)  # cost, time, reliability
    total_cost = db.Column(db.Float, nullable=False)
    total_duration = db.Column(db.Float, nullable=False)
    total_delay_prob = db.Column(db.Float, default=0.0)
    airports_sequence = db.Column(db.Text)  # JSON string of airport codes
    flights_sequence = db.Column(db.Text)   # JSON string of flight numbers
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Booking(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_name = db.Column(db.String(50), nullable=False)
    flight_id = db.Column(db.Integer, db.ForeignKey('flight.id'))
    route_id = db.Column(db.Integer, db.ForeignKey('route.id'), nullable=True)
    status = db.Column(db.String(20), default="confirmed")
    booking_date = db.Column(db.DateTime, default=datetime.utcnow)
    
    flight = db.relationship('Flight', backref='bookings')
    route = db.relationship('Route', backref='bookings')
