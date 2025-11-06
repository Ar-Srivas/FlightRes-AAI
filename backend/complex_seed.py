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
        # Adding more airports for complexity
        {"code": "AMD", "name": "Sardar Vallabhbhai Patel Intl", "city": "Ahmedabad", "latitude": 23.0726, "longitude": 72.6177, "timezone": "Asia/Kolkata"},
        {"code": "PNQ", "name": "Pune Airport", "city": "Pune", "latitude": 18.5821, "longitude": 73.9197, "timezone": "Asia/Kolkata"},
        {"code": "GOI", "name": "Goa Airport", "city": "Goa", "latitude": 15.3808, "longitude": 73.8314, "timezone": "Asia/Kolkata"},
        {"code": "JAI", "name": "Jaipur Airport", "city": "Jaipur", "latitude": 26.8167, "longitude": 75.8042, "timezone": "Asia/Kolkata"},
    ]
    
    airport_objects = []
    for airport_data in airports_data:
        airport = Airport(**airport_data)
        airport_objects.append(airport)
        db.session.add(airport)
    
    db.session.commit()

    # Create a COMPLEX flight network with NO DIRECT routes between many major airports
    # This will force multi-hop routing and make algorithms more interesting
    flights_data = [
        # Hub 1: Delhi (DEL) - Major northern hub
        {"flight_number": "AI101", "source_id": 1, "destination_id": 2, "duration": 2.0, "price": 4500, "delay_prob": 0.12, "departure_time": "08:00", "arrival_time": "10:00", "aircraft_type": "Boeing 737"},  # DEL->BOM
        {"flight_number": "AI102", "source_id": 1, "destination_id": 5, "duration": 2.3, "price": 4700, "delay_prob": 0.18, "departure_time": "16:30", "arrival_time": "18:48", "aircraft_type": "Airbus A320"},  # DEL->CCU
        {"flight_number": "AI103", "source_id": 1, "destination_id": 7, "duration": 1.5, "price": 3800, "delay_prob": 0.10, "departure_time": "11:00", "arrival_time": "12:30", "aircraft_type": "Boeing 737"},  # DEL->AMD
        {"flight_number": "AI104", "source_id": 1, "destination_id": 10, "duration": 1.2, "price": 3200, "delay_prob": 0.08, "departure_time": "14:00", "arrival_time": "15:12", "aircraft_type": "Airbus A320"},  # DEL->JAI
        
        # Hub 2: Mumbai (BOM) - Major western hub  
        {"flight_number": "AI201", "source_id": 2, "destination_id": 1, "duration": 2.0, "price": 4600, "delay_prob": 0.14, "departure_time": "07:00", "arrival_time": "09:00", "aircraft_type": "Boeing 737"},  # BOM->DEL
        {"flight_number": "AI202", "source_id": 2, "destination_id": 6, "duration": 1.3, "price": 3600, "delay_prob": 0.11, "departure_time": "10:15", "arrival_time": "11:33", "aircraft_type": "Airbus A320"},  # BOM->HYD
        {"flight_number": "AI203", "source_id": 2, "destination_id": 8, "duration": 0.5, "price": 2800, "delay_prob": 0.06, "departure_time": "13:00", "arrival_time": "13:30", "aircraft_type": "ATR 72"},  # BOM->PNQ
        {"flight_number": "AI204", "source_id": 2, "destination_id": 9, "duration": 1.2, "price": 3400, "delay_prob": 0.09, "departure_time": "15:45", "arrival_time": "17:03", "aircraft_type": "Boeing 737"},  # BOM->GOI
        
        # Hub 3: Bangalore (BLR) - Major southern hub (NO direct to Delhi!)
        {"flight_number": "AI301", "source_id": 3, "destination_id": 4, "duration": 1.0, "price": 3200, "delay_prob": 0.08, "departure_time": "12:30", "arrival_time": "13:30", "aircraft_type": "Boeing 737"},  # BLR->MAA
        {"flight_number": "AI302", "source_id": 3, "destination_id": 6, "duration": 1.2, "price": 3400, "delay_prob": 0.10, "departure_time": "19:15", "arrival_time": "20:27", "aircraft_type": "Airbus A320"},  # BLR->HYD
        {"flight_number": "AI303", "source_id": 3, "destination_id": 9, "duration": 1.8, "price": 4200, "delay_prob": 0.13, "departure_time": "09:00", "arrival_time": "10:48", "aircraft_type": "Boeing 737"},  # BLR->GOI
        
        # Hub 4: Chennai (MAA) - Eastern coastal hub (NO direct to Delhi or Mumbai!)
        {"flight_number": "AI401", "source_id": 4, "destination_id": 3, "duration": 1.0, "price": 3300, "delay_prob": 0.06, "departure_time": "14:45", "arrival_time": "15:45", "aircraft_type": "Boeing 737"},  # MAA->BLR
        {"flight_number": "AI402", "source_id": 4, "destination_id": 5, "duration": 1.8, "price": 4000, "delay_prob": 0.15, "departure_time": "11:30", "arrival_time": "13:18", "aircraft_type": "Airbus A320"},  # MAA->CCU
        {"flight_number": "AI403", "source_id": 4, "destination_id": 6, "duration": 1.5, "price": 3800, "delay_prob": 0.11, "departure_time": "17:00", "arrival_time": "18:30", "aircraft_type": "Boeing 737"},  # MAA->HYD
        
        # Hub 5: Kolkata (CCU) - Eastern hub (connects to Delhi)
        {"flight_number": "AI501", "source_id": 5, "destination_id": 1, "duration": 2.3, "price": 4800, "delay_prob": 0.19, "departure_time": "08:15", "arrival_time": "10:33", "aircraft_type": "Boeing 737"},  # CCU->DEL
        {"flight_number": "AI502", "source_id": 5, "destination_id": 4, "duration": 1.8, "price": 4100, "delay_prob": 0.14, "departure_time": "16:00", "arrival_time": "17:48", "aircraft_type": "Airbus A320"},  # CCU->MAA
        {"flight_number": "AI503", "source_id": 5, "destination_id": 6, "duration": 2.0, "price": 4400, "delay_prob": 0.12, "departure_time": "13:20", "arrival_time": "15:20", "aircraft_type": "Boeing 737"},  # CCU->HYD
        
        # Hub 6: Hyderabad (HYD) - Central hub (connects most places)
        {"flight_number": "AI601", "source_id": 6, "destination_id": 2, "duration": 1.3, "price": 3700, "delay_prob": 0.11, "departure_time": "18:45", "arrival_time": "20:03", "aircraft_type": "Airbus A320"},  # HYD->BOM
        {"flight_number": "AI602", "source_id": 6, "destination_id": 3, "duration": 1.2, "price": 3500, "delay_prob": 0.07, "departure_time": "15:00", "arrival_time": "16:12", "aircraft_type": "Boeing 737"},  # HYD->BLR
        {"flight_number": "AI603", "source_id": 6, "destination_id": 4, "duration": 1.5, "price": 3800, "delay_prob": 0.09, "departure_time": "06:30", "arrival_time": "08:00", "aircraft_type": "Airbus A320"},  # HYD->MAA
        {"flight_number": "AI604", "source_id": 6, "destination_id": 5, "duration": 2.0, "price": 4500, "delay_prob": 0.13, "departure_time": "12:00", "arrival_time": "14:00", "aircraft_type": "Airbus A320"},  # HYD->CCU
        {"flight_number": "AI605", "source_id": 6, "destination_id": 7, "duration": 1.8, "price": 4000, "delay_prob": 0.14, "departure_time": "20:00", "arrival_time": "21:48", "aircraft_type": "Boeing 737"},  # HYD->AMD
        
        # Secondary hub: Ahmedabad (AMD) - Western Gujarat hub
        {"flight_number": "AI701", "source_id": 7, "destination_id": 1, "duration": 1.5, "price": 3900, "delay_prob": 0.12, "departure_time": "14:30", "arrival_time": "16:00", "aircraft_type": "Boeing 737"},  # AMD->DEL
        {"flight_number": "AI702", "source_id": 7, "destination_id": 6, "duration": 1.8, "price": 4100, "delay_prob": 0.15, "departure_time": "22:15", "arrival_time": "00:03", "aircraft_type": "Airbus A320"},  # AMD->HYD
        {"flight_number": "AI703", "source_id": 7, "destination_id": 8, "duration": 0.8, "price": 2600, "delay_prob": 0.05, "departure_time": "10:00", "arrival_time": "10:48", "aircraft_type": "ATR 72"},  # AMD->PNQ
        
        # Regional: Pune (PNQ) - Close to Mumbai
        {"flight_number": "AI801", "source_id": 8, "destination_id": 2, "duration": 0.5, "price": 2900, "delay_prob": 0.07, "departure_time": "16:00", "arrival_time": "16:30", "aircraft_type": "ATR 72"},  # PNQ->BOM
        {"flight_number": "AI802", "source_id": 8, "destination_id": 7, "duration": 0.8, "price": 2700, "delay_prob": 0.06, "departure_time": "12:00", "arrival_time": "12:48", "aircraft_type": "ATR 72"},  # PNQ->AMD
        {"flight_number": "AI803", "source_id": 8, "destination_id": 9, "duration": 1.5, "price": 3600, "delay_prob": 0.10, "departure_time": "08:30", "arrival_time": "10:00", "aircraft_type": "Boeing 737"},  # PNQ->GOI
        
        # Regional: Goa (GOI) - Tourist destination
        {"flight_number": "AI901", "source_id": 9, "destination_id": 2, "duration": 1.2, "price": 3500, "delay_prob": 0.08, "departure_time": "18:00", "arrival_time": "19:12", "aircraft_type": "Boeing 737"},  # GOI->BOM
        {"flight_number": "AI902", "source_id": 9, "destination_id": 3, "duration": 1.8, "price": 4300, "delay_prob": 0.12, "departure_time": "11:15", "arrival_time": "13:03", "aircraft_type": "Boeing 737"},  # GOI->BLR
        {"flight_number": "AI903", "source_id": 9, "destination_id": 8, "duration": 1.5, "price": 3700, "delay_prob": 0.09, "departure_time": "14:30", "arrival_time": "16:00", "aircraft_type": "Boeing 737"},  # GOI->PNQ
        
        # Regional: Jaipur (JAI) - Close to Delhi
        {"flight_number": "AI1001", "source_id": 10, "destination_id": 1, "duration": 1.2, "price": 3300, "delay_prob": 0.09, "departure_time": "17:00", "arrival_time": "18:12", "aircraft_type": "Airbus A320"},  # JAI->DEL
        
        # SPECIAL EXPENSIVE/COMPLEX ROUTES (for interesting comparisons)
        
        # Mumbai to Bangalore (requires layover via Hyderabad - NO DIRECT!)
        # BOM -> HYD -> BLR path available
        
        # Delhi to Chennai (requires layover via Kolkata - NO DIRECT!)  
        # DEL -> CCU -> MAA path available
        
        # Delhi to Bangalore (requires multiple layovers - NO DIRECT!)
        # Possible paths: DEL -> BOM -> HYD -> BLR or DEL -> CCU -> MAA -> BLR
        
        # Some premium/late night routes for variety
        {"flight_number": "AI951", "source_id": 2, "destination_id": 7, "duration": 1.0, "price": 5200, "delay_prob": 0.05, "departure_time": "23:30", "arrival_time": "00:30", "aircraft_type": "Boeing 737"},  # BOM->AMD (premium)
        {"flight_number": "AI952", "source_id": 3, "destination_id": 8, "duration": 2.5, "price": 5800, "delay_prob": 0.16, "departure_time": "02:00", "arrival_time": "04:30", "aircraft_type": "Airbus A320"},  # BLR->PNQ (red-eye)
        {"flight_number": "AI953", "source_id": 4, "destination_id": 9, "duration": 3.0, "price": 6200, "delay_prob": 0.20, "departure_time": "01:15", "arrival_time": "04:15", "aircraft_type": "Boeing 737"},  # MAA->GOI (expensive)
    ]
    
    for flight_data in flights_data:
        flight = Flight(**flight_data)
        db.session.add(flight)
    
    db.session.commit()
    
    # Build the flight network
    flight_network.build_network()
    stats = flight_network.get_network_statistics()

    print("🛫 COMPLEX FLIGHT NETWORK CREATED! 🛫")
    print("=" * 50)
    print(f"✅ Network Statistics: {stats}")
    print("\n🚫 NO DIRECT ROUTES FOR:")
    print("   • DEL ↔ BLR (requires 2+ hops)")
    print("   • DEL ↔ MAA (via CCU)")  
    print("   • BOM ↔ BLR (via HYD)")
    print("   • BOM ↔ MAA (via HYD)")
    print("   • BOM ↔ CCU (via DEL or HYD)")
    print("   • BLR ↔ CCU (via MAA or HYD)")
    print("\n🔗 MULTI-HOP SCENARIOS:")
    print("   • DEL → BLR: DEL→BOM→HYD→BLR or DEL→CCU→MAA→BLR")
    print("   • BOM → MAA: BOM→HYD→MAA") 
    print("   • DEL → GOI: DEL→BOM→GOI")
    print("   • CCU → GOI: CCU→HYD→BOM→GOI")
    print("\n🎯 ALGORITHM OPTIMIZATION:")
    print("   • Dijkstra's will find guaranteed optimal multi-hop routes")
    print("   • A* will use heuristics for faster pathfinding")
    print("   • Cost vs Time vs Reliability trade-offs will be significant")
    print("\n📊 ROUTE COMPLEXITY:")
    print(f"   • Total airports: {len(airports_data)}")
    print(f"   • Total flights: {len(flights_data)}")
    print("   • Hub structure: DEL, BOM, HYD as major hubs")
    print("   • Regional connections via AMD, PNQ, GOI, JAI")
    print("\n🔧 Ready for advanced graph algorithms!")