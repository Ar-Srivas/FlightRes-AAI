import { useEffect, useState } from "react";
import { useSearchParams, useNavigate } from "react-router-dom";
import { motion } from "framer-motion";
import { ArrowLeft, Clock, DollarSign, TrendingUp, MapPin, Plane } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import MapVisualization from "@/components/MapVisualization";

interface RouteData {
  source: string;
  destination: string;
  optimal_route: string[];
  total_price: number;
  total_time: string;
  delay_probability: number;
}

const RouteResults = () => {
  const [searchParams] = useSearchParams();
  const navigate = useNavigate();
  const [routeData, setRouteData] = useState<RouteData | null>(null);
  const [loading, setLoading] = useState(true);

  const source = searchParams.get("source") || "";
  const destination = searchParams.get("destination") || "";
  const type = searchParams.get("type") || "cheapest";

  useEffect(() => {
    // Simulate API call with mock data
    const fetchRouteData = async () => {
      setLoading(true);
      
      // Simulate API delay
      await new Promise(resolve => setTimeout(resolve, 1500));

      // Mock data - replace with actual API call
      const mockData: RouteData = {
        source: `${source}`,
        destination: `${destination}`,
        optimal_route: [source, "CDG", destination],
        total_price: type === "cheapest" ? 520 : type === "fastest" ? 780 : 650,
        total_time: type === "fastest" ? "6h 30m" : type === "cheapest" ? "11h 45m" : "8h 20m",
        delay_probability: type === "reliable" ? 0.08 : type === "cheapest" ? 0.18 : 0.12,
      };

      setRouteData(mockData);
      setLoading(false);
    };

    fetchRouteData();
  }, [source, destination, type]);

  const handleBookFlight = () => {
    navigate(`/booking?route=${routeData?.optimal_route.join('-')}&price=${routeData?.total_price}`);
  };

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gradient-to-b from-background to-secondary/20">
        <div className="text-center">
          <motion.div
            animate={{ rotate: 360 }}
            transition={{ duration: 2, repeat: Infinity, ease: "linear" }}
            className="inline-block"
          >
            <Plane className="h-12 w-12 text-primary" />
          </motion.div>
          <p className="mt-4 text-muted-foreground">Finding optimal routes...</p>
        </div>
      </div>
    );
  }

  if (!routeData) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-center">
          <p className="text-muted-foreground">No route data available</p>
          <Button onClick={() => navigate("/find-routes")} className="mt-4">
            Search Again
          </Button>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen py-8 bg-gradient-to-b from-background to-secondary/20">
      <div className="container mx-auto px-4 sm:px-6 lg:px-8">
        {/* Back Button */}
        <Button
          variant="ghost"
          onClick={() => navigate("/find-routes")}
          className="mb-6"
        >
          <ArrowLeft className="mr-2 h-4 w-4" />
          Back to Search
        </Button>

        {/* Header */}
        <motion.div
          initial={{ opacity: 0, y: -20 }}
          animate={{ opacity: 1, y: 0 }}
          className="mb-8"
        >
          <h1 className="text-3xl font-bold mb-2">
            Route from{" "}
            <span className="text-primary">{source}</span>
            {" "}to{" "}
            <span className="text-accent">{destination}</span>
          </h1>
          <p className="text-muted-foreground">
            Optimized for:{" "}
            <Badge variant="secondary" className="ml-2">
              {type === "cheapest" ? "💰 Best Price" : type === "fastest" ? "⚡ Fastest" : "🛡️ Most Reliable"}
            </Badge>
          </p>
        </motion.div>

        <div className="grid lg:grid-cols-3 gap-6">
          {/* Stats Cards */}
          <motion.div
            initial={{ opacity: 0, x: -20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ delay: 0.1 }}
          >
            <Card className="shadow-lg border-primary/20">
              <CardHeader>
                <CardTitle className="flex items-center gap-2 text-lg">
                  <DollarSign className="h-5 w-5 text-primary" />
                  Total Price
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="text-3xl font-bold text-primary">
                  ${routeData.total_price}
                </div>
                <p className="text-sm text-muted-foreground mt-1">Per passenger</p>
              </CardContent>
            </Card>
          </motion.div>

          <motion.div
            initial={{ opacity: 0, x: -20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ delay: 0.2 }}
          >
            <Card className="shadow-lg border-accent/20">
              <CardHeader>
                <CardTitle className="flex items-center gap-2 text-lg">
                  <Clock className="h-5 w-5 text-accent" />
                  Travel Time
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="text-3xl font-bold text-accent">
                  {routeData.total_time}
                </div>
                <p className="text-sm text-muted-foreground mt-1">Total duration</p>
              </CardContent>
            </Card>
          </motion.div>

          <motion.div
            initial={{ opacity: 0, x: -20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ delay: 0.3 }}
          >
            <Card className="shadow-lg">
              <CardHeader>
                <CardTitle className="flex items-center gap-2 text-lg">
                  <TrendingUp className="h-5 w-5 text-primary" />
                  Reliability
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="text-3xl font-bold">
                  {((1 - routeData.delay_probability) * 100).toFixed(0)}%
                </div>
                <p className="text-sm text-muted-foreground mt-1">
                  {routeData.delay_probability < 0.1 ? "Excellent" : routeData.delay_probability < 0.15 ? "Good" : "Fair"} on-time rate
                </p>
              </CardContent>
            </Card>
          </motion.div>
        </div>

        {/* Route Details Card */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.4 }}
          className="mt-6"
        >
          <Card className="shadow-lg">
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <MapPin className="h-5 w-5 text-primary" />
                Flight Route
              </CardTitle>
              <CardDescription>
                {routeData.optimal_route.length - 2} layover(s)
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="flex items-center justify-between flex-wrap gap-4">
                {routeData.optimal_route.map((airport, index) => (
                  <div key={index} className="flex items-center">
                    <div className="text-center">
                      <div className="w-12 h-12 rounded-full bg-gradient-to-r from-primary to-accent flex items-center justify-center text-white font-bold mb-2">
                        {index + 1}
                      </div>
                      <div className="font-semibold">{airport}</div>
                      <div className="text-xs text-muted-foreground">
                        {index === 0 ? "Origin" : index === routeData.optimal_route.length - 1 ? "Destination" : "Layover"}
                      </div>
                    </div>
                    {index < routeData.optimal_route.length - 1 && (
                      <div className="mx-4 flex-1 min-w-[60px]">
                        <div className="h-0.5 bg-gradient-to-r from-primary to-accent" />
                        <Plane className="h-4 w-4 text-primary mx-auto -mt-2.5" />
                      </div>
                    )}
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        </motion.div>

        {/* Map Visualization */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.5 }}
          className="mt-6"
        >
          <Card className="shadow-lg overflow-hidden">
            <CardHeader>
              <CardTitle>Route Visualization</CardTitle>
              <CardDescription>Interactive map showing your flight path</CardDescription>
            </CardHeader>
            <CardContent className="p-0">
              <MapVisualization route={routeData.optimal_route} />
            </CardContent>
          </Card>
        </motion.div>

        {/* Book Button */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.6 }}
          className="mt-8 text-center"
        >
          <Button
            onClick={handleBookFlight}
            variant="hero"
            size="lg"
            className="min-w-[250px]"
          >
            Book This Flight
          </Button>
        </motion.div>
      </div>
    </div>
  );
};

export default RouteResults;
