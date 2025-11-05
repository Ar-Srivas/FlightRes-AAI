import { motion } from "framer-motion";
import { Plane, Calendar, MapPin, DollarSign } from "lucide-react";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";

const Bookings = () => {
  // Mock booking data
  const bookings = [
    {
      id: "BK-001",
      route: "JFK → LHR",
      date: "2024-02-15",
      passengers: 1,
      price: 720,
      status: "Confirmed",
    },
    {
      id: "BK-002",
      route: "LAX → NRT",
      date: "2024-03-20",
      passengers: 2,
      price: 1560,
      status: "Confirmed",
    },
  ];

  return (
    <div className="min-h-screen py-12 bg-gradient-to-b from-background via-secondary/20 to-background">
      <div className="container mx-auto px-4 sm:px-6 lg:px-8">
        <motion.div
          initial={{ opacity: 0, y: -20 }}
          animate={{ opacity: 1, y: 0 }}
          className="text-center mb-12"
        >
          <h1 className="text-4xl font-bold mb-4">
            My{" "}
            <span className="bg-gradient-to-r from-primary to-accent bg-clip-text text-transparent">
              Bookings
            </span>
          </h1>
          <p className="text-muted-foreground text-lg">Manage and view your flight reservations</p>
        </motion.div>

        {bookings.length === 0 ? (
          <motion.div
            initial={{ opacity: 0, scale: 0.9 }}
            animate={{ opacity: 1, scale: 1 }}
            className="text-center py-20"
          >
            <Plane className="h-20 w-20 text-muted-foreground mx-auto mb-6" />
            <h2 className="text-2xl font-semibold mb-4">No Bookings Yet</h2>
            <p className="text-muted-foreground mb-8">
              Start exploring routes and book your next flight
            </p>
          </motion.div>
        ) : (
          <div className="grid gap-6 max-w-4xl mx-auto">
            {bookings.map((booking, index) => (
              <motion.div
                key={booking.id}
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: index * 0.1 }}
              >
                <Card className="shadow-lg hover:shadow-xl transition-shadow duration-300">
                  <CardHeader>
                    <div className="flex items-start justify-between">
                      <div>
                        <CardTitle className="flex items-center gap-3 text-xl">
                          <Plane className="h-6 w-6 text-primary" />
                          {booking.route}
                        </CardTitle>
                        <CardDescription className="mt-2">
                          Booking ID: {booking.id}
                        </CardDescription>
                      </div>
                      <Badge variant="secondary" className="bg-green-100 text-green-800">
                        {booking.status}
                      </Badge>
                    </div>
                  </CardHeader>
                  <CardContent>
                    <div className="grid md:grid-cols-3 gap-6">
                      <div className="flex items-center gap-3">
                        <Calendar className="h-5 w-5 text-primary" />
                        <div>
                          <div className="text-sm text-muted-foreground">Departure Date</div>
                          <div className="font-semibold">
                            {new Date(booking.date).toLocaleDateString("en-US", {
                              month: "short",
                              day: "numeric",
                              year: "numeric",
                            })}
                          </div>
                        </div>
                      </div>

                      <div className="flex items-center gap-3">
                        <MapPin className="h-5 w-5 text-primary" />
                        <div>
                          <div className="text-sm text-muted-foreground">Passengers</div>
                          <div className="font-semibold">{booking.passengers} Adult(s)</div>
                        </div>
                      </div>

                      <div className="flex items-center gap-3">
                        <DollarSign className="h-5 w-5 text-primary" />
                        <div>
                          <div className="text-sm text-muted-foreground">Total Price</div>
                          <div className="font-semibold text-primary text-lg">
                            ${booking.price}
                          </div>
                        </div>
                      </div>
                    </div>
                  </CardContent>
                </Card>
              </motion.div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
};

export default Bookings;
