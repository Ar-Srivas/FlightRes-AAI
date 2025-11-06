// API service for flight network optimization system
const API_BASE_URL = 'http://localhost:5001';

export interface Airport {
  id: number;
  code: string;
  name: string;
  city: string;
  latitude: number;
  longitude: number;
  timezone: string;
}

export interface Flight {
  id: number;
  flight_number: string;
  source: {
    code: string;
    name: string;
    city: string;
  };
  destination: {
    code: string;
    name: string;
    city: string;
  };
  duration: number;
  price: number;
  delay_prob: number;
  status: string;
  departure_time: string;
  arrival_time: string;
  aircraft_type: string;
  max_capacity: number;
  current_bookings: number;
  latest_status?: {
    status: string;
    delay_minutes: number;
    reason: string;
    updated_at: string;
  };
}

export interface Route {
  route_type: string;
  airports: string[];
  flights: string[];
  total_cost: number;
  total_duration: number;
  average_delay_probability: number;
  stops: number;
}

export interface RouteResponse {
  source: string;
  destination: string;
  algorithm_used: string;
  optimization_criteria: string;
  routes_found: number;
  routes: Route[];
}

export interface DelayPrediction {
  flight_number: string;
  source: string;
  destination: string;
  predicted_delay_probability: number;
  risk_level: 'low' | 'medium' | 'high';
}

export interface NetworkStats {
  total_airports: number;
  total_flights: number;
  delayed_flights: number;
  cancelled_flights: number;
  avg_delay_probability: number;
  network_connectivity: number;
  saved_routes?: number;
  total_disruptions_recorded?: number;
  disruptions_today?: number;
}

export interface DisruptionResponse {
  message: string;
  flight_number: string;
  disruption_type: string;
  delay_minutes?: number;
  affected_passengers: number;
  alternative_routes_found: number;
  alternatives: Array<{
    booking_id: number;
    passenger: string;
    alternative_routes: Route[];
  }>;
}

class FlightNetworkAPI {
  private async request<T>(endpoint: string, options?: RequestInit): Promise<T> {
    const response = await fetch(`${API_BASE_URL}${endpoint}`, {
      headers: {
        'Content-Type': 'application/json',
        ...options?.headers,
      },
      ...options,
    });

    if (!response.ok) {
      const error = await response.json().catch(() => ({ error: 'Network error' }));
      throw new Error(error.error || `HTTP ${response.status}`);
    }

    return response.json();
  }

  // Airport and Flight Management
  async getAirports(): Promise<Airport[]> {
    return this.request<Airport[]>('/flights/airports');
  }

  async getFlights(): Promise<Flight[]> {
    return this.request<Flight[]>('/flights');
  }

  async searchFlights(params: {
    source?: string;
    destination?: string;
    max_price?: number;
    max_duration?: number;
    status?: string;
  }): Promise<{ flights: Flight[]; count: number; search_criteria: any }> {
    const searchParams = new URLSearchParams();
    Object.entries(params).forEach(([key, value]) => {
      if (value !== undefined) {
        searchParams.append(key, value.toString());
      }
    });
    
    return this.request(`/flights/search?${searchParams}`);
  }

  async getFlightDetails(flightNumber: string): Promise<Flight> {
    return this.request<Flight>(`/flights/${flightNumber}`);
  }

  // Network Management
  async buildNetwork(): Promise<{ message: string; statistics: NetworkStats }> {
    return this.request('/routes/build-network', { method: 'POST' });
  }

  async getNetworkStats(): Promise<NetworkStats> {
    return this.request<NetworkStats>('/routes/network-stats');
  }

  // Route Optimization
  async findRoutes(params: {
    source: string;
    destination: string;
    algorithm?: 'dijkstra' | 'a_star' | 'multiple';
    optimization?: 'cost' | 'time' | 'reliability';
    num_routes?: number;
  }): Promise<RouteResponse> {
    return this.request<RouteResponse>('/routes/find', {
      method: 'POST',
      body: JSON.stringify(params),
    });
  }

  async compareAlgorithms(params: {
    source: string;
    destination: string;
    optimization?: 'cost' | 'time' | 'reliability';
  }): Promise<{
    source: string;
    destination: string;
    optimization: string;
    dijkstra: Route | null;
    a_star: Route | null;
    comparison: {
      same_route: boolean;
      cost_difference: number;
      time_difference: number;
    } | null;
  }> {
    return this.request('/routes/compare-algorithms', {
      method: 'POST',
      body: JSON.stringify(params),
    });
  }

  // Delay Prediction
  async getDelayPredictions(): Promise<{
    predictions: DelayPrediction[];
    generated_at: string;
  }> {
    return this.request('/routes/delay-prediction');
  }

  // Disruption Handling
  async handleDisruption(params: {
    flight_number: string;
    type: 'delay' | 'cancellation';
    delay_minutes?: number;
    reason?: string;
  }): Promise<DisruptionResponse> {
    return this.request<DisruptionResponse>('/routes/handle-disruption', {
      method: 'POST',
      body: JSON.stringify(params),
    });
  }

  async updateFlightStatus(flightNumber: string, params: {
    status: 'delayed' | 'cancelled' | 'on_time';
    delay_minutes?: number;
    reason?: string;
  }): Promise<{
    message: string;
    flight_number: string;
    new_status: string;
    delay_minutes?: number;
  }> {
    return this.request(`/flights/${flightNumber}/status`, {
      method: 'POST',
      body: JSON.stringify(params),
    });
  }

  // Route History
  async getSavedRoutes(): Promise<{
    routes: Array<{
      id: number;
      source: string;
      destination: string;
      route_type: string;
      total_cost: number;
      total_duration: number;
      delay_probability: number;
      airports: string[];
      flights: string[];
      created_at: string;
    }>;
    total_count: number;
  }> {
    return this.request('/routes/saved-routes');
  }

  // Health Check
  async healthCheck(): Promise<{ status: string }> {
    return this.request('/health');
  }

  // Map Visualization
  async getRouteVisualization(params: {
    airports: string[];
    flights?: string[];
    route_type?: string;
  }): Promise<string> {
    console.log('Fetching route visualization for:', params);
    const response = await fetch(`${API_BASE_URL}/routes/visualize-route`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(params),
    });
    
    if (!response.ok) {
      const errorText = await response.text();
      console.error('Route visualization error:', errorText);
      throw new Error(`Failed to get route visualization: HTTP ${response.status}`);
    }
    
    const htmlContent = await response.text();
    console.log('Received HTML content length:', htmlContent.length);
    return htmlContent;
  }

  async getNetworkVisualization(): Promise<string> {
    console.log('Fetching network visualization');
    const response = await fetch(`${API_BASE_URL}/routes/visualize-network`);
    
    if (!response.ok) {
      const errorText = await response.text();
      console.error('Network visualization error:', errorText);
      throw new Error(`Failed to get network visualization: HTTP ${response.status}`);
    }
    
    const htmlContent = await response.text();
    console.log('Received network HTML content length:', htmlContent.length);
    return htmlContent;
  }

  async getRoutesComparison(routes: Route[]): Promise<string> {
    console.log('Fetching routes comparison for:', routes.length, 'routes');
    const response = await fetch(`${API_BASE_URL}/routes/visualize-comparison`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ routes }),
    });
    
    if (!response.ok) {
      const errorText = await response.text();
      console.error('Routes comparison error:', errorText);
      throw new Error(`Failed to get routes comparison: HTTP ${response.status}`);
    }
    
    const htmlContent = await response.text();
    console.log('Received comparison HTML content length:', htmlContent.length);
    return htmlContent;
  }
}

export const flightAPI = new FlightNetworkAPI();