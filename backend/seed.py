from app import app, db
from models import Airport, Flight
from flight_network import flight_network

with app.app_context():
    db.drop_all()
    db.create_all()

    # Seed airports with coordinates
    airports_data = [
        {"code": "DEL", "name": "Indira Gandhi Intl", "city": "Delhi", "latitude": 28.5562, "longitude": 77.1000, "timezone": "Asia/Delhi"},
        {"code": "BOM", "name": "Chhatrapati Shivaji Intl", "city": "Mumbai", "latitude": 19.0896, "longitude": 72.8656, "timezone": "Asia/Kolkata"},
        {"code": "BLR", "name": "Kempegowda Intl", "city": "Bangalore", "latitude": 12.9716, "longitude": 77.5946, "timezone": "Asia/Kolkata"},
        {"code": "MAA", "name": "Chennai Intl", "city": "Chennai", "latitude": 12.9941, "longitude": 80.1709, "timezone": "Asia/Kolkata"},
        {"code": "CCU", "name": "Netaji Subhash Chandra Bose Intl", "city": "Kolkata", "latitude": 22.6549, "longitude": 88.4462, "timezone": "Asia/Kolkata"},
        {"code": "HYD", "name": "Rajiv Gandhi Intl", "city": "Hyderabad", "latitude": 17.2403, "longitude": 78.4294, "timezone": "Asia/Kolkata"},
    ]
    
    airport_objects = []
    for airport_data in airports_data:
        airport = Airport(**airport_data)
        airport_objects.append(airport)
        db.session.add(airport)
    
    db.session.commit()

    # Create a more comprehensive flight network
    flights_data = [
        # From Delhi (DEL)
        {"flight_number": "AI101", "source_id": 1, "destination_id": 2, "duration": 2.0, "price": 4500, "delay_prob": 0.1, "departure_time": "08:00", "arrival_time": "10:00", "aircraft_type": "Boeing 737"},
        {"flight_number": "AI102", "source_id": 1, "destination_id": 3, "duration": 2.5, "price": 5200, "delay_prob": 0.15, "departure_time": "09:30", "arrival_time": "12:00", "aircraft_type": "Airbus A320"},
        {"flight_number": "AI103", "source_id": 1, "destination_id": 4, "duration": 2.2, "price": 4800, "delay_prob": 0.12, "departure_time": "14:00", "arrival_time": "16:12", "aircraft_type": "Boeing 737"},
        {"flight_number": "AI104", "source_id": 1, "destination_id": 5, "duration": 2.3, "price": 4700, "delay_prob": 0.18, "departure_time": "16:30", "arrival_time": "18:48", "aircraft_type": "Airbus A320"},
        {"flight_number": "AI105", "source_id": 1, "destination_id": 6, "duration": 1.8, "price": 4200, "delay_prob": 0.08, "departure_time": "11:00", "arrival_time": "12:48", "aircraft_type": "Boeing 737"},
        
        # From Mumbai (BOM)
        {"flight_number": "AI201", "source_id": 2, "destination_id": 1, "duration": 2.0, "price": 4600, "delay_prob": 0.14, "departure_time": "07:00", "arrival_time": "09:00", "aircraft_type": "Boeing 737"},
        {"flight_number": "AI202", "source_id": 2, "destination_id": 3, "duration": 1.5, "price": 3800, "delay_prob": 0.2, "departure_time": "13:00", "arrival_time": "14:30", "aircraft_type": "Airbus A320"},
        {"flight_number": "AI203", "source_id": 2, "destination_id": 4, "duration": 2.3, "price": 5000, "delay_prob": 0.16, "departure_time": "15:45", "arrival_time": "18:03", "aircraft_type": "Boeing 737"},
        {"flight_number": "AI204", "source_id": 2, "destination_id": 6, "duration": 1.3, "price": 3600, "delay_prob": 0.1, "departure_time": "10:15", "arrival_time": "11:33", "aircraft_type": "Airbus A320"},
        
        # From Bangalore (BLR)
        {"flight_number": "AI301", "source_id": 3, "destination_id": 1, "duration": 2.5, "price": 5100, "delay_prob": 0.05, "departure_time": "06:30", "arrival_time": "09:00", "aircraft_type": "Boeing 737"},
        {"flight_number": "AI302", "source_id": 3, "destination_id": 2, "duration": 1.5, "price": 3900, "delay_prob": 0.12, "departure_time": "17:00", "arrival_time": "18:30", "aircraft_type": "Airbus A320"},
        {"flight_number": "AI303", "source_id": 3, "destination_id": 4, "duration": 1.0, "price": 3200, "delay_prob": 0.08, "departure_time": "12:30", "arrival_time": "13:30", "aircraft_type": "Boeing 737"},
        {"flight_number": "AI304", "source_id": 3, "destination_id": 6, "duration": 1.2, "price": 3400, "delay_prob": 0.1, "departure_time": "19:15", "arrival_time": "20:27", "aircraft_type": "Airbus A320"},
        
        # From Chennai (MAA)
        {"flight_number": "AI401", "source_id": 4, "destination_id": 1, "duration": 2.2, "price": 4900, "delay_prob": 0.13, "departure_time": "05:45", "arrival_time": "07:57", "aircraft_type": "Boeing 737"},
        {"flight_number": "AI402", "source_id": 4, "destination_id": 2, "duration": 2.3, "price": 5100, "delay_prob": 0.17, "departure_time": "20:00", "arrival_time": "22:18", "aircraft_type": "Airbus A320"},
        {"flight_number": "AI403", "source_id": 4, "destination_id": 3, "duration": 1.0, "price": 3300, "delay_prob": 0.06, "departure_time": "14:45", "arrival_time": "15:45", "aircraft_type": "Boeing 737"},
        {"flight_number": "AI404", "source_id": 4, "destination_id": 5, "duration": 1.8, "price": 4000, "delay_prob": 0.15, "departure_time": "11:30", "arrival_time": "13:18", "aircraft_type": "Airbus A320"},
        
        # From Kolkata (CCU)
        {"flight_number": "AI501", "source_id": 5, "destination_id": 1, "duration": 2.3, "price": 4800, "delay_prob": 0.19, "departure_time": "08:15", "arrival_time": "10:33", "aircraft_type": "Boeing 737"},
        {"flight_number": "AI502", "source_id": 5, "destination_id": 4, "duration": 1.8, "price": 4100, "delay_prob": 0.14, "departure_time": "16:00", "arrival_time": "17:48", "aircraft_type": "Airbus A320"},
        {"flight_number": "AI503", "source_id": 5, "destination_id": 6, "duration": 2.0, "price": 4400, "delay_prob": 0.11, "departure_time": "13:20", "arrival_time": "15:20", "aircraft_type": "Boeing 737"},
        
        # From Hyderabad (HYD)
        {"flight_number": "AI601", "source_id": 6, "destination_id": 1, "duration": 1.8, "price": 4300, "delay_prob": 0.09, "departure_time": "07:30", "arrival_time": "09:18", "aircraft_type": "Boeing 737"},
        {"flight_number": "AI602", "source_id": 6, "destination_id": 2, "duration": 1.3, "price": 3700, "delay_prob": 0.11, "departure_time": "18:45", "arrival_time": "20:03", "aircraft_type": "Airbus A320"},
        {"flight_number": "AI603", "source_id": 6, "destination_id": 3, "duration": 1.2, "price": 3500, "delay_prob": 0.07, "departure_time": "15:00", "arrival_time": "16:12", "aircraft_type": "Boeing 737"},
        {"flight_number": "AI604", "source_id": 6, "destination_id": 5, "duration": 2.0, "price": 4500, "delay_prob": 0.13, "departure_time": "12:00", "arrival_time": "14:00", "aircraft_type": "Airbus A320"},
    ]
    
    for flight_data in flights_data:
        flight = Flight(**flight_data)
        db.session.add(flight)
    
    db.session.commit()
    
    # Build the flight network
    flight_network.build_network()
    stats = flight_network.get_network_statistics()

    print("Database seeded successfully with enhanced flight network!")
    print(f"Network Statistics: {stats}")
    print("\nAvailable routes:")
    print("- Direct flights between major Indian cities")
    print("- Multi-hop routing capabilities")
    print("- Graph-based optimization algorithms ready")
    print("\nNew API endpoints available:")
    print("- POST /routes/build-network")
    print("- POST /routes/find")
    print("- POST /routes/handle-disruption")
    print("- GET /routes/delay-prediction")
    print("- GET /routes/network-stats")
