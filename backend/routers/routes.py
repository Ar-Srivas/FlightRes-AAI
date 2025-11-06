from flask import Blueprint, jsonify, request, make_response
from models import db, Flight, Airport, Route as RouteModel, FlightStatus
from flight_network import flight_network, Route
from map_visualization import create_route_map, create_network_overview_map, create_multiple_routes_comparison
import json
from datetime import datetime

routes_blueprint = Blueprint('routes', __name__, url_prefix='/routes')

@routes_blueprint.route('/build-network', methods=['POST'])
def build_network():
    """Build or rebuild the flight network graph"""
    try:
        flight_network.build_network()
        stats = flight_network.get_network_statistics()
        return jsonify({
            "message": "Flight network built successfully",
            "statistics": stats
        }), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@routes_blueprint.route('/find', methods=['POST'])
def find_optimal_routes():
    """Find optimal routes between two airports"""
    try:
        data = request.get_json()
        source = data.get('source')
        destination = data.get('destination')
        algorithm = data.get('algorithm', 'dijkstra')  # dijkstra or a_star
        optimization = data.get('optimization', 'cost')  # cost, time, reliability
        num_routes = data.get('num_routes', 3)
        
        if not source or not destination:
            return jsonify({"error": "Source and destination are required"}), 400
        
        # Ensure network is built
        flight_network.build_network()
        
        if algorithm == 'multiple':
            routes = flight_network.find_multiple_routes(source, destination, num_routes)
        elif algorithm == 'a_star':
            route = flight_network.a_star_shortest_path(source, destination, optimization)
            routes = [route] if route else []
        else:  # dijkstra
            route = flight_network.dijkstra_shortest_path(source, destination, optimization)
            routes = [route] if route else []
        
        if not routes:
            return jsonify({"message": "No routes found between the specified airports"}), 404
        
        # Save routes to database and format response
        result_routes = []
        for route in routes:
            # Save to database
            route_model = RouteModel(
                source_airport_code=source,
                destination_airport_code=destination,
                route_type=route.route_type,
                total_cost=route.total_cost,
                total_duration=route.total_duration,
                total_delay_prob=route.total_delay_prob,
                airports_sequence=json.dumps(route.airports),
                flights_sequence=json.dumps(route.flights)
            )
            db.session.add(route_model)
            
            result_routes.append({
                "route_type": route.route_type,
                "airports": route.airports,
                "flights": route.flights,
                "total_cost": round(route.total_cost, 2),
                "total_duration": round(route.total_duration, 2),
                "average_delay_probability": round(route.total_delay_prob, 3),
                "stops": len(route.airports) - 2  # Excluding source and destination
            })
        
        db.session.commit()
        
        return jsonify({
            "source": source,
            "destination": destination,
            "algorithm_used": algorithm,
            "optimization_criteria": optimization,
            "routes_found": len(result_routes),
            "routes": result_routes
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500

@routes_blueprint.route('/delay-prediction', methods=['GET'])
def get_delay_predictions():
    """Get delay predictions for all flights"""
    try:
        flight_network.build_network()
        predictions = flight_network.predict_delays()
        
        # Format predictions with flight details
        result = []
        for flight_number, delay_prob in predictions.items():
            flight = Flight.query.filter_by(flight_number=flight_number).first()
            if flight:
                result.append({
                    "flight_number": flight_number,
                    "source": flight.source.code,
                    "destination": flight.destination.code,
                    "predicted_delay_probability": round(delay_prob, 3),
                    "risk_level": "high" if delay_prob > 0.5 else "medium" if delay_prob > 0.2 else "low"
                })
        
        return jsonify({
            "predictions": result,
            "generated_at": datetime.utcnow().isoformat()
        }), 200
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@routes_blueprint.route('/handle-disruption', methods=['POST'])
def handle_flight_disruption():
    """Handle flight delays or cancellations and find alternative routes"""
    try:
        data = request.get_json()
        flight_number = data.get('flight_number')
        disruption_type = data.get('type')  # 'delay' or 'cancellation'
        delay_minutes = data.get('delay_minutes', 0)
        reason = data.get('reason', '')
        
        if not flight_number or not disruption_type:
            return jsonify({"error": "Flight number and disruption type are required"}), 400
        
        flight = Flight.query.filter_by(flight_number=flight_number).first()
        if not flight:
            return jsonify({"error": "Flight not found"}), 404
        
        # Record the disruption
        status_update = FlightStatus(
            flight_id=flight.id,
            status='cancelled' if disruption_type == 'cancellation' else 'delayed',
            delay_minutes=delay_minutes,
            reason=reason
        )
        db.session.add(status_update)
        
        # Update flight status
        flight.status = 'cancelled' if disruption_type == 'cancellation' else 'delayed'
        
        # Handle the disruption in the network
        if disruption_type == 'cancellation':
            flight_network.handle_flight_cancellation(flight_number)
        else:
            flight_network.handle_flight_delay(flight_number, delay_minutes)
        
        # Find affected bookings and suggest alternatives
        affected_bookings = flight.bookings
        alternatives = []
        
        for booking in affected_bookings:
            # Find alternative routes from source to destination
            alt_routes = flight_network.find_multiple_routes(
                flight.source.code, 
                flight.destination.code, 
                3
            )
            
            if alt_routes:
                alternatives.append({
                    "booking_id": booking.id,
                    "passenger": booking.user_name,
                    "alternative_routes": [{
                        "route_type": route.route_type,
                        "airports": route.airports,
                        "flights": route.flights,
                        "total_cost": round(route.total_cost, 2),
                        "total_duration": round(route.total_duration, 2),
                        "delay_probability": round(route.total_delay_prob, 3)
                    } for route in alt_routes]
                })
        
        db.session.commit()
        
        return jsonify({
            "message": f"Flight {flight_number} {disruption_type} handled successfully",
            "flight_number": flight_number,
            "disruption_type": disruption_type,
            "delay_minutes": delay_minutes if disruption_type == 'delay' else None,
            "affected_passengers": len(affected_bookings),
            "alternative_routes_found": len(alternatives),
            "alternatives": alternatives
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500

@routes_blueprint.route('/network-stats', methods=['GET'])
def get_network_statistics():
    """Get flight network statistics"""
    try:
        flight_network.build_network()
        stats = flight_network.get_network_statistics()
        
        # Add additional database statistics
        total_routes = RouteModel.query.count()
        total_disruptions = FlightStatus.query.count()
        recent_disruptions = FlightStatus.query.filter(
            FlightStatus.updated_at >= datetime.utcnow().replace(hour=0, minute=0, second=0)
        ).count()
        
        stats.update({
            "saved_routes": total_routes,
            "total_disruptions_recorded": total_disruptions,
            "disruptions_today": recent_disruptions
        })
        
        return jsonify(stats), 200
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@routes_blueprint.route('/saved-routes', methods=['GET'])
def get_saved_routes():
    """Get all saved routes from database"""
    try:
        routes = RouteModel.query.order_by(RouteModel.created_at.desc()).limit(50).all()
        
        result = []
        for route in routes:
            result.append({
                "id": route.id,
                "source": route.source_airport_code,
                "destination": route.destination_airport_code,
                "route_type": route.route_type,
                "total_cost": route.total_cost,
                "total_duration": route.total_duration,
                "delay_probability": route.total_delay_prob,
                "airports": json.loads(route.airports_sequence),
                "flights": json.loads(route.flights_sequence),
                "created_at": route.created_at.isoformat()
            })
        
        return jsonify({
            "routes": result,
            "total_count": len(result)
        }), 200
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@routes_blueprint.route('/compare-algorithms', methods=['POST'])
def compare_algorithms():
    """Compare Dijkstra vs A* algorithms for the same route"""
    try:
        data = request.get_json()
        source = data.get('source')
        destination = data.get('destination')
        optimization = data.get('optimization', 'cost')
        
        if not source or not destination:
            return jsonify({"error": "Source and destination are required"}), 400
        
        flight_network.build_network()
        
        # Run Dijkstra
        dijkstra_route = flight_network.dijkstra_shortest_path(source, destination, optimization)
        
        # Run A*
        astar_route = flight_network.a_star_shortest_path(source, destination, optimization)
        
        result = {
            "source": source,
            "destination": destination,
            "optimization": optimization,
            "dijkstra": None,
            "a_star": None,
            "comparison": None
        }
        
        if dijkstra_route:
            result["dijkstra"] = {
                "airports": dijkstra_route.airports,
                "flights": dijkstra_route.flights,
                "total_cost": round(dijkstra_route.total_cost, 2),
                "total_duration": round(dijkstra_route.total_duration, 2),
                "delay_probability": round(dijkstra_route.total_delay_prob, 3)
            }
        
        if astar_route:
            result["a_star"] = {
                "airports": astar_route.airports,
                "flights": astar_route.flights,
                "total_cost": round(astar_route.total_cost, 2),
                "total_duration": round(astar_route.total_duration, 2),
                "delay_probability": round(astar_route.total_delay_prob, 3)
            }
        
        if dijkstra_route and astar_route:
            result["comparison"] = {
                "same_route": dijkstra_route.flights == astar_route.flights,
                "cost_difference": round(abs(dijkstra_route.total_cost - astar_route.total_cost), 2),
                "time_difference": round(abs(dijkstra_route.total_duration - astar_route.total_duration), 2)
            }
        
        return jsonify(result), 200
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@routes_blueprint.route('/visualize-route', methods=['POST'])
def visualize_route():
    """Generate Folium map visualization for a specific route"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "No JSON data provided"}), 400
            
        airports_sequence = data.get('airports', [])
        flights_sequence = data.get('flights', [])
        route_type = data.get('route_type', 'optimal')
        
        print(f"[DEBUG] Visualize route request: {data}")
        
        if not airports_sequence:
            return jsonify({"error": "Airports sequence is required"}), 400
        
        print(f"[DEBUG] Creating map for airports: {airports_sequence}")
        
        # Create the map
        map_viz = create_route_map(airports_sequence, flights_sequence, route_type)
        
        if not map_viz:
            return jsonify({"error": "Failed to create map"}), 500
        
        # Get the HTML content and extract just the map div content
        map_html = map_viz._repr_html_()
        
        if not map_html:
            return jsonify({"error": "Failed to generate map HTML"}), 500
        
        # Extract just the inner content without the outer iframe wrapper
        import re
        
        # Find the srcdoc content from the iframe
        srcdoc_match = re.search(r'srcdoc="([^"]*)"', map_html)
        if srcdoc_match:
            # Decode HTML entities
            import html
            inner_html = html.unescape(srcdoc_match.group(1))
            print(f"[DEBUG] Extracted inner HTML size: {len(inner_html)} bytes")
            map_html = inner_html
        
        print(f"[DEBUG] Final HTML size: {len(map_html)} bytes")
        
        # Return HTML response
        response = make_response(map_html)
        response.headers['Content-Type'] = 'text/html'
        response.headers['Access-Control-Allow-Origin'] = '*'
        return response
        
    except Exception as e:
        print(f"[ERROR] Map visualization error: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({"error": f"Map generation failed: {str(e)}"}), 500

@routes_blueprint.route('/visualize-network', methods=['GET'])
def visualize_network():
    """Generate Folium map visualization for the entire flight network"""
    try:
        # Create the network overview map
        map_viz = create_network_overview_map()
        
        # Get the HTML content and extract just the map div content
        map_html = map_viz._repr_html_()
        
        # Extract just the inner content without the outer iframe wrapper
        import re
        import html
        
        # Find the srcdoc content from the iframe
        srcdoc_match = re.search(r'srcdoc="([^"]*)"', map_html)
        if srcdoc_match:
            # Decode HTML entities
            inner_html = html.unescape(srcdoc_match.group(1))
            map_html = inner_html
        
        # Return HTML response
        response = make_response(map_html)
        response.headers['Content-Type'] = 'text/html'
        response.headers['Access-Control-Allow-Origin'] = '*'
        return response
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@routes_blueprint.route('/visualize-comparison', methods=['POST'])
def visualize_comparison():
    """Generate Folium map visualization comparing multiple routes"""
    try:
        data = request.get_json()
        routes_data = data.get('routes', [])
        
        if not routes_data:
            return jsonify({"error": "Routes data is required"}), 400
        
        # Create the comparison map
        map_viz = create_multiple_routes_comparison(routes_data)
        
        # Get the HTML content and extract just the map div content
        map_html = map_viz._repr_html_()
        
        # Extract just the inner content without the outer iframe wrapper
        import re
        import html
        
        # Find the srcdoc content from the iframe
        srcdoc_match = re.search(r'srcdoc="([^"]*)"', map_html)
        if srcdoc_match:
            # Decode HTML entities
            inner_html = html.unescape(srcdoc_match.group(1))
            map_html = inner_html
        
        # Return HTML response
        response = make_response(map_html)
        response.headers['Content-Type'] = 'text/html'
        response.headers['Access-Control-Allow-Origin'] = '*'
        return response
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500