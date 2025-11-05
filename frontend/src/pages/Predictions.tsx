import { motion } from "framer-motion";
import { TrendingUp, AlertTriangle, CheckCircle, Info } from "lucide-react";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Progress } from "@/components/ui/progress";

const Predictions = () => {
  const predictions = [
    {
      route: "JFK → LHR",
      delayProbability: 0.12,
      priceChange: "+5%",
      reliability: "High",
      recommendation: "Book now - prices expected to rise",
    },
    {
      route: "LAX → NRT",
      delayProbability: 0.08,
      priceChange: "-3%",
      reliability: "Very High",
      recommendation: "Wait 2-3 days for better prices",
    },
    {
      route: "DXB → SIN",
      delayProbability: 0.22,
      priceChange: "+2%",
      reliability: "Moderate",
      recommendation: "Consider alternative dates",
    },
    {
      route: "CDG → JFK",
      delayProbability: 0.15,
      priceChange: "Stable",
      reliability: "Good",
      recommendation: "Good time to book",
    },
  ];

  const getReliabilityColor = (prob: number) => {
    if (prob < 0.1) return "text-green-600";
    if (prob < 0.15) return "text-blue-600";
    if (prob < 0.2) return "text-yellow-600";
    return "text-red-600";
  };

  const getReliabilityIcon = (prob: number) => {
    if (prob < 0.15) return <CheckCircle className="h-5 w-5 text-green-600" />;
    if (prob < 0.2) return <Info className="h-5 w-5 text-blue-600" />;
    return <AlertTriangle className="h-5 w-5 text-yellow-600" />;
  };

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
            Flight{" "}
            <span className="bg-gradient-to-r from-primary to-accent bg-clip-text text-transparent">
              Predictions
            </span>
          </h1>
          <p className="text-muted-foreground text-lg max-w-2xl mx-auto">
            AI-powered insights on delay probabilities and price trends for popular routes
          </p>
        </motion.div>

        {/* Stats Overview */}
        <div className="grid md:grid-cols-3 gap-6 mb-12">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.1 }}
          >
            <Card className="shadow-lg">
              <CardHeader>
                <CardTitle className="flex items-center gap-2 text-lg">
                  <TrendingUp className="h-5 w-5 text-primary" />
                  Prediction Accuracy
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="text-3xl font-bold text-primary mb-2">98.2%</div>
                <Progress value={98} className="mb-2" />
                <p className="text-sm text-muted-foreground">Based on 10K+ flights</p>
              </CardContent>
            </Card>
          </motion.div>

          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.2 }}
          >
            <Card className="shadow-lg">
              <CardHeader>
                <CardTitle className="flex items-center gap-2 text-lg">
                  <CheckCircle className="h-5 w-5 text-green-600" />
                  Routes Analyzed
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="text-3xl font-bold text-green-600 mb-2">500+</div>
                <Progress value={75} className="mb-2" />
                <p className="text-sm text-muted-foreground">Major airports worldwide</p>
              </CardContent>
            </Card>
          </motion.div>

          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.3 }}
          >
            <Card className="shadow-lg">
              <CardHeader>
                <CardTitle className="flex items-center gap-2 text-lg">
                  <AlertTriangle className="h-5 w-5 text-accent" />
                  Avg. Delay Rate
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="text-3xl font-bold text-accent mb-2">12.4%</div>
                <Progress value={12} className="mb-2" />
                <p className="text-sm text-muted-foreground">Across all routes</p>
              </CardContent>
            </Card>
          </motion.div>
        </div>

        {/* Predictions List */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.4 }}
        >
          <h2 className="text-2xl font-bold mb-6">Popular Route Predictions</h2>
          <div className="grid gap-6">
            {predictions.map((pred, index) => (
              <motion.div
                key={pred.route}
                initial={{ opacity: 0, x: -20 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ delay: 0.1 * index }}
              >
                <Card className="shadow-lg hover:shadow-xl transition-shadow duration-300">
                  <CardHeader>
                    <div className="flex items-start justify-between">
                      <div className="flex-1">
                        <CardTitle className="flex items-center gap-3">
                          <span className="text-xl">{pred.route}</span>
                          {getReliabilityIcon(pred.delayProbability)}
                        </CardTitle>
                        <CardDescription className="mt-2">
                          {pred.recommendation}
                        </CardDescription>
                      </div>
                      <Badge
                        variant={pred.priceChange.startsWith("+") ? "destructive" : "secondary"}
                      >
                        {pred.priceChange}
                      </Badge>
                    </div>
                  </CardHeader>
                  <CardContent>
                    <div className="grid md:grid-cols-3 gap-6">
                      <div>
                        <div className="text-sm text-muted-foreground mb-1">Delay Probability</div>
                        <div className={`text-2xl font-bold ${getReliabilityColor(pred.delayProbability)}`}>
                          {(pred.delayProbability * 100).toFixed(1)}%
                        </div>
                        <Progress
                          value={pred.delayProbability * 100}
                          className="mt-2"
                        />
                      </div>

                      <div>
                        <div className="text-sm text-muted-foreground mb-1">Reliability</div>
                        <div className="text-2xl font-bold text-foreground">
                          {pred.reliability}
                        </div>
                        <div className="text-sm text-muted-foreground mt-1">
                          {((1 - pred.delayProbability) * 100).toFixed(0)}% on-time
                        </div>
                      </div>

                      <div>
                        <div className="text-sm text-muted-foreground mb-1">Price Trend</div>
                        <div className="flex items-center gap-2 mt-1">
                          <TrendingUp
                            className={`h-5 w-5 ${
                              pred.priceChange.startsWith("+")
                                ? "text-red-600"
                                : pred.priceChange.startsWith("-")
                                ? "text-green-600"
                                : "text-muted-foreground"
                            }`}
                          />
                          <span className="text-lg font-semibold">
                            {pred.priceChange}
                          </span>
                        </div>
                        <div className="text-sm text-muted-foreground mt-1">Next 7 days</div>
                      </div>
                    </div>
                  </CardContent>
                </Card>
              </motion.div>
            ))}
          </div>
        </motion.div>

        {/* Info Section */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.6 }}
          className="mt-12"
        >
          <Card className="bg-gradient-to-r from-primary/10 to-accent/10 border-primary/20">
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Info className="h-5 w-5 text-primary" />
                How We Predict
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-2 text-sm text-muted-foreground">
              <p>
                Our AI analyzes historical flight data, weather patterns, airline performance, and seasonal trends
                to provide accurate delay predictions and price forecasts.
              </p>
              <p>
                Predictions are updated daily based on the latest available data and market conditions.
              </p>
            </CardContent>
          </Card>
        </motion.div>
      </div>
    </div>
  );
};

export default Predictions;
