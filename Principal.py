from flask import Flask, request, jsonify, render_template
from Classes.Services.ParserJSON import ParserJSON
from Classes.Planning.Simulation import SimulationEngine
from Classes.Services.InterruptionsService import Interruptions
from Classes.Services.report_service import ReportService
from Classes.RouteEngine.RoutePlanner import RoutePlanner

app = Flask(__name__)

parser  = ParserJSON()
graph   = parser.parse("Data/airports.json")
engine  = SimulationEngine("Data/travelers.json", graph)
planner = RoutePlanner()
report  = ReportService()

# ─────────────────────────────────────────────
# Helpers
# ─────────────────────────────────────────────
def ok(data=None, msg="OK", code=200):
    return jsonify({"success": True, "message": msg, "data": data}), code

def err(msg, code=400):
    return jsonify({"success": False, "message": str(msg), "data": None}), code


@app.route("/")
def index():
    """Página principal — interfaz SkyRoute Planner."""
    return render_template("index.html")

@app.route("/graph", methods=["GET"])
def get_graph():
    """Devuelve todos los nodos y aristas del grafo."""
    nodes = [
        {
            "id":      a.iataId,
            "name":    a.name,
            "city":    a.city,
            "country": a.country,
            "isHub":   a.isHub,
            "accommodationCost": a.accommodationCost,
            "foodCost": a.foodCost,
            "activities": [
                {"name": x.name, "id": x.id, "duration": x.duration,
                 "price": x.price, "isImportant": x.isImportant}
                for x in a.activities
            ],
            "jobs": [
                {"id": j.jobId, "name": j.nameJob,
                 "rate": j.hourlyRate, "maxHours": j.maxHours}
                for j in a.jobs
            ]
        }
        for a in graph.airports
    ]
    edges = [
        {
            "origin":      r.origin.iataId,
            "destination": r.destination.iataId,
            "distance":    r.distance,
            "time":        r.time,
            "basePrice":   r.basePrice,
            "aircraft":    r.aircraft.type,
            "minStay":     r.minStay,
            "isBlocked":   r.isBlocked
        }
        for r in graph.routes
    ]
    return ok({"nodes": nodes, "edges": edges})

@app.route("/graph/airport/<iata>", methods=["GET"])
def get_airport(iata):
    """Detalle completo de un aeropuerto."""
    try:
        a = graph.getAirportPerCode(iata.upper())
        return ok({
            "iataId":  a.iataId,  "name": a.name,
            "city":    a.city,    "country": a.country,
            "isHub":   a.isHub,
            "accommodationCost": a.accommodationCost,
            "foodCost": a.foodCost,
            "activities": [{"name": x.name, "id": x.id, "duration": x.duration, "price": x.price, "isImportant": x.isImportant} for x in a.activities],
            "jobs":       [{"id": j.jobId, "name": j.nameJob, "rate": j.hourlyRate, "maxHours": j.maxHours} for j in a.jobs],
            "adjacencies":[{"destination": r.destination.iataId, "distance": r.distance, "aircraft": r.aircraft.type, "basePrice": r.basePrice, "isBlocked": r.isBlocked} for r in a.adjacencies]
        })
    except Exception as e:
        return err(e, 404)

@app.route("/route/calculate", methods=["POST"])
def calculate_route():
    """
    Dijkstra entre origen y destino.
    Body: { origin, destination, criterion, allowedAircraft?, excludeSecondary? }
    """
    try:
        b = request.get_json(force=True)
        origin      = graph.getAirportPerCode(b["origin"].upper())
        destination = graph.getAirportPerCode(b["destination"].upper())
        criterion   = b.get("criterion", "cost")
        allowed     = b.get("allowedAircraft", None)
        excl        = b.get("excludeSecondary", False)

        itinerary = planner.calculateRoute(graph, origin, destination, criterion, allowed, excl)
        if not itinerary or not itinerary.visitedDestinations:
            return err("No se encontró ruta entre esos aeropuertos.", 404)

        stops    = itinerary.visitedDestinations
        segments = []
        for i in range(len(stops) - 1):
            try:
                r = graph.getRoute(stops[i], stops[i + 1])
                segments.append({
                    "from": stops[i], "to": stops[i + 1],
                    "distance": r.distance, "time": r.time,
                    "aircraft": r.aircraft.type,
                    "cost": round(r.basePrice + r.aircraft.calculateCost(r.distance), 2)
                })
            except Exception:
                segments.append({"from": stops[i], "to": stops[i + 1]})

        return ok({
            "criterion":  itinerary.criterion,
            "totalCost":  round(itinerary.totalCost, 2),
            "stops":      stops,
            "segments":   segments,
            "totalStops": len(stops)
        })
    except Exception as e:
        return err(e)

@app.route("/route/maximize", methods=["POST"])
def maximize_route():
    """
    DFS que maximiza destinos visitados usando los 3 tipos de transporte.
    Body: { origin, budget, limit }
    """
    try:
        b      = request.get_json(force=True)
        origin = b["origin"].upper()
        budget = float(b["budget"])
        limit  = b.get("limit", "cost")
        best   = planner.maximumOptimization(graph, origin, budget, limit)
        if not best:
            return err("No se encontró ruta dentro del presupuesto.", 404)
        return ok({"route": best, "totalStops": len(best), "limit": limit, "budget": budget})
    except Exception as e:
        return err(e)

@app.route("/traveler", methods=["POST"])
def create_traveler():
    """
    Body: { id, name, budget, timeAvailable, startAirport }
    """
    try:
        b = request.get_json(force=True)
        graph.getAirportPerCode(b["startAirport"].upper())   # valida existencia
        engine.createTraveler(str(b["id"]), b["name"], float(b["budget"]), float(b["timeAvailable"]), b["startAirport"].upper())
        return ok({"id": str(b["id"]), "name": b["name"], "startAirport": b["startAirport"].upper()}, "Viajero creado", 201)
    except Exception as e:
        return err(e)


@app.route("/traveler/<tid>", methods=["GET"])
def get_traveler_status(tid):
    """Estado actual del viajero y opciones disponibles en su aeropuerto."""
    try:
        return ok(engine.getAirportOptions(tid))
    except Exception as e:
        return err(e, 404)

@app.route("/traveler/<tid>/fly", methods=["POST"])
def start_flight(tid):
    """
    Body: { destination, aircraftType, criterion }
    """
    try:
        b = request.get_json(force=True)
        return ok(engine.startFlight(tid, b["destination"].upper(), b.get("aircraftType", "Commercial Airplane"), b.get("criterion", "cost")))
    except Exception as e:
        return err(e)

@app.route("/traveler/<tid>/tick", methods=["POST"])
def tick(tid):
    """
    Body (opcional): { timeStepHours: 0.5 }
    """
    try:
        b    = request.get_json(force=True) or {}
        step = float(b.get("timeStepHours", 0.5))
        return ok(engine.tickSimulation(tid, step))
    except Exception as e:
        return err(e)

@app.route("/traveler/<tid>/activity", methods=["POST"])
def do_activity(tid):
    """Body: { activityId }"""
    try:
        b = request.get_json(force=True)
        return ok(engine.doActivity(tid, b["activityId"]))
    except Exception as e:
        return err(e)

@app.route("/traveler/<tid>/job", methods=["POST"])
def do_job(tid):
    """Body: { jobId, hours }"""
    try:
        b = request.get_json(force=True)
        return ok(engine.doJob(tid, b["jobId"], float(b["hours"])))
    except Exception as e:
        return err(e)

@app.route("/route/block", methods=["POST"])
def block_route():
    """
    Body: { travelerId, origin, destination }
    Bloquea la ruta y recalcula el itinerario si el viajero está en tránsito.
    """
    try:
        b    = request.get_json(force=True)
        orig = b["origin"].upper()
        dest = b["destination"].upper()
        tid  = str(b.get("travelerId", "NONE"))
        return ok(engine.interruptFlight(tid, orig, dest))
    except Exception as e:
        return err(e)

@app.route("/route/unblock", methods=["POST"])
def unblock_route():
    """Body: { origin, destination }"""
    try:
        b = request.get_json(force=True)
        graph.unblockRoute(b["origin"].upper(), b["destination"].upper())
        return ok({"unblocked": f"{b['origin'].upper()} -> {b['destination'].upper()}"})
    except Exception as e:
        return err(e)

@app.route("/route/blocked", methods=["GET"])
def get_blocked():
    """Lista todas las rutas bloqueadas actualmente."""
    blocked = [
        {"origin": r.origin.iataId, "destination": r.destination.iataId, "distance": r.distance}
        for r in graph.routes if r.isBlocked
    ]
    return ok({"blocked": blocked, "total": len(blocked)})

@app.route("/traveler/<tid>/report", methods=["GET"])
def get_report(tid):
    """Reporte completo del viaje: destinos, vuelos, actividades, trabajos, totales."""
    try:
        traveler = engine.loadTraveler(tid)
        return ok(report.build_report(traveler, graph))
    except Exception as e:
        return err(e, 404)


@app.route("/health", methods=["GET"])
def health():
    return ok({
        "airports": len(graph.airports),
        "routes":   len(graph.routes),
        "status":   "SkyRoute Planner running"
    }, "OK")


if __name__ == "__main__":
    app.run()