import { useState, useEffect } from "react";
import { motion } from "framer-motion";
import { useNavigate } from "react-router-dom";
import { Search, MapPin, Calendar, Plane, RefreshCw } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Badge } from "@/components/ui/badge";
import { toast } from "sonner";
import { flightAPI, Airport, NetworkStats } from "@/lib/api";

const FindRoutes = () => {
  const navigate = useNavigate();
  const [airports, setAirports] = useState<Airport[]>([]);
  const [networkStats, setNetworkStats] = useState<NetworkStats | null>(null);
  const [loading, setLoading] = useState(false);
  const [buildingNetwork, setBuildingNetwork] = useState(false);
  const [formData, setFormData] = useState({
    source: "",
    destination: "",
    algorithm: "multiple",
    optimization: "cost",
    date: "",
  });

  // Load airports and network stats on component mount
  useEffect(() => {
    const loadData = async () => {
      try {
        const [airportsData, statsData] = await Promise.all([
          flightAPI.getAirports(),
          flightAPI.getNetworkStats()
        ]);
        setAirports(airportsData);
        setNetworkStats(statsData);
      } catch (error) {
        console.error('Error loading data:', error);
        toast.error('Failed to load airport data');
      }
    };

    loadData();
  }, []);

  const handleBuildNetwork = async () => {
    setBuildingNetwork(true);
    try {
      const result = await flightAPI.buildNetwork();
      setNetworkStats(result.statistics);
      toast.success('Flight network built successfully');
    } catch (error) {
      console.error('Error building network:', error);
      toast.error('Failed to build network');
    } finally {
      setBuildingNetwork(false);
    }
  };

  const handleSearch = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!formData.source || !formData.destination) {
      toast.error("Please select both source and destination airports");
      return;
    }

    if (formData.source === formData.destination) {
      toast.error("Source and destination cannot be the same");
      return;
    }

    setLoading(true);
    try {
      // Navigate to results page with search params
      const params = new URLSearchParams({
        source: formData.source,
        destination: formData.destination,
        algorithm: formData.algorithm,
        optimization: formData.optimization,
      });
      
      navigate(`/results?${params.toString()}`);
    } catch (error) {
      console.error('Error during search:', error);
      toast.error('Search failed. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const getAirportOptions = () => {
    return airports.map(airport => ({
      value: airport.code,
      label: `${airport.code} - ${airport.name} (${airport.city})`
    }));
  };

  const indianRoutes = [
    { from: "DEL", to: "BOM", label: "Delhi → Mumbai" },
    { from: "DEL", to: "BLR", label: "Delhi → Bangalore" },
    { from: "BOM", to: "MAA", label: "Mumbai → Chennai" },
    { from: "BLR", to: "HYD", label: "Bangalore → Hyderabad" },
    { from: "DEL", to: "MAA", label: "Delhi → Chennai" },
    { from: "CCU", to: "HYD", label: "Kolkata → Hyderabad" },
  ];

  return (
    <div className="min-h-screen py-12 bg-gradient-to-b from-background via-secondary/20 to-background">
      <div className="container mx-auto px-4 sm:px-6 lg:px-8">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5 }}
          className="max-w-4xl mx-auto"
        >
          {/* Header */}
          <div className="text-center mb-12">
            <h1 className="text-4xl font-bold mb-4">
              Find Your{" "}
              <span className="bg-gradient-to-r from-primary to-accent bg-clip-text text-transparent">
                Optimal Route
              </span>
            </h1>
            <p className="text-muted-foreground text-lg">
              Powered by Graph Theory • Dijkstra's & A* Algorithms • Real-time Optimization
            </p>
          </div>

          {/* Network Status */}
          {networkStats && (
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.1 }}
              className="mb-8"
            >
              <Card className="bg-gradient-to-r from-primary/5 to-accent/5 border-primary/20">
                <CardHeader>
                  <CardTitle className="flex items-center justify-between">
                    <span className="flex items-center gap-2">
                      <Plane className="h-5 w-5 text-primary" />
                      Network Status
                    </span>
                    <Button
                      variant="outline"
                      size="sm"
                      onClick={handleBuildNetwork}
                      disabled={buildingNetwork}
                    >
                      {buildingNetwork ? (
                        <>
                          <RefreshCw className="mr-2 h-4 w-4 animate-spin" />
                          Building...
                        </>
                      ) : (
                        <>
                          <RefreshCw className="mr-2 h-4 w-4" />
                          Rebuild Network
                        </>
                      )}
                    </Button>
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm">
                    <div>
                      <div className="text-muted-foreground">Airports</div>
                      <div className="text-2xl font-bold text-primary">{networkStats.total_airports}</div>
                    </div>
                    <div>
                      <div className="text-muted-foreground">Flights</div>
                      <div className="text-2xl font-bold text-accent">{networkStats.total_flights}</div>
                    </div>
                    <div>
                      <div className="text-muted-foreground">Connectivity</div>
                      <div className="text-xl font-bold">{networkStats.network_connectivity.toFixed(1)}</div>
                    </div>
                    <div>
                      <div className="text-muted-foreground">Reliability</div>
                      <div className="text-xl font-bold text-green-600">
                        {((1 - networkStats.avg_delay_probability) * 100).toFixed(0)}%
                      </div>
                    </div>
                  </div>
                  {(networkStats.delayed_flights > 0 || networkStats.cancelled_flights > 0) && (
                    <div className="mt-4 flex gap-2">
                      {networkStats.delayed_flights > 0 && (
                        <Badge variant="destructive">{networkStats.delayed_flights} Delayed</Badge>
                      )}
                      {networkStats.cancelled_flights > 0 && (
                        <Badge variant="destructive">{networkStats.cancelled_flights} Cancelled</Badge>
                      )}
                    </div>
                  )}
                </CardContent>
              </Card>
            </motion.div>
          )}

          {/* Search Card */}
          <Card className="shadow-xl border-border/50">
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Search className="h-5 w-5 text-primary" />
                Route Optimization Search
              </CardTitle>
              <CardDescription>
                Choose airports, algorithm, and optimization criteria for the best routes
              </CardDescription>
            </CardHeader>
            <CardContent>
              <form onSubmit={handleSearch} className="space-y-6">
                {/* Source & Destination */}
                <div className="grid md:grid-cols-2 gap-4">
                  <div className="space-y-2">
                    <Label htmlFor="source" className="flex items-center gap-2">
                      <MapPin className="h-4 w-4 text-primary" />
                      From Airport
                    </Label>
                    <Select
                      value={formData.source}
                      onValueChange={(value) => setFormData({ ...formData, source: value })}
                    >
                      <SelectTrigger id="source">
                        <SelectValue placeholder="Select departure airport" />
                      </SelectTrigger>
                      <SelectContent className="bg-popover max-h-60">
                        {getAirportOptions().map((airport) => (
                          <SelectItem key={airport.value} value={airport.value}>
                            {airport.label}
                          </SelectItem>
                        ))}
                      </SelectContent>
                    </Select>
                  </div>

                  <div className="space-y-2">
                    <Label htmlFor="destination" className="flex items-center gap-2">
                      <MapPin className="h-4 w-4 text-accent" />
                      To Airport
                    </Label>
                    <Select
                      value={formData.destination}
                      onValueChange={(value) => setFormData({ ...formData, destination: value })}
                    >
                      <SelectTrigger id="destination">
                        <SelectValue placeholder="Select destination airport" />
                      </SelectTrigger>
                      <SelectContent className="bg-popover max-h-60">
                        {getAirportOptions().map((airport) => (
                          <SelectItem key={airport.value} value={airport.value}>
                            {airport.label}
                          </SelectItem>
                        ))}
                      </SelectContent>
                    </Select>
                  </div>
                </div>

                {/* Algorithm & Optimization */}
                <div className="grid md:grid-cols-3 gap-4">
                  <div className="space-y-2">
                    <Label htmlFor="algorithm">Algorithm</Label>
                    <Select
                      value={formData.algorithm}
                      onValueChange={(value) => setFormData({ ...formData, algorithm: value })}
                    >
                      <SelectTrigger id="algorithm">
                        <SelectValue />
                      </SelectTrigger>
                      <SelectContent className="bg-popover">
                        <SelectItem value="multiple">🎯 Multiple Routes</SelectItem>
                        <SelectItem value="dijkstra">📊 Dijkstra's Algorithm</SelectItem>
                        <SelectItem value="a_star">⭐ A* Algorithm</SelectItem>
                      </SelectContent>
                    </Select>
                  </div>

                  <div className="space-y-2">
                    <Label htmlFor="optimization">Optimization</Label>
                    <Select
                      value={formData.optimization}
                      onValueChange={(value) => setFormData({ ...formData, optimization: value })}
                    >
                      <SelectTrigger id="optimization">
                        <SelectValue />
                      </SelectTrigger>
                      <SelectContent className="bg-popover">
                        <SelectItem value="cost">💰 Lowest Cost</SelectItem>
                        <SelectItem value="time">⚡ Fastest Route</SelectItem>
                        <SelectItem value="reliability">🛡️ Most Reliable</SelectItem>
                      </SelectContent>
                    </Select>
                  </div>

                  <div className="space-y-2">
                    <Label htmlFor="date" className="flex items-center gap-2">
                      <Calendar className="h-4 w-4 text-primary" />
                      Departure Date
                    </Label>
                    <Input
                      id="date"
                      type="date"
                      value={formData.date}
                      onChange={(e) => setFormData({ ...formData, date: e.target.value })}
                      min={new Date().toISOString().split('T')[0]}
                    />
                  </div>
                </div>

                {/* Submit Button */}
                <Button
                  type="submit"
                  variant="hero"
                  size="lg"
                  className="w-full"
                  disabled={loading}
                >
                  {loading ? (
                    <>
                      <RefreshCw className="mr-2 h-5 w-5 animate-spin" />
                      Finding Routes...
                    </>
                  ) : (
                    <>
                      <Search className="mr-2 h-5 w-5" />
                      Find Optimal Routes
                    </>
                  )}
                </Button>
              </form>
            </CardContent>
          </Card>

          {/* Popular Routes */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5, delay: 0.2 }}
            className="mt-12"
          >
            <h3 className="text-xl font-semibold mb-6 text-center">Popular Indian Routes</h3>
            <div className="grid sm:grid-cols-2 lg:grid-cols-3 gap-3">
              {indianRoutes.map((route, index) => (
                <button
                  key={index}
                  onClick={() => {
                    setFormData({ ...formData, source: route.from, destination: route.to });
                  }}
                  className="p-4 bg-card border border-border rounded-lg hover:border-primary/50 hover:shadow-md transition-all duration-300 text-left group"
                >
                  <div className="flex items-center justify-between">
                    <div className="flex-1">
                      <div className="text-sm font-medium text-foreground group-hover:text-primary transition-colors">
                        {route.label}
                      </div>
                      <div className="text-xs text-muted-foreground mt-1">
                        {route.from} → {route.to}
                      </div>
                    </div>
                    <div className="text-primary opacity-0 group-hover:opacity-100 transition-opacity">
                      →
                    </div>
                  </div>
                </button>
              ))}
            </div>
          </motion.div>
        </motion.div>
      </div>
    </div>
  );
};

export default FindRoutes;
