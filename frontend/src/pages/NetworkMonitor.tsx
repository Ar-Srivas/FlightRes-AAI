import { useEffect, useState } from "react";
import { motion } from "framer-motion";
import { 
  AlertTriangle, 
  CheckCircle, 
  Clock, 
  Plane, 
  RefreshCw, 
  Settings, 
  TrendingDown,
  TrendingUp,
  Users,
  MapPin,
  BarChart3
} from "lucide-react";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Progress } from "@/components/ui/progress";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { toast } from "sonner";
import { flightAPI, NetworkStats, Flight } from "@/lib/api";
import MapVisualization from "@/components/MapVisualization";

const NetworkMonitor = () => {
  const [networkStats, setNetworkStats] = useState<NetworkStats | null>(null);
  const [flights, setFlights] = useState<Flight[]>([]);
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);
  const [selectedFlight, setSelectedFlight] = useState<string>("");
  const [disruptionType, setDisruptionType] = useState<"delay" | "cancellation">("delay");
  const [delayMinutes, setDelayMinutes] = useState<number>(60);
  const [reason, setReason] = useState<string>("");
  const [processing, setProcessing] = useState(false);

  const loadData = async (showToast = false) => {
    try {
      setRefreshing(true);
      const [statsData, flightsData] = await Promise.all([
        flightAPI.getNetworkStats(),
        flightAPI.getFlights()
      ]);
      
      setNetworkStats(statsData);
      setFlights(flightsData);
      
      if (showToast) {
        toast.success('Network data refreshed');
      }
    } catch (error) {
      console.error('Error loading network data:', error);
      toast.error('Failed to load network data');
    } finally {
      setLoading(false);
      setRefreshing(false);
    }
  };

  useEffect(() => {
    loadData();
  }, []);

  const handleRefresh = () => {
    loadData(true);
  };

  const handleDisruption = async () => {
    if (!selectedFlight) {
      toast.error('Please select a flight');
      return;
    }

    setProcessing(true);
    try {
      const result = await flightAPI.handleDisruption({
        flight_number: selectedFlight,
        type: disruptionType,
        delay_minutes: disruptionType === 'delay' ? delayMinutes : undefined,
        reason: reason || undefined
      });

      toast.success(result.message);
      
      // Reset form
      setSelectedFlight("");
      setReason("");
      setDelayMinutes(60);
      
      // Refresh data
      loadData();
      
    } catch (error) {
      console.error('Error handling disruption:', error);
      toast.error('Failed to handle disruption');
    } finally {
      setProcessing(false);
    }
  };

  const buildNetwork = async () => {
    setProcessing(true);
    try {
      const result = await flightAPI.buildNetwork();
      setNetworkStats(result.statistics);
      toast.success('Network rebuilt successfully');
    } catch (error) {
      console.error('Error building network:', error);
      toast.error('Failed to rebuild network');
    } finally {
      setProcessing(false);
    }
  };

  const getFlightsByStatus = () => {
    const onTime = flights.filter(f => f.status === 'scheduled').length;
    const delayed = flights.filter(f => f.status === 'delayed').length;
    const cancelled = flights.filter(f => f.status === 'cancelled').length;
    return { onTime, delayed, cancelled };
  };

  const getHighRiskFlights = () => {
    return flights.filter(f => f.delay_prob > 0.2);
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
            <Settings className="h-12 w-12 text-primary" />
          </motion.div>
          <p className="mt-4 text-muted-foreground">Loading network monitoring data...</p>
        </div>
      </div>
    );
  }

  const flightStatusStats = getFlightsByStatus();
  const highRiskFlights = getHighRiskFlights();

  return (
    <div className="min-h-screen py-12 bg-gradient-to-b from-background via-secondary/20 to-background">
      <div className="container mx-auto px-4 sm:px-6 lg:px-8">
        {/* Header */}
        <motion.div
          initial={{ opacity: 0, y: -20 }}
          animate={{ opacity: 1, y: 0 }}
          className="text-center mb-12"
        >
          <h1 className="text-4xl font-bold mb-4">
            Network{" "}
            <span className="bg-gradient-to-r from-primary to-accent bg-clip-text text-transparent">
              Monitor
            </span>
          </h1>
          <p className="text-muted-foreground text-lg max-w-2xl mx-auto mb-6">
            Real-time flight network monitoring and disruption management
          </p>
          
          <div className="flex items-center justify-center gap-4">
            <Button
              variant="outline"
              onClick={handleRefresh}
              disabled={refreshing}
            >
              {refreshing ? (
                <>
                  <RefreshCw className="mr-2 h-4 w-4 animate-spin" />
                  Refreshing...
                </>
              ) : (
                <>
                  <RefreshCw className="mr-2 h-4 w-4" />
                  Refresh Data
                </>
              )}
            </Button>
            
            <Button
              variant="default"
              onClick={buildNetwork}
              disabled={processing}
            >
              {processing ? (
                <>
                  <Settings className="mr-2 h-4 w-4 animate-spin" />
                  Building...
                </>
              ) : (
                <>
                  <Settings className="mr-2 h-4 w-4" />
                  Rebuild Network
                </>
              )}
            </Button>
          </div>
        </motion.div>

        {/* Network Overview */}
        {networkStats && (
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.1 }}
            className="mb-8"
          >
            <div className="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-6 gap-4">
              <Card>
                <CardContent className="p-4">
                  <div className="flex items-center gap-2">
                    <MapPin className="h-5 w-5 text-primary" />
                    <div>
                      <div className="text-2xl font-bold">{networkStats.total_airports}</div>
                      <div className="text-xs text-muted-foreground">Airports</div>
                    </div>
                  </div>
                </CardContent>
              </Card>

              <Card>
                <CardContent className="p-4">
                  <div className="flex items-center gap-2">
                    <Plane className="h-5 w-5 text-accent" />
                    <div>
                      <div className="text-2xl font-bold">{networkStats.total_flights}</div>
                      <div className="text-xs text-muted-foreground">Total Flights</div>
                    </div>
                  </div>
                </CardContent>
              </Card>

              <Card>
                <CardContent className="p-4">
                  <div className="flex items-center gap-2">
                    <Clock className="h-5 w-5 text-yellow-600" />
                    <div>
                      <div className="text-2xl font-bold text-yellow-600">{networkStats.delayed_flights}</div>
                      <div className="text-xs text-muted-foreground">Delayed</div>
                    </div>
                  </div>
                </CardContent>
              </Card>

              <Card>
                <CardContent className="p-4">
                  <div className="flex items-center gap-2">
                    <AlertTriangle className="h-5 w-5 text-red-600" />
                    <div>
                      <div className="text-2xl font-bold text-red-600">{networkStats.cancelled_flights}</div>
                      <div className="text-xs text-muted-foreground">Cancelled</div>
                    </div>
                  </div>
                </CardContent>
              </Card>

              <Card>
                <CardContent className="p-4">
                  <div className="flex items-center gap-2">
                    <TrendingUp className="h-5 w-5 text-green-600" />
                    <div>
                      <div className="text-2xl font-bold text-green-600">
                        {((1 - networkStats.avg_delay_probability) * 100).toFixed(0)}%
                      </div>
                      <div className="text-xs text-muted-foreground">Reliability</div>
                    </div>
                  </div>
                </CardContent>
              </Card>

              <Card>
                <CardContent className="p-4">
                  <div className="flex items-center gap-2">
                    <BarChart3 className="h-5 w-5 text-primary" />
                    <div>
                      <div className="text-2xl font-bold">{networkStats.network_connectivity.toFixed(1)}</div>
                      <div className="text-xs text-muted-foreground">Connectivity</div>
                    </div>
                  </div>
                </CardContent>
              </Card>
            </div>
          </motion.div>
        )}

        <Tabs defaultValue="overview" className="space-y-6">
          <TabsList className="grid w-full grid-cols-4">
            <TabsTrigger value="overview">Network Overview</TabsTrigger>
            <TabsTrigger value="map">Network Map</TabsTrigger>
            <TabsTrigger value="disruptions">Manage Disruptions</TabsTrigger>
            <TabsTrigger value="flights">Flight Status</TabsTrigger>
          </TabsList>

          <TabsContent value="overview" className="space-y-6">
            {/* Flight Status Distribution */}
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.2 }}
            >
              <Card>
                <CardHeader>
                  <CardTitle className="flex items-center gap-2">
                    <BarChart3 className="h-5 w-5 text-primary" />
                    Flight Status Distribution
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="grid md:grid-cols-3 gap-6">
                    <div className="space-y-2">
                      <div className="flex items-center justify-between">
                        <span className="text-sm font-medium">On Time</span>
                        <span className="text-sm text-muted-foreground">{flightStatusStats.onTime}</span>
                      </div>
                      <Progress value={(flightStatusStats.onTime / flights.length) * 100} className="h-2" />
                      <div className="flex items-center gap-2">
                        <CheckCircle className="h-4 w-4 text-green-600" />
                        <span className="text-sm text-green-600">
                          {((flightStatusStats.onTime / flights.length) * 100).toFixed(1)}%
                        </span>
                      </div>
                    </div>

                    <div className="space-y-2">
                      <div className="flex items-center justify-between">
                        <span className="text-sm font-medium">Delayed</span>
                        <span className="text-sm text-muted-foreground">{flightStatusStats.delayed}</span>
                      </div>
                      <Progress value={(flightStatusStats.delayed / flights.length) * 100} className="h-2" />
                      <div className="flex items-center gap-2">
                        <Clock className="h-4 w-4 text-yellow-600" />
                        <span className="text-sm text-yellow-600">
                          {((flightStatusStats.delayed / flights.length) * 100).toFixed(1)}%
                        </span>
                      </div>
                    </div>

                    <div className="space-y-2">
                      <div className="flex items-center justify-between">
                        <span className="text-sm font-medium">Cancelled</span>
                        <span className="text-sm text-muted-foreground">{flightStatusStats.cancelled}</span>
                      </div>
                      <Progress value={(flightStatusStats.cancelled / flights.length) * 100} className="h-2" />
                      <div className="flex items-center gap-2">
                        <AlertTriangle className="h-4 w-4 text-red-600" />
                        <span className="text-sm text-red-600">
                          {((flightStatusStats.cancelled / flights.length) * 100).toFixed(1)}%
                        </span>
                      </div>
                    </div>
                  </div>
                </CardContent>
              </Card>
            </motion.div>

            {/* High Risk Flights */}
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.3 }}
            >
              <Card>
                <CardHeader>
                  <CardTitle className="flex items-center gap-2">
                    <AlertTriangle className="h-5 w-5 text-red-600" />
                    High Risk Flights
                  </CardTitle>
                  <CardDescription>
                    Flights with delay probability above 20%
                  </CardDescription>
                </CardHeader>
                <CardContent>
                  {highRiskFlights.length === 0 ? (
                    <p className="text-muted-foreground text-center py-4">
                      No high-risk flights detected
                    </p>
                  ) : (
                    <div className="space-y-4">
                      {highRiskFlights.slice(0, 5).map((flight, index) => (
                        <div key={flight.id} className="flex items-center justify-between p-3 border rounded-lg">
                          <div className="flex items-center gap-3">
                            <Badge variant="destructive">{flight.flight_number}</Badge>
                            <span>{flight.source.code} → {flight.destination.code}</span>
                          </div>
                          <div className="flex items-center gap-2">
                            <span className="text-sm text-muted-foreground">
                              {(flight.delay_prob * 100).toFixed(1)}% delay risk
                            </span>
                            <Badge variant={flight.status === 'scheduled' ? 'default' : 'destructive'}>
                              {flight.status}
                            </Badge>
                          </div>
                        </div>
                      ))}
                    </div>
                  )}
                </CardContent>
              </Card>
            </motion.div>
          </TabsContent>

          <TabsContent value="map">
            <MapVisualization showNetworkOverview={true} />
          </TabsContent>

          <TabsContent value="disruptions" className="space-y-6">
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.2 }}
            >
              <Card>
                <CardHeader>
                  <CardTitle className="flex items-center gap-2">
                    <Settings className="h-5 w-5 text-primary" />
                    Simulate Flight Disruption
                  </CardTitle>
                  <CardDescription>
                    Test the system's response to flight delays and cancellations
                  </CardDescription>
                </CardHeader>
                <CardContent className="space-y-4">
                  <div className="grid md:grid-cols-2 gap-4">
                    <div className="space-y-2">
                      <Label htmlFor="flight-select">Select Flight</Label>
                      <Select value={selectedFlight} onValueChange={setSelectedFlight}>
                        <SelectTrigger id="flight-select">
                          <SelectValue placeholder="Choose a flight" />
                        </SelectTrigger>
                        <SelectContent className="bg-popover max-h-60">
                          {flights
                            .filter(f => f.status === 'scheduled')
                            .map((flight) => (
                              <SelectItem key={flight.id} value={flight.flight_number}>
                                {flight.flight_number} - {flight.source.code} → {flight.destination.code}
                              </SelectItem>
                            ))}
                        </SelectContent>
                      </Select>
                    </div>

                    <div className="space-y-2">
                      <Label htmlFor="disruption-type">Disruption Type</Label>
                      <Select value={disruptionType} onValueChange={(value: "delay" | "cancellation") => setDisruptionType(value)}>
                        <SelectTrigger id="disruption-type">
                          <SelectValue />
                        </SelectTrigger>
                        <SelectContent className="bg-popover">
                          <SelectItem value="delay">Flight Delay</SelectItem>
                          <SelectItem value="cancellation">Flight Cancellation</SelectItem>
                        </SelectContent>
                      </Select>
                    </div>
                  </div>

                  {disruptionType === 'delay' && (
                    <div className="space-y-2">
                      <Label htmlFor="delay-minutes">Delay Duration (minutes)</Label>
                      <Input
                        id="delay-minutes"
                        type="number"
                        min="15"
                        max="480"
                        value={delayMinutes}
                        onChange={(e) => setDelayMinutes(Number(e.target.value))}
                      />
                    </div>
                  )}

                  <div className="space-y-2">
                    <Label htmlFor="reason">Reason (Optional)</Label>
                    <Input
                      id="reason"
                      placeholder="e.g., Weather conditions, Technical issues"
                      value={reason}
                      onChange={(e) => setReason(e.target.value)}
                    />
                  </div>

                  <Button
                    onClick={handleDisruption}
                    disabled={processing || !selectedFlight}
                    className="w-full"
                  >
                    {processing ? (
                      <>
                        <RefreshCw className="mr-2 h-4 w-4 animate-spin" />
                        Processing...
                      </>
                    ) : (
                      <>
                        <AlertTriangle className="mr-2 h-4 w-4" />
                        Simulate {disruptionType === 'delay' ? 'Delay' : 'Cancellation'}
                      </>
                    )}
                  </Button>
                </CardContent>
              </Card>
            </motion.div>
          </TabsContent>

          <TabsContent value="flights" className="space-y-6">
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.2 }}
            >
              <Card>
                <CardHeader>
                  <CardTitle>All Flights Status</CardTitle>
                  <CardDescription>Real-time status of all flights in the network</CardDescription>
                </CardHeader>
                <CardContent>
                  <div className="space-y-4">
                    {flights.map((flight, index) => (
                      <div key={flight.id} className="flex items-center justify-between p-3 border rounded-lg">
                        <div className="flex items-center gap-4">
                          <Badge variant="outline">{flight.flight_number}</Badge>
                          <span className="font-medium">
                            {flight.source.code} → {flight.destination.code}
                          </span>
                          <span className="text-sm text-muted-foreground">
                            {flight.departure_time} - {flight.arrival_time}
                          </span>
                        </div>
                        <div className="flex items-center gap-3">
                          <span className="text-sm text-muted-foreground">
                            ₹{flight.price.toLocaleString()}
                          </span>
                          <span className="text-sm text-muted-foreground">
                            {flight.duration}h
                          </span>
                          <Badge 
                            variant={
                              flight.status === 'scheduled' ? 'default' :
                              flight.status === 'delayed' ? 'secondary' :
                              'destructive'
                            }
                          >
                            {flight.status}
                          </Badge>
                          <span className="text-sm text-muted-foreground">
                            {flight.current_bookings}/{flight.max_capacity}
                          </span>
                        </div>
                      </div>
                    ))}
                  </div>
                </CardContent>
              </Card>
            </motion.div>
          </TabsContent>
        </Tabs>
      </div>
    </div>
  );
};

export default NetworkMonitor;