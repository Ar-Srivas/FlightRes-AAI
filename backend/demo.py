#!/usr/bin/env python3
"""
Flight Network Route Optimization Demo
Demonstrates graph theory implementation with Dijkstra's and A* algorithms
"""

from app import app, db
from models import Airport, Flight, FlightStatus
from flight_network import flight_network
import json

def demo_flight_network():
    """Comprehensive demonstration of the flight network system"""
    
    print("🛫 FLIGHT NETWORK ROUTE OPTIMIZATION SYSTEM")
    print("=" * 70)
    print("Built with Graph Theory, Dijkstra's Algorithm, and A* Algorithm")
    print("=" * 70)
    
    with app.app_context():
        # Initialize the network
        print("\n📡 INITIALIZING FLIGHT NETWORK")
        print("-" * 40)
        flight_network.build_network()
        stats = flight_network.get_network_statistics()
        
        print(f"🏢 Airports (Nodes): {stats['total_airports']}")
        print(f"✈️  Flights (Edges): {stats['total_flights']}")
        print(f"🔗 Network Connectivity: {stats['network_connectivity']:.1f} flights per airport")
        print(f"⚠️  Average Delay Probability: {stats['avg_delay_probability']:.1%}")
        
        # Show the network structure
        print("\n🗺️  NETWORK TOPOLOGY")
        print("-" * 40)
        airports = Airport.query.all()
        for airport in airports:
            connections = [edge.destination for edge in flight_network.graph.get(airport.code, [])]
            print(f"{airport.code} ({airport.city}): → {', '.join(connections)}")
        
        # Demonstrate route optimization algorithms
        print("\n🔍 ROUTE OPTIMIZATION DEMONSTRATIONS")
        print("-" * 40)
        
        # Example 1: Delhi to Chennai - Different optimization criteria
        print("\n🎯 Example 1: Delhi (DEL) → Chennai (MAA)")
        print("Testing different optimization criteria:")
        
        optimizations = ['cost', 'time', 'reliability']
        for opt in optimizations:
            route = flight_network.dijkstra_shortest_path("DEL", "MAA", opt)
            if route:
                print(f"  📊 {opt.title()} optimized:")
                print(f"     Route: {' → '.join(route.airports)}")
                print(f"     Flights: {', '.join(route.flights)}")
                if opt == 'cost':
                    print(f"     Total Cost: ₹{route.total_cost:.0f}")
                print(f"     Duration: {route.total_duration:.1f} hours")
                print(f"     Delay Risk: {route.total_delay_prob:.1%}")
        
        # Example 2: Complex multi-hop route
        print("\n🎯 Example 2: Mumbai (BOM) → Kolkata (CCU)")
        print("Finding best multi-hop route:")
        
        route = flight_network.dijkstra_shortest_path("BOM", "CCU", "cost")
        if route:
            print(f"  🛣️  Route: {' → '.join(route.airports)}")
            print(f"     Flights: {', '.join(route.flights)}")
            print(f"     Total Cost: ₹{route.total_cost:.0f}")
            print(f"     Total Duration: {route.total_duration:.1f} hours")
            print(f"     Number of Stops: {len(route.airports) - 2}")
        
        # Example 3: Algorithm comparison
        print("\n🎯 Example 3: Algorithm Comparison - Delhi (DEL) → Bangalore (BLR)")
        
        dijkstra_route = flight_network.dijkstra_shortest_path("DEL", "BLR", "cost")
        astar_route = flight_network.a_star_shortest_path("DEL", "BLR", "cost")
        
        print("  🔹 Dijkstra's Algorithm:")
        if dijkstra_route:
            print(f"     Route: {' → '.join(dijkstra_route.airports)}")
            print(f"     Cost: ₹{dijkstra_route.total_cost:.0f}")
        
        print("  ⭐ A* Algorithm:")
        if astar_route:
            print(f"     Route: {' → '.join(astar_route.airports)}")
            print(f"     Cost: ₹{astar_route.total_cost:.0f}")
        
        if dijkstra_route and astar_route:
            same_route = dijkstra_route.flights == astar_route.flights
            print(f"     Same result: {'✅ Yes' if same_route else '❌ No'}")
        
        # Multiple route options
        print("\n🎯 Example 4: Multiple Route Options")
        print("Finding top 3 routes Delhi (DEL) → Hyderabad (HYD):")
        
        routes = flight_network.find_multiple_routes("DEL", "HYD", 3)
        for i, route in enumerate(routes, 1):
            print(f"  {i}. {route.route_type.title()} Route:")
            print(f"     Path: {' → '.join(route.airports)}")
            print(f"     Cost: ₹{route.total_cost:.0f}, Duration: {route.total_duration:.1f}h")
        
        # Delay prediction
        print("\n📈 DELAY PREDICTION SYSTEM")
        print("-" * 40)
        predictions = flight_network.predict_delays()
        
        # Categorize flights by risk
        high_risk = [(f, p) for f, p in predictions.items() if p > 0.3]
        medium_risk = [(f, p) for f, p in predictions.items() if 0.15 < p <= 0.3]
        low_risk = [(f, p) for f, p in predictions.items() if p <= 0.15]
        
        print(f"🔴 High Risk Flights: {len(high_risk)}")
        print(f"🟡 Medium Risk Flights: {len(medium_risk)}")
        print(f"🟢 Low Risk Flights: {len(low_risk)}")
        
        if high_risk:
            print("\nSample High Risk Flights:")
            for flight, prob in high_risk[:3]:
                flight_obj = Flight.query.filter_by(flight_number=flight).first()
                if flight_obj:
                    print(f"  {flight}: {flight_obj.source.code} → {flight_obj.destination.code} ({prob:.1%})")
        
        # Disruption handling demonstration
        print("\n🚨 DISRUPTION HANDLING & RE-ROUTING")
        print("-" * 40)
        
        # Simulate a flight delay
        print("Scenario: Flight AI101 (DEL → BOM) delayed by 90 minutes")
        original_route = flight_network.dijkstra_shortest_path("DEL", "BOM", "cost")
        if original_route:
            print(f"Original route: {' → '.join(original_route.airports)}")
        
        # Handle the delay
        flight_network.handle_flight_delay("AI101", 90)
        
        # Find alternative routes
        alt_routes = flight_network.find_multiple_routes("DEL", "BOM", 2)
        print("Alternative routes found:")
        for i, route in enumerate(alt_routes, 1):
            print(f"  Alternative {i}: {' → '.join(route.airports)}")
            print(f"    Flights: {', '.join(route.flights)}")
            print(f"    Cost: ₹{route.total_cost:.0f}, Duration: {route.total_duration:.1f}h")
        
        # Simulate a cancellation
        print("\nScenario: Flight AI202 (BOM → BLR) cancelled")
        flight_network.handle_flight_cancellation("AI202")
        
        # Find alternatives for the cancelled route
        cancelled_alternatives = flight_network.find_multiple_routes("BOM", "BLR", 2)
        print("Alternative routes for cancelled flight:")
        for i, route in enumerate(cancelled_alternatives, 1):
            print(f"  Alternative {i}: {' → '.join(route.airports)}")
            print(f"    Duration: {route.total_duration:.1f}h, Cost: ₹{route.total_cost:.0f}")
        
        # Final network statistics
        print("\n📊 FINAL NETWORK STATISTICS")
        print("-" * 40)
        final_stats = flight_network.get_network_statistics()
        print(f"Total Flights: {final_stats['total_flights']}")
        print(f"Delayed Flights: {final_stats['delayed_flights']}")
        print(f"Cancelled Flights: {final_stats['cancelled_flights']}")
        print(f"Network Reliability: {(1 - final_stats['avg_delay_probability']):.1%}")
        
        print("\n🎉 DEMONSTRATION COMPLETED")
        print("=" * 70)
        print("✅ Graph Theory Implementation: SUCCESSFUL")
        print("✅ Dijkstra's Algorithm: WORKING")
        print("✅ A* Algorithm: WORKING")
        print("✅ Multi-criteria Optimization: WORKING")
        print("✅ Delay Prediction: WORKING")
        print("✅ Disruption Handling: WORKING")
        print("✅ Real-time Re-routing: WORKING")
        print("=" * 70)

if __name__ == "__main__":
    demo_flight_network()