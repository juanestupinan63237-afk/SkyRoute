from flask import Flask, request, jsonify , render_template
from Classes.Nucleus.Graph import Graph
from Classes.RouteEngine.RoutePlanner import RoutePlanner
from Classes.Services.InterruptionsService import Interruptions
from Classes.Traveler_Logic.Traveler import Traveler

app = Flask(__name__)

graph = Graph()
planner = RoutePlanner()
interruptionService = Interruptions()
travelers:list[Traveler] = []
temporalTravels = []
travelers.append (Traveler (0 , "ewhf" , 10000 , 1000 , None) )

@app.route("/")
def home():
    return render_template ("index.html")

@app.route ("/traveler/descountTime")
async def DescountTime ():
    data = request.get_json ()
    time = data.get("time")
    for traveler in travelers:
        temp_airport = graph.getAirportPerCode (traveler.actualAirportId)
        traveler.pastTime (time)
        traveler.DescountToFood (temp_airport.foodCost)
        traveler.descountToAcommodation (temp_airport.accommodationCost)

@app.route('/api/calculateRoute', methods=['POST'])
async def apiCalculateRoute():
    data = request.get_json()
    origin_iata = data.get('origin')
    destination_iata = data.get('destination')
    criterion = data.get('criterion')

    origin_node = None
    destination_node = None
    for a in graph.airports:
        if a.iataId == origin_iata:
            origin_node = a
        if a.iataId == destination_iata:
            destination_node = a
    if origin_node is None or destination_node is None:
        return jsonify({"success": False, "message": "Airport not found in our database"}), 404
    result = planner.calculateRoute(graph, origin_node, destination_node, criterion)
    return jsonify({
        "success": True,
        "route": result
    })

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

@app.route('/api/optimize', methods=['POST'])
async def apiOptimize():
    data = request.get_json()
    airport_origin = data.get('origin')
    maximum_budget = float(data.get('budget'))
    limit = data.get('limit')
    result = planner.maximumOptimization(graph, airport_origin, maximum_budget, limit)
    return jsonify(result)

@app.route ("/api/traveler" , methods= ["POST"])
async def CreateTraveler ():
    data = request.get_json
    travelers.append (Traveler (data.get("Budget") , data.get("timeAvailable") , data.get("actualAirportId")))
    return jsonify ({"request" : "ok, the traveler had benn created in the system..."})

@app.route ("/traveler/get" , methods = ["POST"])
async def getTraveler ():
    data = request.get_json ()
    temp = None
    for i in travelers: 
        if data.get ("id") == i.id:
            temp = i
    return jsonify ({"name" : temp.name,
                     "id" : id})


if __name__ == '__main__':
    app.run(debug=True)