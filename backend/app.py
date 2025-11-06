from flask import Flask
from flask_cors import CORS

from routers.flights import flights_blueprint
from routers.bookings import bookings_blueprint
from routers.routes import routes_blueprint

app = Flask(__name__)
CORS(app)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
from models import db
db.init_app(app)

# Register routes
app.register_blueprint(flights_blueprint)
app.register_blueprint(bookings_blueprint)
app.register_blueprint(routes_blueprint)

@app.route('/')
def home():
    return {"message": "FlightRes API running with Graph-based Route Optimization"}

@app.route('/health')
def health():
    return {"status": "healthy"}

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    
    # Force run on port 5001
    port = 5001
    print(f"Starting server on port {port}")
    try:
        app.run(debug=True, port=port, host='0.0.0.0')
    except OSError as e:
        if "Address already in use" in str(e):
            print(f"❌ Port {port} is already in use!")
            print("Please check if another instance is running or kill the process using this port:")
            print(f"   lsof -ti:{port} | xargs kill -9")
            exit(1)
        else:
            raise e
