from flask import Flask
from flask_cors import CORS

from routers.flights import flights_blueprint
from routers.bookings import bookings_blueprint

app = Flask(__name__)
CORS(app)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
from models import db
db.init_app(app)

# Register routes
app.register_blueprint(flights_blueprint)
app.register_blueprint(bookings_blueprint)

@app.route('/')
def home():
    return {"message": "FlightRes API running"}

@app.route('/health')
def health():
    return {"status": "healthy"}


if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
