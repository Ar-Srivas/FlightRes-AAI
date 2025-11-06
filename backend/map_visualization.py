import folium
import json
from flask import render_template_string
from models import Airport

import folium
import json
from flask import render_template_string
from models import Airport

def create_route_map(airports_sequence, flights_sequence=None, route_type="optimal"):
    """
    Create a Folium map visualization for flight routes
    """
    
    # Airport coordinates for Indian airports (lat, lon format)
    airport_coords = {
        'DEL': (28.5562, 77.1000),  # Delhi
        'BOM': (19.0896, 72.8656),  # Mumbai  
        'BLR': (12.9716, 77.5946),  # Bangalore
        'MAA': (12.9941, 80.1709),  # Chennai
        'CCU': (22.6549, 88.4462),  # Kolkata
        'HYD': (17.2403, 78.4294),  # Hyderabad
        'AMD': (23.0726, 72.6177),  # Ahmedabad
        'PNQ': (18.5821, 73.9197),  # Pune
        'GOI': (15.3808, 73.8314),  # Goa
        'JAI': (26.8167, 75.8042),  # Jaipur
    }
    
    # Validate that we have airport data
    if not airports_sequence or len(airports_sequence) < 2:
        # Create default map for India
        map_viz = folium.Map(
            location=[20.5937, 78.9629],
            zoom_start=5,
            tiles='OpenStreetMap'
        )
        folium.Marker(
            location=[20.5937, 78.9629],
            popup="No route data available",
            icon=folium.Icon(color='red', icon='exclamation-triangle', prefix='fa')
        ).add_to(map_viz)
        return map_viz
    
    # Get airport details from database
    airport_details = {}
    for code in airports_sequence:
        airport = Airport.query.filter_by(code=code).first()
        if airport and code in airport_coords:
            airport_details[code] = {
                'name': airport.name,
                'city': airport.city,
                'coords': airport_coords[code]
            }
    
    # Calculate center point for map
    valid_coords = [airport_coords[code] for code in airports_sequence if code in airport_coords]
    if valid_coords:
        center_lat = sum(coord[0] for coord in valid_coords) / len(valid_coords)
        center_lon = sum(coord[1] for coord in valid_coords) / len(valid_coords)
    else:
        center_lat, center_lon = 20.5937, 78.9629  # Center of India
    
    # Create the map
    map_viz = folium.Map(
        location=[center_lat, center_lon],
        zoom_start=6,
        tiles='OpenStreetMap'
    )
    
    # Color scheme based on route type
    colors = {
        'cost': '#10B981',      # Green
        'time': '#3B82F6',      # Blue  
        'reliability': '#8B5CF6', # Purple
        'a_star_cost': '#F59E0B',  # Orange
        'a_star_time': '#EF4444',  # Red
        'optimal': '#6366F1'    # Indigo
    }
    
    route_color = colors.get(route_type.lower(), '#6366F1')
    
    # Collect coordinates for path
    path_coordinates = []
    
    # Add markers for each airport and collect coordinates
    for i, airport_code in enumerate(airports_sequence):
        if airport_code in airport_details:
            coords = airport_details[airport_code]['coords']
            path_coordinates.append([coords[0], coords[1]])  # [lat, lon]
            
            # Determine marker style based on position in route
            if i == 0:
                # Origin
                icon_color = 'green'
                icon_name = 'play'
                popup_text = f"🛫 <strong>ORIGIN</strong><br><strong>{airport_code}</strong><br>{airport_details[airport_code]['name']}<br>{airport_details[airport_code]['city']}"
            elif i == len(airports_sequence) - 1:
                # Destination  
                icon_color = 'red'
                icon_name = 'stop'
                popup_text = f"🛬 <strong>DESTINATION</strong><br><strong>{airport_code}</strong><br>{airport_details[airport_code]['name']}<br>{airport_details[airport_code]['city']}"
            else:
                # Layover
                icon_color = 'orange'
                icon_name = 'pause'
                popup_text = f"🔄 <strong>LAYOVER {i}</strong><br><strong>{airport_code}</strong><br>{airport_details[airport_code]['name']}<br>{airport_details[airport_code]['city']}"
            
            # Add flight information if available
            if flights_sequence and i < len(flights_sequence):
                popup_text += f"<br><br>✈️ <strong>Flight: {flights_sequence[i]}</strong>"
            
            # Create marker
            folium.Marker(
                location=coords,
                popup=folium.Popup(popup_text, max_width=300),
                tooltip=f"{airport_code} - {airport_details[airport_code]['city']}",
                icon=folium.Icon(
                    color=icon_color,
                    icon=icon_name,
                    prefix='fa'
                )
            ).add_to(map_viz)
    
    # Draw the main flight path
    if len(path_coordinates) >= 2:
        # Create the main route line
        folium.PolyLine(
            locations=path_coordinates,
            color=route_color,
            weight=6,
            opacity=0.8,
            popup=f"✈️ Flight Route ({route_type.title()})<br>Path: {' → '.join(airports_sequence)}"
        ).add_to(map_viz)
        
        # Add directional arrows along the path
        for i in range(len(path_coordinates) - 1):
            start = path_coordinates[i]
            end = path_coordinates[i + 1]
            
            # Calculate multiple points along the segment for better arrow placement
            num_arrows = 3
            for j in range(1, num_arrows + 1):
                t = j / (num_arrows + 1)  # fraction along the segment
                arrow_lat = start[0] + t * (end[0] - start[0])
                arrow_lon = start[1] + t * (end[1] - start[1])
                
                # Calculate bearing for arrow direction
                import math
                lat1, lon1 = math.radians(start[0]), math.radians(start[1])
                lat2, lon2 = math.radians(end[0]), math.radians(end[1])
                
                dlon = lon2 - lon1
                y = math.sin(dlon) * math.cos(lat2)
                x = math.cos(lat1) * math.sin(lat2) - math.sin(lat1) * math.cos(lat2) * math.cos(dlon)
                bearing = math.degrees(math.atan2(y, x))
                
                # Add arrow marker
                folium.Marker(
                    location=[arrow_lat, arrow_lon],
                    icon=folium.Icon(
                        color='darkblue',
                        icon='arrow-right',
                        prefix='fa'
                    ),
                    popup=f"Flight Direction<br>Segment {i+1} of {len(path_coordinates)-1}"
                ).add_to(map_viz)
        
        # Add distance/time information for each segment
        for i in range(len(path_coordinates) - 1):
            start = path_coordinates[i]
            end = path_coordinates[i + 1]
            mid_lat = (start[0] + end[0]) / 2
            mid_lon = (start[1] + end[1]) / 2
            
            # Calculate approximate distance
            from math import radians, cos, sin, asin, sqrt
            
            def haversine(lon1, lat1, lon2, lat2):
                lon1, lat1, lon2, lat2 = map(radians, [lon1, lat1, lon2, lat2])
                dlon = lon2 - lon1
                dlat = lat2 - lat1
                a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
                c = 2 * asin(sqrt(a))
                r = 6371  # Radius of earth in kilometers
                return c * r
            
            distance = haversine(start[1], start[0], end[1], end[0])
            
            # Add invisible marker for segment info
            segment_info = f"Segment {i+1}<br>{airports_sequence[i]} → {airports_sequence[i+1]}<br>Distance: ~{distance:.0f} km"
            if flights_sequence and i < len(flights_sequence):
                segment_info += f"<br>Flight: {flights_sequence[i]}"
            
            folium.CircleMarker(
                location=[mid_lat, mid_lon],
                radius=8,
                popup=segment_info,
                color=route_color,
                fillColor=route_color,
                fillOpacity=0.7
            ).add_to(map_viz)
    
    # Add a comprehensive legend
    total_distance = 0
    if len(path_coordinates) >= 2:
        from math import radians, cos, sin, asin, sqrt
        def haversine(lon1, lat1, lon2, lat2):
            lon1, lat1, lon2, lat2 = map(radians, [lon1, lat1, lon2, lat2])
            dlon = lon2 - lon1
            dlat = lat2 - lat1
            a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
            c = 2 * asin(sqrt(a))
            r = 6371
            return c * r
        
        for i in range(len(path_coordinates) - 1):
            start = path_coordinates[i]
            end = path_coordinates[i + 1]
            total_distance += haversine(start[1], start[0], end[1], end[0])
    
    legend_html = f'''
    <div style="position: fixed; 
                top: 10px; right: 10px; width: 280px; height: auto; 
                background-color: white; border:3px solid grey; z-index:9999; 
                font-size:13px; padding: 15px; border-radius: 10px; box-shadow: 0 4px 8px rgba(0,0,0,0.1);">
    <h4 style="margin-top:0; color: #333;">🛫 Flight Route Visualization</h4>
    <div style="margin: 10px 0;">
        <p style="margin: 5px 0;"><i class="fa fa-play" style="color:green; margin-right: 8px;"></i><strong>Origin</strong></p>
        <p style="margin: 5px 0;"><i class="fa fa-pause" style="color:orange; margin-right: 8px;"></i><strong>Layover</strong></p>
        <p style="margin: 5px 0;"><i class="fa fa-stop" style="color:red; margin-right: 8px;"></i><strong>Destination</strong></p>
    </div>
    <hr style="margin: 10px 0;">
    <p style="margin: 5px 0;"><strong>Route:</strong> {' → '.join(airports_sequence)}</p>
    <p style="margin: 5px 0;"><strong>Type:</strong> {route_type.title()} Optimized</p>
    <p style="margin: 5px 0;"><strong>Segments:</strong> {len(airports_sequence) - 1}</p>
    <p style="margin: 5px 0;"><strong>Total Distance:</strong> ~{total_distance:.0f} km</p>
    {f'<p style="margin: 5px 0;"><strong>Flights:</strong> {", ".join(flights_sequence)}</p>' if flights_sequence else ''}
    </div>
    '''
    map_viz.get_root().html.add_child(folium.Element(legend_html))
    
    # Fit bounds to show all markers with padding
    if path_coordinates:
        sw = [min(coord[0] for coord in path_coordinates) - 0.5, min(coord[1] for coord in path_coordinates) - 0.5]
        ne = [max(coord[0] for coord in path_coordinates) + 0.5, max(coord[1] for coord in path_coordinates) + 0.5]
        map_viz.fit_bounds([sw, ne])
    
    return map_viz

def create_network_overview_map():
    """
    Create a map showing the entire flight network
    """
    
    # Airport coordinates
    airport_coords = {
        'DEL': (28.5562, 77.1000),  # Delhi
        'BOM': (19.0896, 72.8656),  # Mumbai
        'BLR': (12.9716, 77.5946),  # Bangalore
        'MAA': (12.9941, 80.1709),  # Chennai
        'CCU': (22.6549, 88.4462),  # Kolkata
        'HYD': (17.2403, 78.4294),  # Hyderabad
        'AMD': (23.0726, 72.6177),  # Ahmedabad
        'PNQ': (18.5821, 73.9197),  # Pune
        'GOI': (15.3808, 73.8314),  # Goa
        'JAI': (26.8167, 75.8042),  # Jaipur
    }
    
    # Create map centered on India
    map_viz = folium.Map(
        location=[20.5937, 78.9629],
        zoom_start=5,
        tiles='OpenStreetMap'
    )
    
    # Add all airports
    airports = Airport.query.all()
    for airport in airports:
        if airport.code in airport_coords:
            coords = airport_coords[airport.code]
            
            folium.Marker(
                location=coords,
                popup=f"<strong>{airport.code}</strong><br>{airport.name}<br>{airport.city}",
                tooltip=f"{airport.code} - {airport.city}",
                icon=folium.Icon(color='blue', icon='plane', prefix='fa')
            ).add_to(map_viz)
    
    # Add flight connections (simplified)
    from flight_network import flight_network
    flight_network.build_network()
    
    for source, edges in flight_network.graph.items():
        if source in airport_coords:
            source_coords = airport_coords[source]
            for edge in edges:
                if edge.destination in airport_coords:
                    dest_coords = airport_coords[edge.destination]
                    
                    # Color based on delay probability
                    if edge.delay_prob < 0.1:
                        color = 'green'
                    elif edge.delay_prob < 0.2:
                        color = 'orange'
                    else:
                        color = 'red'
                    
                    folium.PolyLine(
                        [source_coords, dest_coords],
                        color=color,
                        weight=2,
                        opacity=0.6,
                        popup=f"{edge.flight_number}: {source} → {edge.destination}<br>Delay Risk: {edge.delay_prob:.1%}"
                    ).add_to(map_viz)
    
    # Add legend
    legend_html = '''
    <div style="position: fixed; 
                top: 10px; right: 10px; width: 200px; height: auto; 
                background-color: white; border:2px solid grey; z-index:9999; 
                font-size:14px; padding: 10px">
    <h4>Flight Network Overview</h4>
    <p><i class="fa fa-plane" style="color:blue"></i> Airports</p>
    <p><span style="color:green">—</span> Low Delay Risk (&lt;10%)</p>
    <p><span style="color:orange">—</span> Medium Delay Risk (10-20%)</p>
    <p><span style="color:red">—</span> High Delay Risk (&gt;20%)</p>
    </div>
    '''
    map_viz.get_root().html.add_child(folium.Element(legend_html))
    
    return map_viz

def create_multiple_routes_comparison(routes_data):
    """
    Create a map comparing multiple routes
    """
    
    airport_coords = {
        'DEL': (28.5562, 77.1000),
        'BOM': (19.0896, 72.8656),
        'BLR': (12.9716, 77.5946),
        'MAA': (12.9941, 80.1709),
        'CCU': (22.6549, 88.4462),
        'HYD': (17.2403, 78.4294),
    }
    
    # Calculate center from all routes
    all_airports = set()
    for route in routes_data:
        all_airports.update(route['airports'])
    
    if all_airports:
        valid_airports = [code for code in all_airports if code in airport_coords]
        if valid_airports:
            center_lat = sum(airport_coords[code][0] for code in valid_airports) / len(valid_airports)
            center_lon = sum(airport_coords[code][1] for code in valid_airports) / len(valid_airports)
        else:
            center_lat, center_lon = 20.5937, 78.9629
    else:
        center_lat, center_lon = 20.5937, 78.9629
    
    map_viz = folium.Map(
        location=[center_lat, center_lon],
        zoom_start=6,
        tiles='OpenStreetMap'
    )
    
    # Colors for different routes
    route_colors = ['#10B981', '#3B82F6', '#8B5CF6', '#F59E0B', '#EF4444']
    
    # Add all airports first
    all_coords = []
    for airport_code in all_airports:
        if airport_code in airport_coords:
            coords = airport_coords[airport_code]
            all_coords.append([coords[0], coords[1]])  # [lat, lon] format
            
            airport = Airport.query.filter_by(code=airport_code).first()
            airport_name = airport.name if airport else airport_code
            airport_city = airport.city if airport else "Unknown"
            
            folium.Marker(
                location=coords,
                popup=f"<strong>{airport_code}</strong><br>{airport_name}<br>{airport_city}",
                tooltip=f"{airport_code} - {airport_city}",
                icon=folium.Icon(color='darkblue', icon='plane', prefix='fa')
            ).add_to(map_viz)
    
    # Add each route with different colors
    legend_items = []
    for i, route in enumerate(routes_data):
        color = route_colors[i % len(route_colors)]
        path_coordinates = []
        
        for airport_code in route['airports']:
            if airport_code in airport_coords:
                coords = airport_coords[airport_code]
                path_coordinates.append([coords[0], coords[1]])  # [lat, lon] format
        
        if len(path_coordinates) >= 2:
            # Draw the route path
            folium.PolyLine(
                locations=path_coordinates,
                color=color,
                weight=5,
                opacity=0.8,
                popup=f"Route {i+1}: {route['route_type']}<br>Cost: ₹{route['total_cost']:.0f}<br>Duration: {route['total_duration']:.1f}h<br>Path: {' → '.join(route['airports'])}"
            ).add_to(map_viz)
            
            # Add route number markers at the midpoint
            if len(path_coordinates) >= 2:
                mid_idx = len(path_coordinates) // 2
                mid_coord = path_coordinates[mid_idx]
                
                folium.Marker(
                    location=mid_coord,
                    popup=f"Route {i+1}<br>{route['route_type']}<br>₹{route['total_cost']:.0f}",
                    icon=folium.Icon(
                        color='white',
                        icon_color=color,
                        icon=str(i+1),
                        prefix='fa'
                    )
                ).add_to(map_viz)
            
            legend_items.append(f'<p style="margin: 3px 0;"><span style="color:{color}; font-weight:bold; font-size: 18px;">━━</span> Route {i+1}: {route["route_type"]} (₹{route["total_cost"]:.0f}, {route["total_duration"]:.1f}h)</p>')
    
    # Add comprehensive legend
    legend_html = f'''
    <div style="position: fixed; 
                top: 10px; right: 10px; width: 320px; height: auto; 
                background-color: white; border:3px solid grey; z-index:9999; 
                font-size:13px; padding: 15px; border-radius: 10px; box-shadow: 0 4px 8px rgba(0,0,0,0.1);">
    <h4 style="margin-top:0; color: #333;">🛫 Routes Comparison</h4>
    <div style="margin: 10px 0;">
        {''.join(legend_items)}
    </div>
    <hr style="margin: 10px 0;">
    <p style="margin: 5px 0;"><i class="fa fa-plane" style="color:darkblue; margin-right: 8px;"></i><strong>Airports</strong></p>
    <p style="margin: 5px 0; font-size: 11px; color: #666;">Click on routes for details</p>
    </div>
    '''
    map_viz.get_root().html.add_child(folium.Element(legend_html))
    
    # Fit bounds to show all coordinates
    if all_coords:
        # Add padding to bounds
        lats = [coord[0] for coord in all_coords]
        lons = [coord[1] for coord in all_coords]
        sw = [min(lats) - 0.5, min(lons) - 0.5]
        ne = [max(lats) + 0.5, max(lons) + 0.5]
        map_viz.fit_bounds([sw, ne])
    
    return map_viz