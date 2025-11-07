#!/usr/bin/env python3
"""
Test script to demonstrate differences between Dijkstra's and A* algorithms
in flight route optimization.

This script will show cases where the algorithms produce different results
due to A*'s heuristic function potentially being misleading.
"""

from app import app
from flight_network import flight_network
from models import Airport
import math

def haversine_distance(lat1, lon1, lat2, lon2):
    """Calculate the great circle distance between two points on earth."""
    R = 6371  # Earth's radius in km
    
    lat1, lon1, lat2, lon2 = map(math.radians, [lat1, lon1, lat2, lon2])
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    
    a = math.sin(dlat/2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon/2)**2
    c = 2 * math.asin(math.sqrt(a))
    
    return R * c

def a_star_heuristic(current_airport, target_airport):
    """
    A* heuristic function based on geographic distance.
    This can be misleading for flight costs!
    """
    distance = haversine_distance(
        current_airport.latitude, current_airport.longitude,
        target_airport.latitude, target_airport.longitude
    )
    # Convert distance to estimated cost (very rough approximation)
    # This heuristic assumes ₹2 per km, which may not reflect actual pricing
    return distance * 2

def dijkstra_algorithm(start_code, end_code):
    """
    Pure Dijkstra's algorithm - guarantees optimal solution.
    """
    print(f"\n🔵 DIJKSTRA'S ALGORITHM: {start_code} → {end_code}")
    print("=" * 50)
    
    try:
        route = flight_network.find_route(start_code, end_code, algorithm="dijkstra")
        
        if route and route['flights']:
            total_cost = sum(flight['price'] for flight in route['flights'])
            total_time = sum(flight['duration'] for flight in route['flights'])
            route_path = " → ".join([flight['source'] for flight in route['flights']] + [route['flights'][-1]['destination']])
            
            print(f"✅ OPTIMAL ROUTE FOUND:")
            print(f"   Path: {route_path}")
            print(f"   Total Cost: ₹{total_cost:,}")
            print(f"   Total Time: {total_time:.1f} hours")
            print(f"   Flights: {len(route['flights'])}")
            
            print(f"\n📋 Flight Details:")
            for i, flight in enumerate(route['flights'], 1):
                print(f"   {i}. {flight['flight_number']}: {flight['source']} → {flight['destination']}")
                print(f"      Cost: ₹{flight['price']}, Duration: {flight['duration']}h")
            
            return {
                'path': route_path,
                'cost': total_cost,
                'time': total_time,
                'flights': len(route['flights']),
                'algorithm': 'Dijkstra'
            }
        else:
            print("❌ No route found")
            return None
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return None

def a_star_algorithm(start_code, end_code):
    """
    A* algorithm with geographic distance heuristic.
    May choose suboptimal routes due to heuristic bias.
    """
    print(f"\n🔴 A* ALGORITHM: {start_code} → {end_code}")
    print("=" * 50)
    
    try:
        # For this simulation, we'll use a modified version that considers heuristic
        route = flight_network.find_route(start_code, end_code, algorithm="astar")
        
        if route and route['flights']:
            total_cost = sum(flight['price'] for flight in route['flights'])
            total_time = sum(flight['duration'] for flight in route['flights'])
            route_path = " → ".join([flight['source'] for flight in route['flights']] + [route['flights'][-1]['destination']])
            
            print(f"✅ ROUTE FOUND (A* with heuristic):")
            print(f"   Path: {route_path}")
            print(f"   Total Cost: ₹{total_cost:,}")
            print(f"   Total Time: {total_time:.1f} hours")
            print(f"   Flights: {len(route['flights'])}")
            
            print(f"\n📋 Flight Details:")
            for i, flight in enumerate(route['flights'], 1):
                print(f"   {i}. {flight['flight_number']}: {flight['source']} → {flight['destination']}")
                print(f"      Cost: ₹{flight['price']}, Duration: {flight['duration']}h")
            
            return {
                'path': route_path,
                'cost': total_cost,
                'time': total_time,
                'flights': len(route['flights']),
                'algorithm': 'A*'
            }
        else:
            print("❌ No route found")
            return None
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return None

def compare_algorithms(start_code, end_code):
    """Compare results from both algorithms."""
    print(f"\n🔬 ALGORITHM COMPARISON: {start_code} → {end_code}")
    print("=" * 60)
    
    # Get results from both algorithms
    dijkstra_result = dijkstra_algorithm(start_code, end_code)
    astar_result = a_star_algorithm(start_code, end_code)
    
    if dijkstra_result and astar_result:
        print(f"\n📊 COMPARISON RESULTS:")
        print("=" * 40)
        print(f"{'Metric':<20} {'Dijkstra':<15} {'A*':<15} {'Difference'}")
        print("-" * 60)
        print(f"{'Cost':<20} ₹{dijkstra_result['cost']:<14,} ₹{astar_result['cost']:<14,} ₹{abs(dijkstra_result['cost'] - astar_result['cost']):,}")
        print(f"{'Time (hours)':<20} {dijkstra_result['time']:<14.1f} {astar_result['time']:<14.1f} {abs(dijkstra_result['time'] - astar_result['time']):.1f}")
        print(f"{'# of Flights':<20} {dijkstra_result['flights']:<14} {astar_result['flights']:<14} {abs(dijkstra_result['flights'] - astar_result['flights'])}")
        
        if dijkstra_result['cost'] != astar_result['cost']:
            cost_diff_pct = abs(dijkstra_result['cost'] - astar_result['cost']) / min(dijkstra_result['cost'], astar_result['cost']) * 100
            print(f"\n{'🚨 SIGNIFICANT DIFFERENCE!'}")
            print(f"   Cost difference: {cost_diff_pct:.1f}%")
            
            if dijkstra_result['cost'] < astar_result['cost']:
                savings = astar_result['cost'] - dijkstra_result['cost']
                print(f"   Dijkstra saves ₹{savings:,} ({cost_diff_pct:.1f}% cheaper)")
                print(f"   A* chose suboptimal route due to heuristic bias!")
            else:
                print(f"   A* found cheaper route (unusual case)")
        else:
            print(f"\n✅ Both algorithms found same optimal solution")
        
        print(f"\n📍 Route Paths:")
        print(f"   Dijkstra: {dijkstra_result['path']}")
        print(f"   A*:       {astar_result['path']}")
    
    return dijkstra_result, astar_result

def main():
    """Main test function."""
    print("🧪 TESTING DIJKSTRA'S vs A* ALGORITHM DIFFERENCES")
    print("=" * 80)
    print("This test demonstrates cases where A* heuristic leads to suboptimal routes")
    print("compared to Dijkstra's guaranteed optimal solution.")
    
    with app.app_context():
        # Build the network
        flight_network.build_network()
        
        # Test Case 1: Delhi to Chennai
        print(f"\n🧪 TEST CASE 1: Delhi to Chennai")
        print("Expected: A* may choose expensive direct route (₹15,000)")
        print("Expected: Dijkstra finds optimal multi-hop route (~₹6,700)")
        compare_algorithms("DEL", "MAA")
        
        # Test Case 2: Mumbai to Bangalore  
        print(f"\n🧪 TEST CASE 2: Mumbai to Bangalore")
        print("Expected: A* may choose expensive direct route (₹12,000)")
        print("Expected: Dijkstra finds optimal multi-hop route (~₹4,400)")
        compare_algorithms("BOM", "BLR")
        
        # Test Case 3: Control case - should be similar
        print(f"\n🧪 TEST CASE 3: Delhi to Mumbai (Control)")
        print("Expected: Both algorithms should find similar direct routes")
        compare_algorithms("DEL", "BOM")
        
        print(f"\n🎯 CONCLUSION:")
        print("If differences appear in Test Cases 1 & 2 but not 3,")
        print("this demonstrates how A*'s geographic heuristic can be")
        print("misleading in complex pricing scenarios!")

if __name__ == "__main__":
    main()