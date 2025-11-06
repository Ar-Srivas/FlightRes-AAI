import { Link } from "react-router-dom";
import { motion } from "framer-motion";
import { 
  Plane, 
  TrendingDown, 
  Clock, 
  Shield, 
  ArrowRight, 
  BarChart3, 
  Zap, 
  GitBranch,
  Activity,
  Brain,
  Network
} from "lucide-react";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";

const Home = () => {
  const features = [
    {
      icon: GitBranch,
      title: "Graph Theory",
      description: "Advanced network analysis with airports as nodes and flights as edges",
      color: "text-blue-600"
    },
    {
      icon: BarChart3,
      title: "Dijkstra's Algorithm",
      description: "Guaranteed optimal paths for cost, time, and reliability optimization",
      color: "text-green-600"
    },
    {
      icon: Zap,
      title: "A* Algorithm",
      description: "Heuristic-based search for faster route discovery with geographic intelligence",
      color: "text-yellow-600"
    },
    {
      icon: Brain,
      title: "AI Predictions",
      description: "Machine learning models predict delays and optimize routes in real-time",
      color: "text-purple-600"
    },
    {
      icon: Activity,
      title: "Live Monitoring",
      description: "Real-time network health monitoring and disruption management",
      color: "text-red-600"
    },
    {
      icon: Network,
      title: "Dynamic Re-routing",
      description: "Instant alternative route calculation when flights are delayed or cancelled",
      color: "text-indigo-600"
    },
  ];

  const algorithmFeatures = [
    {
      icon: TrendingDown,
      title: "Cost Optimization",
      description: "Find the most affordable routes using price-weighted graph traversal",
    },
    {
      icon: Clock,
      title: "Time Optimization", 
      description: "Minimize travel duration with time-efficient path finding algorithms",
    },
    {
      icon: Shield,
      title: "Reliability Optimization",
      description: "Choose routes with lowest delay probability using historical data analysis",
    },
  ];

  return (
    <div className="min-h-screen">
      {/* Hero Section */}
      <section className="relative overflow-hidden bg-gradient-to-b from-background via-secondary/20 to-background">
        <div className="absolute inset-0 bg-[url('data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iNjAiIGhlaWdodD0iNjAiIHhtbG5zPSJodHRwOi8vd3d3LnczLm9yZy8yMDAwL3N2ZyI+PGRlZnM+PHBhdHRlcm4gaWQ9ImdyaWQiIHdpZHRoPSI2MCIgaGVpZ2h0PSI2MCIgcGF0dGVyblVuaXRzPSJ1c2VyU3BhY2VPblVzZSI+PHBhdGggZD0iTSAxMCAwIEwgMCAwIDAgMTAiIGZpbGw9Im5vbmUiIHN0cm9rZT0iaHNsKDE5OSA4OSUgNDglIC8gMC4wNSkiIHN0cm9rZS13aWR0aD0iMSIvPjwvcGF0dGVybj48L2RlZnM+PHJlY3Qgd2lkdGg9IjEwMCUiIGhlaWdodD0iMTAwJSIgZmlsbD0idXJsKCNncmlkKSIvPjwvc3ZnPg==')] opacity-40" />
        
        <div className="container mx-auto px-4 sm:px-6 lg:px-8 relative">
          <div className="text-center py-20 lg:py-32">
            {/* Hero Content */}
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.6 }}
              className="space-y-8 max-w-4xl mx-auto"
            >
              <div className="inline-flex items-center gap-2 px-4 py-2 bg-secondary rounded-full text-sm font-medium text-primary">
                <Network className="h-4 w-4" />
                <span>Powered by Graph Theory & AI</span>
              </div>
              
              <h1 className="text-4xl sm:text-5xl lg:text-7xl font-bold leading-tight">
                Intelligent{" "}
                <span className="bg-gradient-to-r from-primary to-accent bg-clip-text text-transparent">
                  Flight Network
                </span>
                <br />
                Route Optimization
              </h1>
              
              <p className="text-xl text-muted-foreground max-w-2xl mx-auto leading-relaxed">
                Advanced algorithms meet real-world aviation. Our system uses{" "}
                <span className="font-semibold text-primary">Dijkstra's & A* algorithms</span>{" "}
                to find optimal flight routes while predicting delays and managing disruptions in real-time.
              </p>

              <div className="flex flex-wrap items-center justify-center gap-4">
                <Badge variant="outline" className="px-4 py-2">
                  <GitBranch className="h-4 w-4 mr-2" />
                  Graph Theory
                </Badge>
                <Badge variant="outline" className="px-4 py-2">
                  <BarChart3 className="h-4 w-4 mr-2" />
                  Dijkstra's Algorithm
                </Badge>
                <Badge variant="outline" className="px-4 py-2">
                  <Zap className="h-4 w-4 mr-2" />
                  A* Search
                </Badge>
                <Badge variant="outline" className="px-4 py-2">
                  <Brain className="h-4 w-4 mr-2" />
                  AI Predictions
                </Badge>
              </div>
              
              <div className="flex flex-col sm:flex-row items-center justify-center gap-4">
                <Button asChild variant="hero" size="lg" className="min-w-[200px]">
                  <Link to="/find-routes">
                    Find Optimal Routes
                    <ArrowRight className="ml-2 h-5 w-5" />
                  </Link>
                </Button>
                
                <Button asChild variant="outline" size="lg" className="min-w-[200px]">
                  <Link to="/network-monitor">
                    Monitor Network
                    <Activity className="ml-2 h-5 w-5" />
                  </Link>
                </Button>
              </div>
            </motion.div>
          </div>
        </div>
      </section>

      {/* Algorithm Features */}
      <section className="py-20 bg-secondary/30">
        <div className="container mx-auto px-4 sm:px-6 lg:px-8">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6 }}
            viewport={{ once: true }}
            className="text-center mb-16"
          >
            <h2 className="text-3xl lg:text-4xl font-bold mb-4">
              Multi-Criteria{" "}
              <span className="bg-gradient-to-r from-primary to-accent bg-clip-text text-transparent">
                Optimization
              </span>
            </h2>
            <p className="text-muted-foreground text-lg max-w-2xl mx-auto">
              Choose your priority, and our algorithms will find the perfect route for your needs
            </p>
          </motion.div>

          <div className="grid md:grid-cols-3 gap-8">
            {algorithmFeatures.map((feature, index) => (
              <motion.div
                key={feature.title}
                initial={{ opacity: 0, y: 20 }}
                whileInView={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.6, delay: index * 0.1 }}
                viewport={{ once: true }}
              >
                <Card className="h-full shadow-lg hover:shadow-xl transition-shadow duration-300">
                  <CardHeader>
                    <feature.icon className="h-12 w-12 text-primary mb-4" />
                    <CardTitle className="text-xl">{feature.title}</CardTitle>
                  </CardHeader>
                  <CardContent>
                    <CardDescription className="text-base leading-relaxed">
                      {feature.description}
                    </CardDescription>
                  </CardContent>
                </Card>
              </motion.div>
            ))}
          </div>
        </div>
      </section>

      {/* Core Technologies */}
      <section className="py-20">
        <div className="container mx-auto px-4 sm:px-6 lg:px-8">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6 }}
            viewport={{ once: true }}
            className="text-center mb-16"
          >
            <h2 className="text-3xl lg:text-4xl font-bold mb-4">
              Advanced{" "}
              <span className="bg-gradient-to-r from-primary to-accent bg-clip-text text-transparent">
                Technologies
              </span>
            </h2>
            <p className="text-muted-foreground text-lg max-w-2xl mx-auto">
              Built on cutting-edge computer science algorithms and graph theory principles
            </p>
          </motion.div>

          <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-8">
            {features.map((feature, index) => (
              <motion.div
                key={feature.title}
                initial={{ opacity: 0, scale: 0.9 }}
                whileInView={{ opacity: 1, scale: 1 }}
                transition={{ duration: 0.6, delay: index * 0.1 }}
                viewport={{ once: true }}
              >
                <Card className="h-full shadow-lg hover:shadow-xl transition-all duration-300 hover:scale-105">
                  <CardHeader>
                    <feature.icon className={`h-12 w-12 ${feature.color} mb-4`} />
                    <CardTitle className="text-xl">{feature.title}</CardTitle>
                  </CardHeader>
                  <CardContent>
                    <CardDescription className="text-base leading-relaxed">
                      {feature.description}
                    </CardDescription>
                  </CardContent>
                </Card>
              </motion.div>
            ))}
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="py-20 bg-gradient-to-r from-primary/10 to-accent/10">
        <div className="container mx-auto px-4 sm:px-6 lg:px-8">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6 }}
            viewport={{ once: true }}
            className="text-center space-y-8"
          >
            <h2 className="text-3xl lg:text-4xl font-bold">
              Ready to Experience{" "}
              <span className="bg-gradient-to-r from-primary to-accent bg-clip-text text-transparent">
                Intelligent Flight Routing?
              </span>
            </h2>
            
            <p className="text-muted-foreground text-lg max-w-2xl mx-auto">
              Try our graph-based route optimization system and see how algorithms can revolutionize your travel planning
            </p>
            
            <div className="flex flex-col sm:flex-row items-center justify-center gap-4">
              <Button asChild variant="hero" size="lg" className="min-w-[200px]">
                <Link to="/find-routes">
                  <Plane className="mr-2 h-5 w-5" />
                  Start Optimizing
                </Link>
              </Button>
              
              <Button asChild variant="outline" size="lg" className="min-w-[200px]">
                <Link to="/predictions">
                  <Brain className="mr-2 h-5 w-5" />
                  View Predictions
                </Link>
              </Button>
            </div>
          </motion.div>
        </div>
      </section>
    </div>
  );
};

export default Home;
