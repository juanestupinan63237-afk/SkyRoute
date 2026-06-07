from flask import Flask, request, jsonify
from flask_cors import CORS
from Classes.Nucleus.Graph import Graph
from Classes.RouteEngine.RoutePlanner import RoutePlanner
from Classes.Services.InterruptionsService import Interruptions

app = Flask(__name__)
CORS(app)

graph = Graph()
planner = RoutePlanner()
interruptionService = Interruptions()

@app.route("/")
def home():
    return "The Flask server is running correctly"

@app.route('/api/calculateRoute', methods=['POST'])
async def apiCalculateRoute():
    data = request.get_json()
    origin_str = data.get('origin').toUpperCase().trim()
    destination_str = data.get('destination').toUpperCase().trim()
    criterion = data.get('criterion')
    origin_obj = None
    destination_obj = None

    for airport in graph.airports:
        if airport.iataId == origin_str:
            origin_obj = airport
        if airport.iataId == destination_str:
            destination_obj = airport
    if origin_obj is None or destination_obj is None:
        return jsonify({
            "success": False,
            "message": f"Código IATA no válido. Buscado: {origin_str} a {destination_str}"
        }), 404

    try:
        dijkstraResult = planner.calculateRoute(
            graph,
            origin_obj,
            destination_obj,
            criterion,
            allowedAircraft=None,
            excludeSecondary=False
        )
        return jsonify({
            "success": True,
            "route": dijkstraResult
        })

    except Exception as e:
        return jsonify({
            "success": False,
            "message": str(e)
        }), 500

@app.route('/api/BlockedRoute', methods=['POST'])
async def apiBlockedRoute():
    data = request.get_json()
    originBlocked = data.get('originBlocked')
    destinationBlocked = data.get('destinationBlocked')
    finalDestination = data.get('finalDestination')
    criterion = data.get('criterion')
    result = interruptionService.planningBlock(
        graph,
        originBlocked,
        destinationBlocked,
        finalDestination,
        criterion
    )
    return jsonify(result)

if __name__ == '__main__':
    app.run(debug=True, port=5000)