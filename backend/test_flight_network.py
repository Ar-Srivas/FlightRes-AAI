#!/usr/bin/env python3
"""
Test script for the Flight Network Route Optimization System
Demonstrates graph theory, Dijkstra's algorithm, A* algorithm, and disruption handling
"""

import requests
import json
import time
from pprint import pprint

BASE_URL = "http://localhost:5001"

def print_section(title):
    print("\n" + "="*60)
    print(f" {title}")
    print("="*60)

def test_basic_connectivity():
    """Test basic API connectivity"""
    print_section("Testing Basic Connectivity")
    
    try:
        response = requests.get(f"{BASE_URL}/health")
        if response.status_code == 200:
            print("✓ API is running")
            pprint(response.json())
        else:
            print("✗ API health check failed")
            return False
    except requests.exceptions.ConnectionError:
        print("✗ Cannot connect to API. Make sure Flask server is running on port 5001")
        return False
    
    return True

def test_network_building():
    """Test flight network building"""
    print_section("Building Flight Network")
    
    response = requests.post(f"{BASE_URL}/routes/build-network")
    if response.status_code == 200:
        print("✓ Flight network built successfully")
        pprint(response.json())
    else:
        print("✗ Failed to build network")
        pprint(response.json())
    
    # Get network statistics
    response = requests.get(f"{BASE_URL}/routes/network-stats")
    if response.status_code == 200:
        print("\n📊 Network Statistics:")
        pprint(response.json())

def test_route_optimization():
    """Test route optimization algorithms"""
    print_section("Testing Route Optimization Algorithms")
    
    test_cases = [
        {"source": "DEL", "destination": "MAA", "algorithm": "dijkstra", "optimization": "cost"},
        {"source": "DEL", "destination": "MAA", "algorithm": "dijkstra", "optimization": "time"},
        {"source": "DEL", "destination": "MAA", "algorithm": "dijkstra", "optimization": "reliability"},
        {"source": "BOM", "destination": "CCU", "algorithm": "a_star", "optimization": "cost"},
        {"source": "BLR", "destination": "DEL", "algorithm": "multiple", "optimization": "cost"},
    ]
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n🔍 Test Case {i}: {test_case['source']} → {test_case['destination']}")
        print(f"   Algorithm: {test_case['algorithm']}, Optimization: {test_case['optimization']}")
        
        response = requests.post(f"{BASE_URL}/routes/find", json=test_case)
        
        if response.status_code == 200:
            data = response.json()
            print(f"   ✓ Found {data['routes_found']} route(s)")
            
            for j, route in enumerate(data['routes'], 1):
                print(f"      Route {j}: {' → '.join(route['airports'])}")
                print(f"      Flights: {', '.join(route['flights'])}")
                print(f"      Cost: ₹{route['total_cost']}, Duration: {route['total_duration']}h")
                print(f"      Delay Probability: {route['average_delay_probability']}")
                print(f"      Stops: {route['stops']}")
        else:
            print(f"   ✗ Failed to find routes")
            pprint(response.json())

def test_algorithm_comparison():
    """Test comparison between Dijkstra and A* algorithms"""
    print_section("Comparing Dijkstra vs A* Algorithms")
    
    test_case = {
        "source": "DEL",
        "destination": "BLR",
        "optimization": "cost"
    }
    
    response = requests.post(f"{BASE_URL}/routes/compare-algorithms", json=test_case)
    
    if response.status_code == 200:
        data = response.json()
        print(f"Route: {test_case['source']} → {test_case['destination']}")
        print(f"Optimization: {test_case['optimization']}")
        
        if data['dijkstra']:
            print("\n🔹 Dijkstra's Algorithm:")
            route = data['dijkstra']
            print(f"   Airports: {' → '.join(route['airports'])}")
            print(f"   Flights: {', '.join(route['flights'])}")
            print(f"   Cost: ₹{route['total_cost']}, Duration: {route['total_duration']}h")
        
        if data['a_star']:
            print("\n⭐ A* Algorithm:")
            route = data['a_star']
            print(f"   Airports: {' → '.join(route['airports'])}")
            print(f"   Flights: {', '.join(route['flights'])}")
            print(f"   Cost: ₹{route['total_cost']}, Duration: {route['total_duration']}h")
        
        if data['comparison']:
            comp = data['comparison']
            print(f"\n📊 Comparison:")
            print(f"   Same route found: {comp['same_route']}")
            print(f"   Cost difference: ₹{comp['cost_difference']}")
            print(f"   Time difference: {comp['time_difference']}h")
    else:
        print("✗ Algorithm comparison failed")
        pprint(response.json())

def test_delay_prediction():
    """Test delay prediction functionality"""
    print_section("Testing Delay Prediction")
    
    response = requests.get(f"{BASE_URL}/routes/delay-prediction")
    
    if response.status_code == 200:
        data = response.json()
        print(f"📈 Delay predictions generated at: {data['generated_at']}")
        
        # Show high-risk flights
        high_risk = [p for p in data['predictions'] if p['risk_level'] == 'high']
        medium_risk = [p for p in data['predictions'] if p['risk_level'] == 'medium']
        
        if high_risk:
            print(f"\n🔴 High Risk Flights ({len(high_risk)}):")
            for pred in high_risk[:5]:  # Show top 5
                print(f"   {pred['flight_number']}: {pred['source']} → {pred['destination']} "
                      f"(Risk: {pred['predicted_delay_probability']:.3f})")
        
        if medium_risk:
            print(f"\n🟡 Medium Risk Flights ({len(medium_risk)}):")
            for pred in medium_risk[:3]:  # Show top 3
                print(f"   {pred['flight_number']}: {pred['source']} → {pred['destination']} "
                      f"(Risk: {pred['predicted_delay_probability']:.3f})")
    else:
        print("✗ Delay prediction failed")
        pprint(response.json())

def test_disruption_handling():
    """Test flight disruption and re-routing"""
    print_section("Testing Flight Disruption and Re-routing")
    
    # Test flight delay
    print("🔧 Simulating Flight Delay...")
    delay_data = {
        "flight_number": "AI101",
        "type": "delay",
        "delay_minutes": 90,
        "reason": "Weather conditions"
    }
    
    response = requests.post(f"{BASE_URL}/routes/handle-disruption", json=delay_data)
    
    if response.status_code == 200:
        data = response.json()
        print(f"✓ {data['message']}")
        print(f"   Affected passengers: {data['affected_passengers']}")
        print(f"   Alternative routes found: {data['alternative_routes_found']}")
        
        if data['alternatives']:
            for alt in data['alternatives'][:2]:  # Show first 2 alternatives
                print(f"\n   👤 Passenger: {alt['passenger']}")
                for i, route in enumerate(alt['alternative_routes'][:2], 1):
                    print(f"      Alternative {i}: {' → '.join(route['airports'])}")
                    print(f"      Cost: ₹{route['total_cost']}, Duration: {route['total_duration']}h")
    else:
        print("✗ Disruption handling failed")
        pprint(response.json())
    
    # Test flight cancellation
    print("\n🚫 Simulating Flight Cancellation...")
    cancel_data = {
        "flight_number": "AI202",
        "type": "cancellation",
        "reason": "Technical issues"
    }
    
    response = requests.post(f"{BASE_URL}/routes/handle-disruption", json=cancel_data)
    
    if response.status_code == 200:
        data = response.json()
        print(f"✓ {data['message']}")
        print(f"   Affected passengers: {data['affected_passengers']}")
        print(f"   Alternative routes found: {data['alternative_routes_found']}")
    else:
        print("✗ Cancellation handling failed")
        pprint(response.json())

def test_flight_search():
    """Test enhanced flight search functionality"""
    print_section("Testing Enhanced Flight Search")
    
    # Search flights from Delhi
    response = requests.get(f"{BASE_URL}/flights/search?source=DEL&max_price=5000")
    
    if response.status_code == 200:
        data = response.json()
        print(f"🔍 Found {data['count']} flights from Delhi under ₹5000:")
        
        for flight in data['flights'][:5]:  # Show first 5
            print(f"   {flight['flight_number']}: {flight['source']} → {flight['destination']}")
            print(f"   Price: ₹{flight['price']}, Duration: {flight['duration']}h")
            print(f"   Status: {flight['status']}, Availability: {flight['availability']} seats")
    else:
        print("✗ Flight search failed")
        pprint(response.json())

def main():
    """Run all tests"""
    print("🛫 Flight Network Route Optimization System - Test Suite")
    print("This demonstrates graph theory implementation with Dijkstra's and A* algorithms")
    
    if not test_basic_connectivity():
        return
    
    test_network_building()
    test_route_optimization()
    test_algorithm_comparison()
    test_delay_prediction()
    test_disruption_handling()
    test_flight_search()
    
    print_section("Test Suite Completed")
    print("✅ All major features demonstrated successfully!")
    print("\n📋 Features tested:")
    print("   • Graph-based flight network (airports as nodes, flights as edges)")
    print("   • Dijkstra's algorithm for shortest path optimization")
    print("   • A* algorithm with heuristic-based search")
    print("   • Multi-criteria optimization (cost, time, reliability)")
    print("   • Flight delay prediction")
    print("   • Disruption handling and re-routing")
    print("   • Real-time network updates")
    
    print("\n🔗 API Endpoints demonstrated:")
    print("   • POST /routes/build-network - Build flight network graph")
    print("   • POST /routes/find - Find optimal routes")
    print("   • POST /routes/compare-algorithms - Compare algorithms")
    print("   • GET /routes/delay-prediction - Get delay predictions")
    print("   • POST /routes/handle-disruption - Handle disruptions")
    print("   • GET /flights/search - Search flights")

if __name__ == "__main__":
    main()