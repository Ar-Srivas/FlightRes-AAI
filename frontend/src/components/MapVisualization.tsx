import { useEffect, useRef, useState } from "react";
import mapboxgl from "mapbox-gl";
import "mapbox-gl/dist/mapbox-gl.css";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Alert, AlertDescription } from "@/components/ui/alert";
import { Info } from "lucide-react";

interface MapVisualizationProps {
  route: string[];
}

// Airport coordinates (mock data - replace with actual coordinates)
const airportCoordinates: Record<string, [number, number]> = {
  JFK: [-73.7781, 40.6413],
  LHR: [-0.4543, 51.4700],
  CDG: [2.5479, 49.0097],
  LAX: [-118.4085, 33.9416],
  NRT: [140.3929, 35.7720],
  DXB: [55.3644, 25.2532],
  SIN: [103.9915, 1.3644],
  ORD: [-87.9073, 41.9742],
  ATL: [-84.4277, 33.6407],
  SFO: [-122.3790, 37.6213],
};

const MapVisualization = ({ route }: MapVisualizationProps) => {
  const mapContainer = useRef<HTMLDivElement>(null);
  const map = useRef<mapboxgl.Map | null>(null);
  const [mapboxToken, setMapboxToken] = useState("");
  const [showTokenInput, setShowTokenInput] = useState(true);

  useEffect(() => {
    if (!mapContainer.current || !mapboxToken || map.current) return;

    try {
      mapboxgl.accessToken = mapboxToken;

      const mapInstance = new mapboxgl.Map({
        container: mapContainer.current,
        style: "mapbox://styles/mapbox/light-v11",
        center: [0, 30],
        zoom: 2,
        projection: { name: "globe" } as any,
      });

      mapInstance.addControl(new mapboxgl.NavigationControl(), "top-right");

      mapInstance.on("load", () => {
        // Add markers for each airport in the route
        const coordinates: [number, number][] = [];
        
        route.forEach((airport, index) => {
          const coord = airportCoordinates[airport];
          if (coord) {
            coordinates.push(coord);
            
            // Add marker
            const el = document.createElement("div");
            el.className = "marker";
            el.style.width = "30px";
            el.style.height = "30px";
            el.style.borderRadius = "50%";
            el.style.backgroundColor = index === 0 || index === route.length - 1 ? "#0EA5E9" : "#F59E0B";
            el.style.border = "3px solid white";
            el.style.boxShadow = "0 2px 8px rgba(0,0,0,0.3)";

            new mapboxgl.Marker(el)
              .setLngLat(coord)
              .setPopup(
                new mapboxgl.Popup({ offset: 25 }).setHTML(
                  `<div style="padding: 8px;">
                    <strong>${airport}</strong>
                    <p style="margin: 4px 0 0; font-size: 12px; color: #666;">
                      ${index === 0 ? "Origin" : index === route.length - 1 ? "Destination" : "Layover"}
                    </p>
                  </div>`
                )
              )
              .addTo(mapInstance);
          }
        });

        // Draw route lines
        if (coordinates.length > 1) {
          mapInstance.addSource("route", {
            type: "geojson",
            data: {
              type: "Feature",
              properties: {},
              geometry: {
                type: "LineString",
                coordinates: coordinates,
              },
            },
          });

          mapInstance.addLayer({
            id: "route",
            type: "line",
            source: "route",
            layout: {
              "line-join": "round",
              "line-cap": "round",
            },
            paint: {
              "line-color": "#0EA5E9",
              "line-width": 3,
              "line-dasharray": [2, 2],
            },
          });

          // Fit bounds to show entire route
          const bounds = new mapboxgl.LngLatBounds();
          coordinates.forEach((coord) => bounds.extend(coord));
          mapInstance.fitBounds(bounds, { padding: 80 });
        }
      });

      map.current = mapInstance;
      setShowTokenInput(false);

      return () => {
        mapInstance.remove();
      };
    } catch (error) {
      console.error("Error initializing map:", error);
    }
  }, [route, mapboxToken]);

  if (showTokenInput) {
    return (
      <div className="p-8 space-y-4">
        <Alert>
          <Info className="h-4 w-4" />
          <AlertDescription>
            To display the interactive map, please enter your Mapbox access token. You can get one for free at{" "}
            <a
              href="https://mapbox.com/"
              target="_blank"
              rel="noopener noreferrer"
              className="text-primary hover:underline font-medium"
            >
              mapbox.com
            </a>
          </AlertDescription>
        </Alert>
        
        <div className="space-y-2">
          <Label htmlFor="mapbox-token">Mapbox Access Token</Label>
          <div className="flex gap-2">
            <Input
              id="mapbox-token"
              type="password"
              placeholder="pk.eyJ1..."
              value={mapboxToken}
              onChange={(e) => setMapboxToken(e.target.value)}
              className="flex-1"
            />
            <button
              onClick={() => {
                if (mapboxToken.trim()) {
                  setShowTokenInput(false);
                }
              }}
              className="px-4 py-2 bg-primary text-white rounded-md hover:bg-primary/90 transition-colors"
            >
              Load Map
            </button>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="relative w-full h-[500px]">
      <div ref={mapContainer} className="absolute inset-0 rounded-b-lg" />
    </div>
  );
};

export default MapVisualization;
