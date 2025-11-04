from flask import Blueprint, jsonify, request


flights_blueprint = Blueprint('flights', __name__)

@flights_blueprint.route('/optimize', methods=['GET'])
def optimize_route():
    return jsonify({"message": "Optimize route called"}), 200


