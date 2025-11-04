from app import app, db
from models import Airport, Flight

with app.app_context():
    db.drop_all()
    db.create_all()

    # Seed airports
    a1 = Airport(code="DEL", name="Indira Gandhi Intl", city="Delhi")
    a2 = Airport(code="BOM", name="Chhatrapati Shivaji Intl", city="Mumbai")
    a3 = Airport(code="BLR", name="Kempegowda Intl", city="Bangalore")
    db.session.add_all([a1, a2, a3])
    db.session.commit()

    # Seed flights
    f1 = Flight(flight_number="AI101", source_id=a1.id, destination_id=a2.id, duration=2.0, price=4500, delay_prob=0.1)
    f2 = Flight(flight_number="AI202", source_id=a2.id, destination_id=a3.id, duration=1.5, price=3800, delay_prob=0.2)
    f3 = Flight(flight_number="AI303", source_id=a3.id, destination_id=a1.id, duration=2.5, price=4200, delay_prob=0.05)
    db.session.add_all([f1, f2, f3])
    db.session.commit()

    print("Database seeded successfully.")
