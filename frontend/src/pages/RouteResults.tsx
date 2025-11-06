import { useEffect, useState } from "react";
import { useSearchParams, useNavigate } from "react-router-dom";
import { motion } from "framer-motion";
import { ArrowLeft, Clock, DollarSign, TrendingUp, MapPin, Plane, RefreshCw, BarChart3, Zap } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { toast } from "sonner";
import MapVisualization from "@/components/MapVisualization";
import { flightAPI, RouteResponse, Route } from "@/lib/api";

const RouteResults = () => {
  const [searchParams] = useSearchParams();
  const navigate = useNavigate();
  const [routeData, setRouteData] = useState<RouteResponse | null>(null);
  const [algorithmComparison, setAlgorithmComparison] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [comparing, setComparing] = useState(false);

  const source = searchParams.get("source") || "";
  const destination = searchParams.get("destination") || "";
  const algorithm = searchParams.get("algorithm") || "multiple";
  const optimization = searchParams.get("optimization") || "cost";

  useEffect(() => {
    const fetchRouteData = async () => {
      setLoading(true);
      try {
        const response = await flightAPI.findRoutes({
          source,
          destination,
          algorithm: algorithm as any,
          optimization: optimization as any,
          num_routes: 3
        });
        setRouteData(response);
      } catch (error) {
        console.error('Error fetching routes:', error);
        toast.error('Failed to find routes. Please try again.');
      } finally {
        setLoading(false);
      }
    };

    if (source && destination) {
      fetchRouteData();
    }
  }, [source, destination, algorithm, optimization]);

  const handleCompareAlgorithms = async () => {
    if (!source || !destination) return;
    
    setComparing(true);
    try {
      const comparison = await flightAPI.compareAlgorithms({
        source,
        destination,
        optimization: optimization as any
      });
      setAlgorithmComparison(comparison);
      toast.success('Algorithm comparison completed');
    } catch (error) {
      console.error('Error comparing algorithms:', error);
      toast.error('Failed to compare algorithms');
    } finally {
      setComparing(false);
    }
  };

  const handleBookFlight = (route: Route) => {
    const routeString = route.airports.join('-');
    const flightString = route.flights.join(',');
    navigate(`/booking?route=${routeString}&flights=${flightString}&cost=${route.total_cost}`);
  };

  const getOptimizationIcon = (routeType: string) => {
    if (routeType.includes('cost')) return <DollarSign className="h-4 w-4" />;
    if (routeType.includes('time')) return <Clock className="h-4 w-4" />;
    if (routeType.includes('reliability')) return <TrendingUp className="h-4 w-4" />;
    return <BarChart3 className="h-4 w-4" />;
  };

  const getOptimizationColor = (routeType: string) => {
    if (routeType.includes('cost')) return 'text-green-600';
    if (routeType.includes('time')) return 'text-blue-600';
    if (routeType.includes('reliability')) return 'text-purple-600';
    return 'text-primary';
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
          <p className="mt-4 text-muted-foreground">Optimizing routes with graph algorithms...</p>
          <p className="text-sm text-muted-foreground mt-2">
            Using {algorithm === 'multiple' ? 'Multiple Algorithms' : algorithm === 'dijkstra' ? "Dijkstra's Algorithm" : "A* Algorithm"}
          </p>
        </div>
      </div>
    );
  }

  if (!routeData || routeData.routes.length === 0) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-center">
          <p className="text-muted-foreground mb-4">No routes found between {source} and {destination}</p>
          <Button onClick={() => navigate("/find-routes")}>
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
            Routes from{" "}
            <span className="text-primary">{source}</span>
            {" "}to{" "}
            <span className="text-accent">{destination}</span>
          </h1>
          <div className="flex flex-wrap gap-2 items-center">
            <Badge variant="secondary">
              {routeData.algorithm_used === 'multiple' ? 'Multiple Algorithms' : 
               routeData.algorithm_used === 'dijkstra' ? "Dijkstra's Algorithm" : 
               "A* Algorithm"}
            </Badge>
            <Badge variant="outline">
              Optimized for: {routeData.optimization_criteria}
            </Badge>
            <Badge variant="outline">
              {routeData.routes_found} route{routeData.routes_found !== 1 ? 's' : ''} found
            </Badge>
          </div>
        </motion.div>

        {/* Algorithm Comparison Button */}
        <motion.div
          initial={{ opacity: 0, x: -20 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ delay: 0.1 }}
          className="mb-6"
        >
          <Button
            variant="outline"
            onClick={handleCompareAlgorithms}
            disabled={comparing}
            className="mb-4"
          >
            {comparing ? (
              <>
                <RefreshCw className="mr-2 h-4 w-4 animate-spin" />
                Comparing Algorithms...
              </>
            ) : (
              <>
                <BarChart3 className="mr-2 h-4 w-4" />
                Compare Dijkstra vs A*
              </>
            )}
          </Button>
        </motion.div>

        <Tabs defaultValue="routes" className="space-y-6">
          <TabsList>
            <TabsTrigger value="routes">Route Options</TabsTrigger>
            <TabsTrigger value="comparison" disabled={!algorithmComparison}>
              Algorithm Comparison
            </TabsTrigger>
            <TabsTrigger value="map">Route Visualization</TabsTrigger>
          </TabsList>

          <TabsContent value="routes" className="space-y-6">
            {/* Route Cards */}
            {routeData.routes.map((route, index) => (
              <motion.div
                key={index}
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 0.1 * index }}
              >
                <Card className="shadow-lg hover:shadow-xl transition-shadow duration-300">
                  <CardHeader>
                    <div className="flex items-start justify-between">
                      <div className="flex-1">
                        <CardTitle className="flex items-center gap-2">
                          <div className={`p-1.5 rounded-lg ${getOptimizationColor(route.route_type)} bg-current/10`}>
                            {getOptimizationIcon(route.route_type)}
                          </div>
                          <span className="capitalize">{route.route_type.replace('_', ' ')} Route</span>
                          {index === 0 && (
                            <Badge variant="default" className="ml-2">Recommended</Badge>
                          )}
                        </CardTitle>
                        <CardDescription className="mt-2">
                          {route.stops === 0 ? 'Direct flight' : `${route.stops} stop${route.stops > 1 ? 's' : ''}`}
                        </CardDescription>
                      </div>
                    </div>
                  </CardHeader>
                  <CardContent>
                    {/* Stats Row */}
                    <div className="grid md:grid-cols-4 gap-6 mb-6">
                      <div>
                        <div className="text-sm text-muted-foreground mb-1">Total Cost</div>
                        <div className="text-2xl font-bold text-primary">
                          ₹{route.total_cost.toLocaleString()}
                        </div>
                      </div>
                      <div>
                        <div className="text-sm text-muted-foreground mb-1">Duration</div>
                        <div className="text-2xl font-bold text-accent">
                          {route.total_duration.toFixed(1)}h
                        </div>
                      </div>
                      <div>
                        <div className="text-sm text-muted-foreground mb-1">Reliability</div>
                        <div className="text-2xl font-bold text-green-600">
                          {((1 - route.average_delay_probability) * 100).toFixed(0)}%
                        </div>
                      </div>
                      <div>
                        <div className="text-sm text-muted-foreground mb-1">Delay Risk</div>
                        <Badge 
                          variant={route.average_delay_probability < 0.1 ? "default" : 
                                  route.average_delay_probability < 0.2 ? "secondary" : "destructive"}
                        >
                          {route.average_delay_probability < 0.1 ? 'Low' : 
                           route.average_delay_probability < 0.2 ? 'Medium' : 'High'}
                        </Badge>
                      </div>
                    </div>

                    {/* Route Path */}
                    <div className="mb-6">
                      <div className="text-sm text-muted-foreground mb-2">Flight Path</div>
                      <div className="flex items-center justify-between flex-wrap gap-4">
                        {route.airports.map((airport, airportIndex) => (
                          <div key={airportIndex} className="flex items-center">
                            <div className="text-center">
                              <div className="w-10 h-10 rounded-full bg-gradient-to-r from-primary to-accent flex items-center justify-center text-white font-bold mb-2 text-sm">
                                {airportIndex + 1}
                              </div>
                              <div className="font-semibold text-sm">{airport}</div>
                              <div className="text-xs text-muted-foreground">
                                {airportIndex === 0 ? "Origin" : 
                                 airportIndex === route.airports.length - 1 ? "Destination" : "Layover"}
                              </div>
                            </div>
                            {airportIndex < route.airports.length - 1 && (
                              <div className="mx-4 flex-1 min-w-[60px]">
                                <div className="h-0.5 bg-gradient-to-r from-primary to-accent" />
                                <Plane className="h-4 w-4 text-primary mx-auto -mt-2.5" />
                              </div>
                            )}
                          </div>
                        ))}
                      </div>
                    </div>

                    {/* Flight Numbers */}
                    <div className="mb-6">
                      <div className="text-sm text-muted-foreground mb-2">Flight Numbers</div>
                      <div className="flex flex-wrap gap-2">
                        {route.flights.map((flight, flightIndex) => (
                          <Badge key={flightIndex} variant="outline">
                            {flight}
                          </Badge>
                        ))}
                      </div>
                    </div>

                    {/* Book Button */}
                    <Button
                      onClick={() => handleBookFlight(route)}
                      variant={index === 0 ? "hero" : "default"}
                      className="w-full"
                    >
                      Book This Route
                    </Button>
                  </CardContent>
                </Card>
              </motion.div>
            ))}
          </TabsContent>

          <TabsContent value="comparison">
            {algorithmComparison && (
              <Card className="shadow-lg">
                <CardHeader>
                  <CardTitle className="flex items-center gap-2">
                    <BarChart3 className="h-5 w-5 text-primary" />
                    Algorithm Performance Comparison
                  </CardTitle>
                  <CardDescription>
                    Comparing Dijkstra's Algorithm vs A* Algorithm for {optimization} optimization
                  </CardDescription>
                </CardHeader>
                <CardContent>
                  <div className="grid md:grid-cols-2 gap-6">
                    {/* Dijkstra Results */}
                    <div className="space-y-4">
                      <h3 className="text-lg font-semibold flex items-center gap-2">
                        <BarChart3 className="h-5 w-5 text-blue-600" />
                        Dijkstra's Algorithm
                      </h3>
                      {algorithmComparison.dijkstra ? (
                        <div className="space-y-2">
                          <div className="flex justify-between">
                            <span className="text-muted-foreground">Route:</span>
                            <span>{algorithmComparison.dijkstra.airports.join(' → ')}</span>
                          </div>
                          <div className="flex justify-between">
                            <span className="text-muted-foreground">Cost:</span>
                            <span className="font-semibold">₹{algorithmComparison.dijkstra.total_cost.toLocaleString()}</span>
                          </div>
                          <div className="flex justify-between">
                            <span className="text-muted-foreground">Duration:</span>
                            <span className="font-semibold">{algorithmComparison.dijkstra.total_duration.toFixed(1)}h</span>
                          </div>
                        </div>
                      ) : (
                        <p className="text-muted-foreground">No route found</p>
                      )}
                    </div>

                    {/* A* Results */}
                    <div className="space-y-4">
                      <h3 className="text-lg font-semibold flex items-center gap-2">
                        <Zap className="h-5 w-5 text-yellow-600" />
                        A* Algorithm
                      </h3>
                      {algorithmComparison.a_star ? (
                        <div className="space-y-2">
                          <div className="flex justify-between">
                            <span className="text-muted-foreground">Route:</span>
                            <span>{algorithmComparison.a_star.airports.join(' → ')}</span>
                          </div>
                          <div className="flex justify-between">
                            <span className="text-muted-foreground">Cost:</span>
                            <span className="font-semibold">₹{algorithmComparison.a_star.total_cost.toLocaleString()}</span>
                          </div>
                          <div className="flex justify-between">
                            <span className="text-muted-foreground">Duration:</span>
                            <span className="font-semibold">{algorithmComparison.a_star.total_duration.toFixed(1)}h</span>
                          </div>
                        </div>
                      ) : (
                        <p className="text-muted-foreground">No route found</p>
                      )}
                    </div>
                  </div>

                  {/* Comparison Summary */}
                  {algorithmComparison.comparison && (
                    <div className="mt-6 p-4 bg-muted/50 rounded-lg">
                      <h4 className="font-semibold mb-2">Comparison Summary</h4>
                      <div className="space-y-2 text-sm">
                        <div className="flex justify-between">
                          <span>Same route found:</span>
                          <Badge variant={algorithmComparison.comparison.same_route ? "default" : "secondary"}>
                            {algorithmComparison.comparison.same_route ? "Yes" : "No"}
                          </Badge>
                        </div>
                        {!algorithmComparison.comparison.same_route && (
                          <>
                            <div className="flex justify-between">
                              <span>Cost difference:</span>
                              <span>₹{algorithmComparison.comparison.cost_difference.toLocaleString()}</span>
                            </div>
                            <div className="flex justify-between">
                              <span>Time difference:</span>
                              <span>{algorithmComparison.comparison.time_difference.toFixed(1)}h</span>
                            </div>
                          </>
                        )}
                      </div>
                    </div>
                  )}
                </CardContent>
              </Card>
            )}
          </TabsContent>

          <TabsContent value="map">
            {routeData.routes.length > 1 ? (
              <MapVisualization 
                routes={routeData.routes}
                showComparison={true}
              />
            ) : routeData.routes.length === 1 ? (
              <MapVisualization 
                route={routeData.routes[0].airports}
                flights={routeData.routes[0].flights}
                routeType={routeData.routes[0].route_type}
              />
            ) : (
              <Card className="shadow-lg">
                <CardContent className="text-center py-12">
                  <p className="text-muted-foreground">No routes available for visualization</p>
                </CardContent>
              </Card>
            )}
          </TabsContent>
        </Tabs>
      </div>
    </div>
  );
};

export default RouteResults;
