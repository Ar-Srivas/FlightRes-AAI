from flask import Flask
from routers.flights import flights_blueprint
from routers.bookings import bookings_blueprint

app = Flask(__name__)


app.register_blueprint(flights_blueprint, url_prefix='/flights')
app.register_blueprint(bookings_blueprint, url_prefix='/bookings')



@app.route('/')
def home():
    return "Hello, World!"

@app.route('/status')
def status():
    return {"status": "OK"}, 200


if __name__ == '__main__':
    app.run(debug=True)
