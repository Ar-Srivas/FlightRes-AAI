import { useEffect, useState } from "react";
import { TrendingUp, AlertTriangle, CheckCircle, Info, RefreshCw, Plane, BarChart3 } from "lucide-react";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Progress } from "@/components/ui/progress";
import { Button } from "@/components/ui/button";
import { toast } from "sonner";
import { flightAPI, DelayPrediction, NetworkStats } from "@/lib/api";

const Predictions = () => {
  const [predictions, setPredictions] = useState<DelayPrediction[]>([]);
  const [networkStats, setNetworkStats] = useState<NetworkStats | null>(null);
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);
  const [lastUpdated, setLastUpdated] = useState<Date | null>(null);

  const loadPredictions = async (showToast = false) => {
    try {
      setRefreshing(true);
      const [predictionsData, statsData] = await Promise.all([
        flightAPI.getDelayPredictions(),
        flightAPI.getNetworkStats()
      ]);

      setPredictions(predictionsData.predictions);
      setNetworkStats(statsData);
      setLastUpdated(new Date(predictionsData.generated_at));

      if (showToast) {
        toast.success('Predictions updated successfully');
      }
    } catch (error) {
      console.error('Error loading predictions:', error);
      toast.error('Failed to load predictions');
    } finally {
      setLoading(false);
      setRefreshing(false);
    }
  };

  useEffect(() => {
    loadPredictions();
  }, []);

  const handleRefresh = () => {
    loadPredictions(true);
  };

  const getReliabilityColor = (prob: number) => {
    if (prob < 0.1) return "text-green-600";
    if (prob < 0.2) return "text-blue-600";
    if (prob < 0.3) return "text-yellow-600";
    return "text-red-600";
  };

  const getReliabilityIcon = (prob: number) => {
    if (prob < 0.15) return <CheckCircle className="h-5 w-5 text-green-600" />;
    if (prob < 0.25) return <Info className="h-5 w-5 text-blue-600" />;
    return <AlertTriangle className="h-5 w-5 text-yellow-600" />;
  };

  const getRiskBadgeVariant = (riskLevel: string) => {
    switch (riskLevel) {
      case 'low': return 'default';
      case 'medium': return 'secondary';
      case 'high': return 'destructive';
      default: return 'outline';
    }
  };

  const getRiskStats = () => {
    const high = predictions.filter(p => p.risk_level === 'high').length;
    const medium = predictions.filter(p => p.risk_level === 'medium').length;
    const low = predictions.filter(p => p.risk_level === 'low').length;
    const total = predictions.length;

    return { high, medium, low, total };
  };

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gradient-to-b from-background to-secondary/20">
        <div className="text-center">
            <Plane className="h-12 w-12 text-primary" />
          <p className="mt-4 text-muted-foreground">Analyzing flight delay patterns...</p>
        </div>
      </div>
    );
  }

  const riskStats = getRiskStats();

  return (
    <div className="min-h-screen py-12 bg-gradient-to-b from-background via-secondary/20 to-background">
      <div className="container mx-auto px-4 sm:px-6 lg:px-8">
        {/* Header */}
          <h1 className="text-4xl font-bold mb-4">
            Flight{" "}
            <span className="bg-gradient-to-r from-primary to-accent bg-clip-text text-transparent">
              Predictions
            </span>
          </h1>
          <p className="text-muted-foreground text-lg max-w-2xl mx-auto mb-6">
            AI-powered delay predictions using graph theory and real-time network analysis
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
                  Updating...
                </>
              ) : (
                <>
                  <RefreshCw className="mr-2 h-4 w-4" />
                  Refresh Predictions
                </>
              )}
            </Button>
            {lastUpdated && (
              <p className="text-sm text-muted-foreground">
                Last updated: {lastUpdated.toLocaleTimeString()}
              </p>
            )}
          </div>

        {/* Network Overview */}
        {networkStats && (
            <Card className="bg-gradient-to-r from-primary/5 to-accent/5 border-primary/20">
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <BarChart3 className="h-5 w-5 text-primary" />
                  Network Health Overview
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="grid grid-cols-2 md:grid-cols-5 gap-4 text-sm">
                  <div>
                    <div className="text-muted-foreground">Total Flights</div>
                    <div className="text-2xl font-bold text-primary">{networkStats.total_flights}</div>
                  </div>
                  <div>
                    <div className="text-muted-foreground">Network Reliability</div>
                    <div className="text-2xl font-bold text-green-600">
                      {((1 - networkStats.avg_delay_probability) * 100).toFixed(0)}%
                    </div>
                  </div>
                  <div>
                    <div className="text-muted-foreground">Currently Delayed</div>
                    <div className="text-2xl font-bold text-yellow-600">{networkStats.delayed_flights}</div>
                  </div>
                  <div>
                    <div className="text-muted-foreground">Cancelled Today</div>
                    <div className="text-2xl font-bold text-red-600">{networkStats.cancelled_flights}</div>
                  </div>
                  <div>
                    <div className="text-muted-foreground">Predictions Made</div>
                    <div className="text-2xl font-bold text-accent">{predictions.length}</div>
                  </div>
                </div>
              </CardContent>
            </Card>
        )}

        {/* Risk Distribution */}
        <div className="grid md:grid-cols-4 gap-6 mb-12">
            <Card className="shadow-lg">
              <CardHeader>
                <CardTitle className="flex items-center gap-2 text-lg">
                  <TrendingUp className="h-5 w-5 text-primary" />
                  Total Analyzed
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="text-3xl font-bold text-primary mb-2">{riskStats.total}</div>
                <Progress value={100} className="mb-2" />
                <p className="text-sm text-muted-foreground">Active flights tracked</p>
              </CardContent>
            </Card>

            <Card className="shadow-lg">
              <CardHeader>
                <CardTitle className="flex items-center gap-2 text-lg">
                  <CheckCircle className="h-5 w-5 text-green-600" />
                  Low Risk
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="text-3xl font-bold text-green-600 mb-2">{riskStats.low}</div>
                <Progress value={(riskStats.low / riskStats.total) * 100} className="mb-2" />
                <p className="text-sm text-muted-foreground">Reliable flights</p>
              </CardContent>
            </Card>
            <Card className="shadow-lg">
              <CardHeader>
                <CardTitle className="flex items-center gap-2 text-lg">
                  <Info className="h-5 w-5 text-blue-600" />
                  Medium Risk
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="text-3xl font-bold text-blue-600 mb-2">{riskStats.medium}</div>
                <Progress value={(riskStats.medium / riskStats.total) * 100} className="mb-2" />
                <p className="text-sm text-muted-foreground">Monitor closely</p>
              </CardContent>
            </Card>
            <Card className="shadow-lg">
              <CardHeader>
                <CardTitle className="flex items-center gap-2 text-lg">
                  <AlertTriangle className="h-5 w-5 text-red-600" />
                  High Risk
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="text-3xl font-bold text-red-600 mb-2">{riskStats.high}</div>
                <Progress value={(riskStats.high / riskStats.total) * 100} className="mb-2" />
                <p className="text-sm text-muted-foreground">Likely delays</p>
              </CardContent>
            </Card>
        </div>
          <h2 className="text-2xl font-bold mb-6">Flight Delay Predictions</h2>
          {predictions.length === 0 ? (
            <Card>
              <CardContent className="text-center py-12">
                <p className="text-muted-foreground">No predictions available. Try refreshing the data.</p>
              </CardContent>
            </Card>
          ) : (
            <div className="grid gap-6">
              {predictions
                .sort((a, b) => b.predicted_delay_probability - a.predicted_delay_probability)
                .map((pred, index) => (

                    <Card className="shadow-lg hover:shadow-xl transition-shadow duration-300">
                      <CardHeader>
                        <div className="flex items-start justify-between">
                          <div className="flex-1">
                            <CardTitle className="flex items-center gap-3">
                              <span className="text-xl font-mono">{pred.flight_number}</span>
                              <span className="text-lg font-normal text-muted-foreground">
                                {pred.source} → {pred.destination}
                              </span>
                              {getReliabilityIcon(pred.predicted_delay_probability)}
                            </CardTitle>
                            <CardDescription className="mt-2">
                              Real-time delay prediction based on network analysis
                            </CardDescription>
                          </div>
                          <Badge variant={getRiskBadgeVariant(pred.risk_level)}>
                            {pred.risk_level.toUpperCase()} RISK
                          </Badge>
                        </div>
                      </CardHeader>
                      <CardContent>
                        <div className="grid md:grid-cols-3 gap-6">
                          <div>
                            <div className="text-sm text-muted-foreground mb-1">Delay Probability</div>
                            <div className={`text-2xl font-bold ${getReliabilityColor(pred.predicted_delay_probability)}`}>
                              {(pred.predicted_delay_probability * 100).toFixed(1)}%
                            </div>
                            <Progress
                              value={pred.predicted_delay_probability * 100}
                              className="mt-2"
                            />
                          </div>

                          <div>
                            <div className="text-sm text-muted-foreground mb-1">On-Time Probability</div>
                            <div className="text-2xl font-bold text-green-600">
                              {((1 - pred.predicted_delay_probability) * 100).toFixed(1)}%
                            </div>
                            <div className="text-sm text-muted-foreground mt-1">
                              Expected reliability
                            </div>
                          </div>

                          <div>
                            <div className="text-sm text-muted-foreground mb-1">Risk Assessment</div>
                            <div className="flex items-center gap-2 mt-1">
                              {pred.risk_level === 'low' && <CheckCircle className="h-5 w-5 text-green-600" />}
                              {pred.risk_level === 'medium' && <Info className="h-5 w-5 text-blue-600" />}
                              {pred.risk_level === 'high' && <AlertTriangle className="h-5 w-5 text-red-600" />}
                              <span className="text-lg font-semibold capitalize">
                                {pred.risk_level}
                              </span>
                            </div>
                            <div className="text-sm text-muted-foreground mt-1">
                              {pred.risk_level === 'low' && 'Proceed with confidence'}
                              {pred.risk_level === 'medium' && 'Consider alternatives'}
                              {pred.risk_level === 'high' && 'High delay likelihood'}
                            </div>
                          </div>
                        </div>
                      </CardContent>
                    </Card>
                ))}
            </div>
          )}

          <Card className="bg-gradient-to-r from-primary/10 to-accent/10 border-primary/20">
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Info className="h-5 w-5 text-primary" />
                How Our Predictions Work
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-3 text-sm text-muted-foreground">
              <p>
                Our AI system uses <strong>graph theory</strong> to analyze the flight network, considering:
              </p>
              <ul className="list-disc list-inside space-y-1 ml-4">
                <li>Historical delay patterns for each route and aircraft</li>
                <li>Real-time network congestion and bottlenecks</li>
                <li>Weather conditions and seasonal factors</li>
                <li>Airport operational efficiency metrics</li>
                <li>Airline performance statistics</li>
              </ul>
              <p>
                Predictions are updated continuously as new data becomes available,
                ensuring you have the most accurate delay forecasts for informed decision-making.
              </p>
            </CardContent>
          </Card>
      </div>
    </div>
  );
};

export default Predictions;
