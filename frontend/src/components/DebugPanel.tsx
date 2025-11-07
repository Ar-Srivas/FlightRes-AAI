import { useState } from 'react';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { flightAPI } from '@/lib/api';
import { toast } from 'sonner';

const DebugPanel = () => {
  const [results, setResults] = useState<any>({});
  const [loading, setLoading] = useState<any>({});

  const testAPI = async (testName: string, testFunc: () => Promise<any>) => {
    setLoading({ ...loading, [testName]: true });
    try {
      const result = await testFunc();
      setResults({ ...results, [testName]: { success: true, data: result } });
      toast.success(`${testName} successful`);
    } catch (error) {
      console.error(`${testName} failed:`, error);
      setResults({ ...results, [testName]: { success: false, error: error.message } });
      toast.error(`${testName} failed: ${error.message}`);
    } finally {
      setLoading({ ...loading, [testName]: false });
    }
  };

  const tests = [
    {
      name: 'Health Check',
      func: () => flightAPI.healthCheck()
    },
    {
      name: 'Load Airports',
      func: () => flightAPI.getAirports()
    },
    {
      name: 'Network Stats',
      func: () => flightAPI.getNetworkStats()
    },
    {
      name: 'Find Route (DEL→BOM)',
      func: () => flightAPI.findRoutes({
        source: 'DEL',
        destination: 'BOM',
        algorithm: 'dijkstra'
      })
    },
    {
      name: 'Compare Algorithms',
      func: () => flightAPI.compareAlgorithms({
        source: 'BOM',
        destination: 'BLR',
        optimization: 'cost'
      })
    },
    {
      name: 'Route Map',
      func: async () => {
        const html = await flightAPI.getRouteVisualization({
          airports: ['DEL', 'BOM'],
          flights: ['AI101'],
          route_type: 'optimal'
        });
        return { htmlLength: html.length, preview: html.substring(0, 200) };
      }
    },
    {
      name: 'Network Map',
      func: async () => {
        const html = await flightAPI.getNetworkVisualization();
        return { htmlLength: html.length, preview: html.substring(0, 200) };
      }
    }
  ];

  return (
    <Card className="w-full max-w-4xl mx-auto">
      <CardHeader>
        <CardTitle>🐛 API Debug Panel</CardTitle>
      </CardHeader>
      <CardContent>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4 mb-6">
          {tests.map((test) => (
            <Button
              key={test.name}
              onClick={() => testAPI(test.name, test.func)}
              disabled={loading[test.name]}
              variant="outline"
              size="sm"
            >
              {loading[test.name] ? 'Testing...' : test.name}
            </Button>
          ))}
        </div>

        <div className="space-y-4">
          {Object.entries(results).map(([testName, result]: [string, any]) => (
            <div key={testName} className="border p-4 rounded">
              <div className="flex items-center gap-2 mb-2">
                <h4 className="font-semibold">{testName}</h4>
                <Badge variant={result.success ? "default" : "destructive"}>
                  {result.success ? "✅ Success" : "❌ Failed"}
                </Badge>
              </div>
              {result.success ? (
                <pre className="bg-green-50 p-2 rounded text-xs overflow-auto max-h-32">
                  {JSON.stringify(result.data, null, 2)}
                </pre>
              ) : (
                <pre className="bg-red-50 p-2 rounded text-xs text-red-700">
                  {result.error}
                </pre>
              )}
            </div>
          ))}
        </div>
      </CardContent>
    </Card>
  );
};

export default DebugPanel;