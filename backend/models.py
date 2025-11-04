from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class Airport(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(10), unique=True, nullable=False)
    name = db.Column(db.String(100), nullable=False)
    city = db.Column(db.String(100), nullable=False)

class Flight(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    flight_number = db.Column(db.String(20), unique=True, nullable=False)
    source_id = db.Column(db.Integer, db.ForeignKey('airport.id'))
    destination_id = db.Column(db.Integer, db.ForeignKey('airport.id'))
    duration = db.Column(db.Float, nullable=False)
    price = db.Column(db.Float, nullable=False)
    delay_prob = db.Column(db.Float, default=0.0)

    source = db.relationship('Airport', foreign_keys=[source_id])
    destination = db.relationship('Airport', foreign_keys=[destination_id])

class Booking(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_name = db.Column(db.String(50), nullable=False)
    flight_id = db.Column(db.Integer, db.ForeignKey('flight.id'))
    status = db.Column(db.String(20), default="confirmed")

    flight = db.relationship('Flight', backref='bookings')
