import { useState } from "react";
import { motion } from "framer-motion";
import { useNavigate } from "react-router-dom";
import { Search, MapPin, Calendar } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { toast } from "sonner";

const FindRoutes = () => {
  const navigate = useNavigate();
  const [formData, setFormData] = useState({
    source: "",
    destination: "",
    routeType: "cheapest",
    date: "",
  });

  const handleSearch = (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!formData.source || !formData.destination) {
      toast.error("Please enter both source and destination airports");
      return;
    }

    if (formData.source === formData.destination) {
      toast.error("Source and destination cannot be the same");
      return;
    }

    // Navigate to results page with search params
    navigate(`/results?source=${formData.source}&destination=${formData.destination}&type=${formData.routeType}`);
  };

  const popularRoutes = [
    { from: "New York (JFK)", to: "London (LHR)" },
    { from: "Los Angeles (LAX)", to: "Tokyo (NRT)" },
    { from: "Dubai (DXB)", to: "Singapore (SIN)" },
    { from: "Paris (CDG)", to: "New York (JFK)" },
  ];

  return (
    <div className="min-h-screen py-12 bg-gradient-to-b from-background via-secondary/20 to-background">
      <div className="container mx-auto px-4 sm:px-6 lg:px-8">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5 }}
          className="max-w-3xl mx-auto"
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
              Enter your travel details and let our AI find the best flight routes for you
            </p>
          </div>

          {/* Search Card */}
          <Card className="shadow-xl border-border/50">
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Search className="h-5 w-5 text-primary" />
                Search Flights
              </CardTitle>
              <CardDescription>
                Compare routes based on price, speed, and reliability
              </CardDescription>
            </CardHeader>
            <CardContent>
              <form onSubmit={handleSearch} className="space-y-6">
                {/* Source & Destination */}
                <div className="grid md:grid-cols-2 gap-4">
                  <div className="space-y-2">
                    <Label htmlFor="source" className="flex items-center gap-2">
                      <MapPin className="h-4 w-4 text-primary" />
                      From (Airport Code)
                    </Label>
                    <Input
                      id="source"
                      placeholder="e.g., JFK, LAX, LHR"
                      value={formData.source}
                      onChange={(e) => setFormData({ ...formData, source: e.target.value.toUpperCase() })}
                      className="uppercase"
                      maxLength={3}
                    />
                  </div>

                  <div className="space-y-2">
                    <Label htmlFor="destination" className="flex items-center gap-2">
                      <MapPin className="h-4 w-4 text-accent" />
                      To (Airport Code)
                    </Label>
                    <Input
                      id="destination"
                      placeholder="e.g., JFK, LAX, LHR"
                      value={formData.destination}
                      onChange={(e) => setFormData({ ...formData, destination: e.target.value.toUpperCase() })}
                      className="uppercase"
                      maxLength={3}
                    />
                  </div>
                </div>

                {/* Route Type & Date */}
                <div className="grid md:grid-cols-2 gap-4">
                  <div className="space-y-2">
                    <Label htmlFor="routeType">Optimization Priority</Label>
                    <Select
                      value={formData.routeType}
                      onValueChange={(value) => setFormData({ ...formData, routeType: value })}
                    >
                      <SelectTrigger id="routeType">
                        <SelectValue />
                      </SelectTrigger>
                      <SelectContent className="bg-popover">
                        <SelectItem value="cheapest">💰 Cheapest Route</SelectItem>
                        <SelectItem value="fastest">⚡ Fastest Route</SelectItem>
                        <SelectItem value="reliable">🛡️ Most Reliable</SelectItem>
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
                <Button type="submit" variant="hero" size="lg" className="w-full">
                  <Search className="mr-2 h-5 w-5" />
                  Search Routes
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
            <h3 className="text-xl font-semibold mb-4 text-center">Popular Routes</h3>
            <div className="grid sm:grid-cols-2 gap-3">
              {popularRoutes.map((route, index) => (
                <button
                  key={index}
                  onClick={() => {
                    const sourceCode = route.from.match(/\(([^)]+)\)/)?.[1] || "";
                    const destCode = route.to.match(/\(([^)]+)\)/)?.[1] || "";
                    setFormData({ ...formData, source: sourceCode, destination: destCode });
                  }}
                  className="p-4 bg-card border border-border rounded-lg hover:border-primary/50 hover:shadow-md transition-all duration-300 text-left group"
                >
                  <div className="flex items-center justify-between">
                    <div className="flex-1">
                      <div className="text-sm font-medium text-foreground group-hover:text-primary transition-colors">
                        {route.from}
                      </div>
                      <div className="text-xs text-muted-foreground mt-1">to {route.to}</div>
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
