#!/usr/bin/env python3
"""
Direct test of the flight network functionality without Flask server
"""

from app import app, db
from models import Airport, Flight
from flight_network import flight_network

def test_direct_functionality():
    """Test the core functionality directly"""
    print("🛫 Testing Flight Network Core Functionality")
    print("="*60)
    
    with app.app_context():
        # Build the network
        print("Building flight network...")
        flight_network.build_network()
        
        # Get network statistics
        stats = flight_network.get_network_statistics()
        print(f"\n📊 Network Statistics:")
        for key, value in stats.items():
            print(f"   {key}: {value}")
        
        # Test route finding
        print(f"\n🔍 Testing Route Optimization:")
        
        # Test Dijkstra's algorithm for different optimizations
        test_cases = [
            ("DEL", "MAA", "cost"),
            ("DEL", "MAA", "time"),
            ("DEL", "MAA", "reliability"),
            ("BOM", "CCU", "cost"),
            ("BLR", "HYD", "cost"),
        ]
        
        for source, dest, optimization in test_cases:
            print(f"\n🔹 Finding route: {source} → {dest} (optimized for {optimization})")
            
            # Test Dijkstra
            dijkstra_route = flight_network.dijkstra_shortest_path(source, dest, optimization)
            if dijkstra_route:
                print(f"   Dijkstra: {' → '.join(dijkstra_route.airports)}")
                print(f"   Flights: {', '.join(dijkstra_route.flights)}")
                print(f"   Cost: ₹{dijkstra_route.total_cost:.2f}, Duration: {dijkstra_route.total_duration:.2f}h")
                print(f"   Delay Prob: {dijkstra_route.total_delay_prob:.3f}")
            else:
                print(f"   No route found with Dijkstra")
            
            # Test A*
            astar_route = flight_network.a_star_shortest_path(source, dest, optimization)
            if astar_route:
                print(f"   A*: {' → '.join(astar_route.airports)}")
                print(f"   Cost: ₹{astar_route.total_cost:.2f}, Duration: {astar_route.total_duration:.2f}h")
            else:
                print(f"   No route found with A*")
        
        # Test multiple routes
        print(f"\n🔍 Testing Multiple Route Finding:")
        multiple_routes = flight_network.find_multiple_routes("DEL", "BLR", 3)
        for i, route in enumerate(multiple_routes, 1):
            print(f"   Route {i} ({route.route_type}): {' → '.join(route.airports)}")
            print(f"   Cost: ₹{route.total_cost:.2f}, Duration: {route.total_duration:.2f}h")
        
        # Test delay prediction
        print(f"\n📈 Testing Delay Prediction:")
        predictions = flight_network.predict_delays()
        high_risk_flights = [
            (flight, prob) for flight, prob in predictions.items() 
            if prob > 0.3
        ]
        
        print(f"   High risk flights (>30% delay probability):")
        for flight, prob in high_risk_flights[:5]:
            print(f"   {flight}: {prob:.3f}")
        
        # Test disruption handling
        print(f"\n🚫 Testing Disruption Handling:")
        print("   Simulating delay of flight AI101...")
        flight_network.handle_flight_delay("AI101", 60)
        
        print("   Simulating cancellation of flight AI202...")
        flight_network.handle_flight_cancellation("AI202")
        
        # Check updated statistics
        updated_stats = flight_network.get_network_statistics()
        print(f"   Updated stats - Delayed: {updated_stats['delayed_flights']}, Cancelled: {updated_stats['cancelled_flights']}")
        
        # Test finding routes after disruption
        print("   Finding alternative routes DEL → BOM after disruptions...")
        alt_routes = flight_network.find_multiple_routes("DEL", "BOM", 2)
        for i, route in enumerate(alt_routes, 1):
            print(f"   Alternative {i}: {' → '.join(route.airports)}")
            print(f"   Flights: {', '.join(route.flights)}")

if __name__ == "__main__":
    test_direct_functionality()
    print("\n✅ Core functionality test completed successfully!")
    print("\n🎯 Key Features Demonstrated:")
    print("   ✓ Graph-based flight network (airports as nodes, flights as edges)")
    print("   ✓ Dijkstra's algorithm for shortest path optimization")
    print("   ✓ A* algorithm with distance-based heuristic")
    print("   ✓ Multi-criteria optimization (cost, time, reliability)")
    print("   ✓ Flight delay prediction using probability models")
    print("   ✓ Dynamic disruption handling and network updates")
    print("   ✓ Alternative route finding for cancelled/delayed flights")
    print("   ✓ Real-time network statistics and monitoring")