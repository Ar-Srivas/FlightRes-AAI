import { useEffect, useRef, useState } from "react";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Map, RefreshCw, Network, Route as RouteIcon } from "lucide-react";
import { flightAPI, Route } from "@/lib/api";
import { toast } from "sonner";

interface MapVisualizationProps {
  route?: string[];
  routes?: Route[];
  flights?: string[];
  routeType?: string;
  showNetworkOverview?: boolean;
  showComparison?: boolean;
}

const MapVisualization = ({ 
  route = [], 
  routes = [],
  flights = [],
  routeType = "optimal",
  showNetworkOverview = false,
  showComparison = false
}: MapVisualizationProps) => {
  const iframeRef = useRef<HTMLIFrameElement>(null);
  const [loading, setLoading] = useState(false);
  const [mapHtml, setMapHtml] = useState<string>("");
  const [error, setError] = useState<string>("");

  const loadMapVisualization = async () => {
    if ((!route.length && !showNetworkOverview && !showComparison) || loading) return;

    setLoading(true);
    setError("");

    try {
      let htmlContent = "";

      if (showNetworkOverview) {
        // Load network overview map
        console.log('[MapViz] Loading network overview map...');
        htmlContent = await flightAPI.getNetworkVisualization();
      } else if (showComparison && routes.length > 0) {
        // Load routes comparison map
        console.log('[MapViz] Loading routes comparison map for', routes.length, 'routes...');
        console.log('[MapViz] Routes data:', routes);
        htmlContent = await flightAPI.getRoutesComparison(routes);
      } else if (route.length > 0) {
        // Load single route map
        console.log('[MapViz] Loading route map for:', route);
        console.log('[MapViz] Flight data:', flights);
        console.log('[MapViz] Route type:', routeType);
        htmlContent = await flightAPI.getRouteVisualization({
          airports: route,
          flights: flights,
          route_type: routeType
        });
      }

      if (htmlContent && htmlContent.trim()) {
        console.log('[MapViz] Map HTML loaded successfully, size:', htmlContent.length);
        console.log('[MapViz] HTML preview:', htmlContent.substring(0, 200) + '...');
        setMapHtml(htmlContent);
        setError("");
      } else {
        throw new Error('Empty HTML content received');
      }
    } catch (err) {
      console.error("[MapViz] Error loading map:", err);
      const errorMessage = err instanceof Error ? err.message : "Failed to load map visualization";
      setError(errorMessage);
      toast.error(`Map Error: ${errorMessage}`);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadMapVisualization();
  }, [route, routes, flights, routeType, showNetworkOverview, showComparison]);

  // Create blob URL for the map HTML
  useEffect(() => {
    if (mapHtml) {
      // Create a blob with the HTML content
      const blob = new Blob([mapHtml], { type: 'text/html' });
      const url = URL.createObjectURL(blob);
      
      // Store the URL for the iframe
      const iframe = iframeRef.current;
      if (iframe) {
        iframe.src = url;
      }
      
      // Cleanup blob URL on unmount
      return () => {
        URL.revokeObjectURL(url);
      };
    }
  }, [mapHtml]);

  const handleRefresh = () => {
    loadMapVisualization();
  };

  if (error) {
    return (
      <Card className="w-full">
        <CardHeader>
          <CardTitle className="flex items-center gap-2 text-red-600">
            <Map className="h-5 w-5" />
            Map Visualization Error
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="text-center py-8">
            <p className="text-muted-foreground mb-4">{error}</p>
            <Button onClick={handleRefresh} variant="outline">
              <RefreshCw className="mr-2 h-4 w-4" />
              Retry
            </Button>
          </div>
        </CardContent>
      </Card>
    );
  }

  if (loading) {
    return (
      <Card className="w-full">
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Map className="h-5 w-5" />
            {showNetworkOverview ? "Network Overview" : showComparison ? "Routes Comparison" : "Route Visualization"}
          </CardTitle>
          <CardDescription>
            {showNetworkOverview 
              ? "Loading flight network overview..."
              : showComparison 
              ? "Loading routes comparison..."
              : "Loading route visualization..."}
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="flex items-center justify-center h-[500px]">
            <div className="text-center">
              <RefreshCw className="h-8 w-8 animate-spin text-primary mx-auto mb-4" />
              <p className="text-muted-foreground">Generating map with Folium...</p>
            </div>
          </div>
        </CardContent>
      </Card>
    );
  }

  if (!mapHtml) {
    return (
      <Card className="w-full">
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Map className="h-5 w-5" />
            Route Visualization
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="text-center py-12">
            <Map className="h-12 w-12 text-muted-foreground mx-auto mb-4" />
            <p className="text-muted-foreground mb-4">
              {route.length === 0 ? "No route data to visualize" : "Click refresh to load the map"}
            </p>
            {route.length > 0 && (
              <Button onClick={handleRefresh}>
                <Map className="mr-2 h-4 w-4" />
                Load Map
              </Button>
            )}
          </div>
        </CardContent>
      </Card>
    );
  }

  return (
    <Card className="w-full">
      <CardHeader>
        <div className="flex items-center justify-between">
          <div>
            <CardTitle className="flex items-center gap-2">
              {showNetworkOverview ? (
                <>
                  <Network className="h-5 w-5" />
                  Flight Network Overview
                </>
              ) : showComparison ? (
                <>
                  <RouteIcon className="h-5 w-5" />
                  Routes Comparison
                </>
              ) : (
                <>
                  <Map className="h-5 w-5" />
                  Route Visualization
                </>
              )}
            </CardTitle>
            <CardDescription className="flex items-center gap-2 mt-2">
              {showNetworkOverview ? (
                "Interactive map showing all airports and flight connections"
              ) : showComparison ? (
                `Comparing ${routes.length} different routes`
              ) : (
                <>
                  Route: {route.join(" → ")}
                  {routeType && (
                    <Badge variant="secondary" className="ml-2">
                      {routeType.charAt(0).toUpperCase() + routeType.slice(1)} Optimized
                    </Badge>
                  )}
                </>
              )}
            </CardDescription>
          </div>
          <Button variant="outline" size="sm" onClick={handleRefresh}>
            <RefreshCw className="h-4 w-4" />
          </Button>
        </div>
      </CardHeader>
      <CardContent className="p-0">
        <div className="relative w-full h-[600px] rounded-b-lg overflow-hidden border">
          {mapHtml ? (
            <div className="w-full h-full">
              <iframe
                ref={iframeRef}
                className="w-full h-full border-0"
                title="Flight Route Visualization"
                sandbox="allow-scripts allow-same-origin allow-modals allow-forms allow-popups"
                loading="lazy"
                style={{
                  backgroundColor: '#f8f9fa',
                  border: 'none',
                  display: 'block'
                }}
                onLoad={() => {
                  console.log('[MapViz] Map iframe loaded successfully');
                }}
                onError={(e) => {
                  console.error('[MapViz] Map iframe error:', e);
                  setError('Failed to load map iframe');
                }}
              />
            </div>
          ) : (
            <div className="w-full h-full bg-gray-100 flex items-center justify-center">
              <div className="text-center text-gray-500">
                <Map className="h-12 w-12 mx-auto mb-4" />
                <p>No map data available</p>
                <Button 
                  variant="outline" 
                  size="sm" 
                  onClick={handleRefresh}
                  className="mt-2"
                >
                  Load Map
                </Button>
              </div>
            </div>
          )}
          
          {/* Loading overlay */}
          {loading && (
            <div className="absolute inset-0 bg-white/80 flex items-center justify-center z-10">
              <div className="text-center">
                <RefreshCw className="h-8 w-8 animate-spin text-primary mx-auto mb-4" />
                <p className="text-muted-foreground">Loading map...</p>
              </div>
            </div>
          )}
        </div>
      </CardContent>
    </Card>
  );
};

export default MapVisualization;
