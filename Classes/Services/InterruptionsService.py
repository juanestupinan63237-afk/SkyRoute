from Classes.Nucleus.Graph import Graph
from Classes.RouteEngine.RoutePlanner import RoutePlanner

class Interruptions:
    def __init__(self):
        self.planner = RoutePlanner()
    def planningBlock(self, graph : Graph, originAirportBlocked, destinationBlocked, destinationAirport, criterion):
        origin = None
        finalDestination = None
        for a in graph.airports:
            if originAirportBlocked == a.iataId:
                origin = a
            if destinationAirport == a.iataId:
                finalDestination = a
        if origin is None or finalDestination is None:
            return {"success": False, "message": "Airports not found in our database"}
        graph.blockRoute(originAirportBlocked, destinationBlocked)
        newRoute = self.planner.calculateRoute(graph, origin, finalDestination, criterion)
        return {"success": True, "message": "Route blocked and detour successfully calculated", "newRoute": newRoute}