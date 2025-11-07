import heapq
import math
import random
from typing import Dict, List, Tuple, Optional, Set
from dataclasses import dataclass
from datetime import datetime, timedelta
from models import Flight, Airport, db


@dataclass
class Route:
    """Represents a complete route from source to destination"""
    airports: List[str]
    flights: List[str]
    total_cost: float
    total_duration: float
    total_delay_prob: float
    route_type: str  # 'cost', 'time', 'reliability'


@dataclass
class FlightEdge:
    """Represents an edge in the flight network graph"""
    flight_number: str
    destination: str
    cost: float
    duration: float
    delay_prob: float
    distance: float  # for A* heuristic


class FlightNetwork:
    """Graph-based flight network for route optimization"""
    
    def __init__(self):
        self.graph: Dict[str, List[FlightEdge]] = {}
        self.airports: Dict[str, Dict] = {}
        self.delayed_flights: Set[str] = set()
        self.cancelled_flights: Set[str] = set()
        
    def build_network(self):
        """Build the flight network graph from database"""
        self.graph.clear()
        self.airports.clear()
        
        # Load airports
        airports = Airport.query.all()
        for airport in airports:
            self.airports[airport.code] = {
                'name': airport.name,
                'city': airport.city,
                'lat': self._get_mock_coordinates(airport.code)[0],
                'lon': self._get_mock_coordinates(airport.code)[1]
            }
            self.graph[airport.code] = []
        
        # Load flights as edges
        flights = Flight.query.all()
        for flight in flights:
            if flight.flight_number not in self.cancelled_flights:
                source_code = flight.source.code
                dest_code = flight.destination.code
                
                # Calculate distance for A* heuristic
                distance = self._calculate_distance(source_code, dest_code)
                
                # Adjust delay probability if flight is known to be delayed
                delay_prob = flight.delay_prob
                if flight.flight_number in self.delayed_flights:
                    delay_prob = min(1.0, delay_prob * 2)  # Double delay probability
                
                edge = FlightEdge(
                    flight_number=flight.flight_number,
                    destination=dest_code,
                    cost=flight.price,
                    duration=flight.duration,
                    delay_prob=delay_prob,
                    distance=distance
                )
                
                self.graph[source_code].append(edge)
    
    def _get_mock_coordinates(self, airport_code: str) -> Tuple[float, float]:
        """Mock coordinates for airports (in a real system, these would be in the database)"""
        coords = {
            'DEL': (28.5562, 77.1000),  # Delhi
            'BOM': (19.0896, 72.8656),  # Mumbai
            'BLR': (12.9716, 77.5946),  # Bangalore
            'MAA': (12.9941, 80.1709),  # Chennai
            'CCU': (22.6549, 88.4462),  # Kolkata
            'HYD': (17.2403, 78.4294),  # Hyderabad
        }
        return coords.get(airport_code, (0.0, 0.0))
    
    def _calculate_distance(self, source: str, destination: str) -> float:
        """Calculate great circle distance between two airports"""
        lat1, lon1 = self._get_mock_coordinates(source)
        lat2, lon2 = self._get_mock_coordinates(destination)
        
        # Haversine formula
        R = 6371  # Earth's radius in km
        dlat = math.radians(lat2 - lat1)
        dlon = math.radians(lon2 - lon1)
        a = (math.sin(dlat/2) * math.sin(dlat/2) + 
             math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * 
             math.sin(dlon/2) * math.sin(dlon/2))
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
        return R * c
    
    def dijkstra_shortest_path(self, source: str, destination: str, 
                              optimization: str = 'cost') -> Optional[Route]:
        """
        Find shortest path using Dijkstra's algorithm
        optimization: 'cost', 'time', or 'reliability'
        """
        if source not in self.graph or destination not in self.graph:
            return None
        
        # Priority queue: (cost, current_airport, path, flights, total_duration, total_delay_prob)
        pq = [(0, source, [source], [], 0, 0)]
        visited = set()
        
        while pq:
            current_cost, current_airport, path, flights, total_duration, total_delay_prob = heapq.heappop(pq)
            
            if current_airport in visited:
                continue
            
            visited.add(current_airport)
            
            if current_airport == destination:
                return Route(
                    airports=path,
                    flights=flights,
                    total_cost=current_cost,
                    total_duration=total_duration,
                    total_delay_prob=total_delay_prob / len(flights) if flights else 0,
                    route_type=optimization
                )
            
            for edge in self.graph[current_airport]:
                if edge.destination not in visited:
                    # Calculate cost based on optimization criteria
                    if optimization == 'cost':
                        edge_cost = edge.cost
                    elif optimization == 'time':
                        edge_cost = edge.duration * 100  # Weight time heavily
                    elif optimization == 'reliability':
                        edge_cost = edge.delay_prob * 1000  # Weight reliability heavily
                    else:
                        # Balanced approach
                        edge_cost = edge.cost + edge.duration * 50 + edge.delay_prob * 500
                    
                    new_cost = current_cost + edge_cost
                    new_path = path + [edge.destination]
                    new_flights = flights + [edge.flight_number]
                    new_duration = total_duration + edge.duration
                    new_delay_prob = total_delay_prob + edge.delay_prob
                    
                    heapq.heappush(pq, (new_cost, edge.destination, new_path, 
                                      new_flights, new_duration, new_delay_prob))
        
        return None
    
    def a_star_shortest_path(self, source: str, destination: str, 
                           optimization: str = 'cost') -> Optional[Route]:
        """
        Find shortest path using A* algorithm with heuristic
        """
        if source not in self.graph or destination not in self.graph:
            return None
        
        def heuristic(airport: str) -> float:
            """Heuristic function for A*"""
            if optimization == 'cost':
                # Estimate minimum cost based on distance
                distance = self._calculate_distance(airport, destination)
                return distance * 0.5  # Rough cost per km
            elif optimization == 'time':
                # Estimate minimum time based on distance
                distance = self._calculate_distance(airport, destination)
                return distance / 500  # Rough speed of 500 km/h
            else:
                return 0  # For reliability, no good heuristic
        
        # Priority queue: (f_score, current_airport, path, flights, g_score, total_duration, total_delay_prob)
        pq = [(heuristic(source), source, [source], [], 0, 0, 0)]
        visited = set()
        g_scores = {source: 0}
        
        while pq:
            f_score, current_airport, path, flights, g_score, total_duration, total_delay_prob = heapq.heappop(pq)
            
            if current_airport in visited:
                continue
            
            visited.add(current_airport)
            
            if current_airport == destination:
                return Route(
                    airports=path,
                    flights=flights,
                    total_cost=g_score,
                    total_duration=total_duration,
                    total_delay_prob=total_delay_prob / len(flights) if flights else 0,
                    route_type=f"a_star_{optimization}"
                )
            
            for edge in self.graph[current_airport]:
                if edge.destination not in visited:
                    # Calculate cost based on optimization criteria
                    if optimization == 'cost':
                        edge_cost = edge.cost
                    elif optimization == 'time':
                        edge_cost = edge.duration * 100
                    elif optimization == 'reliability':
                        edge_cost = edge.delay_prob * 1000
                    else:
                        edge_cost = edge.cost + edge.duration * 50 + edge.delay_prob * 500
                    
                    tentative_g_score = g_score + edge_cost
                    
                    if edge.destination not in g_scores or tentative_g_score < g_scores[edge.destination]:
                        g_scores[edge.destination] = tentative_g_score
                        f_score = tentative_g_score + heuristic(edge.destination)
                        
                        new_path = path + [edge.destination]
                        new_flights = flights + [edge.flight_number]
                        new_duration = total_duration + edge.duration
                        new_delay_prob = total_delay_prob + edge.delay_prob
                        
                        heapq.heappush(pq, (f_score, edge.destination, new_path, 
                                          new_flights, tentative_g_score, new_duration, new_delay_prob))
        
        return None
    
    def find_multiple_routes(self, source: str, destination: str, 
                           num_routes: int = 3) -> List[Route]:
        """Find multiple optimal routes with different optimization criteria"""
        routes = []
        
        # Find route optimized for cost
        cost_route = self.dijkstra_shortest_path(source, destination, 'cost')
        if cost_route:
            routes.append(cost_route)
        
        # Find route optimized for time
        time_route = self.a_star_shortest_path(source, destination, 'time')
        if time_route and time_route.flights != (cost_route.flights if cost_route else []):
            routes.append(time_route)
        
        # Find route optimized for reliability
        reliability_route = self.dijkstra_shortest_path(source, destination, 'reliability')
        if (reliability_route and 
            reliability_route.flights not in [r.flights for r in routes]):
            routes.append(reliability_route)
        
        return routes[:num_routes]
    
    def handle_flight_delay(self, flight_number: str, delay_minutes: int):
        """Handle flight delay by updating the network"""
        self.delayed_flights.add(flight_number)
        print(f"Flight {flight_number} delayed by {delay_minutes} minutes")
        # Rebuild network to update delay probabilities
        self.build_network()
    
    def handle_flight_cancellation(self, flight_number: str):
        """Handle flight cancellation by removing from network"""
        self.cancelled_flights.add(flight_number)
        print(f"Flight {flight_number} cancelled")
        # Rebuild network to remove cancelled flight
        self.build_network()
    
    def find_alternative_routes(self, original_route: Route, 
                              disrupted_flight: str) -> List[Route]:
        """Find alternative routes when a flight is disrupted"""
        if disrupted_flight not in original_route.flights:
            return [original_route]
        
        # Find the point where the disruption occurs
        disruption_index = original_route.flights.index(disrupted_flight)
        
        if disruption_index == 0:
            # First flight disrupted, find new route from original source
            source = original_route.airports[0]
            destination = original_route.airports[-1]
        else:
            # Find alternative from the last successfully reached airport
            source = original_route.airports[disruption_index]
            destination = original_route.airports[-1]
        
        # Handle the disruption
        if disrupted_flight in self.cancelled_flights:
            self.handle_flight_cancellation(disrupted_flight)
        else:
            self.handle_flight_delay(disrupted_flight, 60)  # Assume 60 min delay
        
        # Find alternative routes
        return self.find_multiple_routes(source, destination)
    
    def predict_delays(self) -> Dict[str, float]:
        """Predict delays for all flights based on various factors"""
        predictions = {}
        
        # Simple delay prediction based on historical data and current conditions
        for airport_code, edges in self.graph.items():
            for edge in edges:
                base_delay_prob = edge.delay_prob
                
                # Factor in time of day (mock implementation)
                time_factor = random.uniform(0.8, 1.2)
                
                # Factor in weather (mock implementation)
                weather_factor = random.uniform(0.9, 1.3)
                
                # Factor in airport congestion (mock implementation)
                congestion_factor = random.uniform(0.8, 1.4)
                
                predicted_delay_prob = min(1.0, base_delay_prob * time_factor * weather_factor * congestion_factor)
                predictions[edge.flight_number] = predicted_delay_prob
        
        return predictions
    
    def find_route(self, source: str, destination: str, algorithm: str = "dijkstra", optimization: str = "cost"):
        """
        Find a route using specified algorithm.
        
        Args:
            source: Source airport code
            destination: Destination airport code  
            algorithm: 'dijkstra' or 'astar'
            optimization: 'cost', 'time', or 'reliability'
        
        Returns:
            Dict with route information or None if no route found
        """
        if algorithm.lower() == "dijkstra":
            route = self.dijkstra_shortest_path(source, destination, optimization)
        elif algorithm.lower() == "astar":
            route = self.a_star_shortest_path(source, destination, optimization)
        else:
            raise ValueError(f"Unknown algorithm: {algorithm}")
        
        if not route:
            return None
        
        # Convert Route object to dict format expected by test script
        flights_data = []
        
        for i, flight_num in enumerate(route.flights):
            # Find flight details
            for airport_code, edges in self.graph.items():
                for edge in edges:
                    if edge.flight_number == flight_num:
                        # Get flight details from database
                        flight = Flight.query.filter_by(flight_number=flight_num).first()
                        if flight:
                            source_airport = Airport.query.get(flight.source_id)
                            dest_airport = Airport.query.get(flight.destination_id)
                            
                            flights_data.append({
                                'flight_number': flight_num,
                                'source': source_airport.code,
                                'destination': dest_airport.code,
                                'price': flight.price,
                                'duration': flight.duration,
                                'delay_prob': flight.delay_prob
                            })
                        break
                else:
                    continue
                break
        
        return {
            'flights': flights_data,
            'total_cost': route.total_cost,
            'total_duration': route.total_duration,
            'total_delay_prob': route.total_delay_prob
        }
    
    def get_network_statistics(self) -> Dict:
        """Get network statistics"""
        total_flights = sum(len(edges) for edges in self.graph.values())
        total_airports = len(self.airports)
        
        avg_delay_prob = 0
        if total_flights > 0:
            total_delay_prob = sum(
                edge.delay_prob 
                for edges in self.graph.values() 
                for edge in edges
            )
            avg_delay_prob = total_delay_prob / total_flights
        
        return {
            'total_airports': total_airports,
            'total_flights': total_flights,
            'delayed_flights': len(self.delayed_flights),
            'cancelled_flights': len(self.cancelled_flights),
            'avg_delay_probability': round(avg_delay_prob, 3),
            'network_connectivity': total_flights / total_airports if total_airports > 0 else 0
        }


# Global flight network instance
flight_network = FlightNetwork()