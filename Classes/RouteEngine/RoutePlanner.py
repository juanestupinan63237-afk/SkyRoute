from Nucleus.Graph import Graph
from Nucleus.Route import Route
from Domain.Aircraft import CommercialAirplane
from Domain.Aircraft import RegionalPlane
from Domain.Aircraft import Propeller
import math
import heapq

class RoutePlanner:
    def calculateRoute(self, graph : Graph, origin, destination, criterion, allowedAircraft= None, excludeHubs=False):
        if origin not in graph.airports or destination not in graph.airports:
            raise ValueError("Another airport doesn't exist")
        validCriteria = ["distance", "time", "cost"]
        if criterion.lower() not in validCriteria:
            raise ValueError("Invalid criterion")
        return self.dijkstra(graph, origin, destination, criterion, allowedAircraft, excludeHubs)

    def dijkstra(self, graph: Graph, origin, destination, criterion, allowedAircraft, excludeHubs):
        distances = {}
        for v in graph.airports:
            distances[v] = math.inf
        distances[origin] = 0
        fathers = {}
        count = 0
        queue = [(0, count, origin)]
        criterion = criterion.lower()
        if origin == destination:
            return {"path": [origin.iataId], "totalWeight": 0, "criterion": criterion}
        while queue:
            currentDistance, _, currentAirport = heapq.heappop(queue)
            if currentDistance > distances[currentAirport]:
                continue
            if currentAirport == destination:
                break
            for route in currentAirport.adjacencies:
                if allowedAircraft is not None:
                    if route.aircraft.type not in allowedAircraft:
                        continue
                if route.isBlocked:
                    continue
                neighbor = route.destination
                if excludeHubs and neighbor.isHub:
                    continue
                weight = self.getWeight(route, criterion)
                newDistance = weight + currentDistance
                if newDistance < distances[neighbor]:
                    count += 1
                    distances[neighbor] = newDistance
                    fathers[neighbor] = currentAirport
                    heapq.heappush(queue, (newDistance, count, neighbor))
        if distances[destination] == math.inf:
            return {"path":[], "totalWeight":math.inf, "criterion": criterion}
        route = self.rebuildRoute(fathers, origin, destination)
        return {"path":route, "totalWeight":distances[destination], "criterion": criterion}

    def getWeight(self, route : Route, criterion):
        if criterion == "distance":
            return route.distance
        elif criterion == "time":
            return route.time
        else:
            return (route.basePrice + (route.distance * route.aircraft.costPerKm))

    def rebuildRoute(self, fathers, origin, destination):
        route = []
        current = destination
        while current != origin:
            route.append(current.iataId)
            current = fathers.get(current)
            if current is None:
                return None
        route.append(origin.iataId)
        route.reverse()
        return route