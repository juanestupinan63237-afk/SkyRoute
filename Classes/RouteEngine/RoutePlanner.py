from Classes.Nucleus.Graph import Graph
from Classes.Nucleus.Route import Route
import math
import heapq

class RoutePlanner:
    def calculateRoute(self, graph : Graph, origin, destination, criterion, allowedAircraft = None, excludeSecondary = False):
        if origin not in graph.airports or destination not in graph.airports:
            raise ValueError("Another airport doesn't exist")
        if isinstance(criterion,str):
            processCriteria = [criterion]
        else:
            processCriteria = criterion
        validCriteria = ["distance", "time", "cost"]
        result = {}
        for c in processCriteria:
            if c.lower() not in validCriteria:
                raise ValueError(f"Invalid criterion {c}")
            route = self.dijkstra(graph, origin, destination, c, allowedAircraft, excludeSecondary)
            result[c.lower()] = route
        return result

    def dijkstra(self, graph: Graph, origin, destination, criterion, allowedAircraft, excludeSecondary):
        distances = {}
        for v in graph.airports:
            distances[v] = math.inf
        distances[origin] = 0
        fathers = {}
        count = 0
        queue = [(0, count, origin, 0, 0)]
        criterion = criterion.lower()
        if origin == destination:
            return {"route": [origin.iataId], "totalWeight": 0, "criterion": criterion}
        while queue:
            currentDistance, _, currentAirport, currentSubsidized, currentTotalDist = heapq.heappop(queue)
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
                if excludeSecondary and not neighbor.isHub:
                    continue
                newTotalDistance = currentTotalDist + route.distance
                if self.getWeight(route, "cost") == 0:
                    newSubsidized = currentSubsidized + route.distance
                else:
                    newSubsidized = currentSubsidized
                if newTotalDistance > 0 and (newSubsidized / newTotalDistance) > 0.20:
                    continue
                weight = self.getWeight(route, criterion)
                newDistance = weight + currentDistance
                if newDistance < distances[neighbor]:
                    count += 1
                    distances[neighbor] = newDistance
                    fathers[neighbor] = currentAirport
                    heapq.heappush(queue, (newDistance, count, neighbor, newSubsidized, newTotalDistance))
        if distances[destination] == math.inf:
            return {"path":[], "totalWeight":math.inf, "criterion": criterion}
        route = self.rebuildRoute(fathers, origin, destination)
        return {"route":route, "totalWeight":distances[destination], "criterion": criterion}

    def getWeight(self, route: Route, criterion):
        if criterion == "distance":
            return route.distance
        elif criterion == "time":
            return route.aircraft.calculateCostTime(route.time)
        else:
            return route.basePrice + route.aircraft.calculateCost(route.distance)

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

    def maximumOptimization(self, graph : Graph, airportOrigin, maximumBudget, limit):
        origin = None
        for a in graph.airports:
            if airportOrigin == a.iataId:
                origin = a
        if origin is None:
            return {"success": False, "message": "Airport not found in our database"}
        self.bestRoute = []
        visited = set()
        def dfs(currentAirport, currentBudget, currentRoute, usedAircraft):
            if currentBudget > maximumBudget:
                return
            if len(currentRoute) > len(self.bestRoute) and len(usedAircraft) == 3:
                self.bestRoute = list(currentRoute)
            visited.add(currentAirport)
            for route in currentAirport.adjacencies:
                if route.isBlocked:
                    continue
                neighbor = route.destination
                if neighbor not in visited:
                    temporalBudget = 0
                    if limit.lower() == "cost":
                        temporalBudget = (route.basePrice + route.aircraft.calculateCost(route.distance)) + (neighbor.accommodationCost + neighbor.foodCost)
                    elif limit.lower() == "time":
                        temporalBudget = route.aircraft.calculateCostTime(route.time)
                    newAircraft = set(usedAircraft)
                    newAircraft.add(route.aircraft.type)
                    dfs(neighbor, currentBudget + temporalBudget, currentRoute + [neighbor], newAircraft)
            visited.remove(currentAirport)
        dfs(origin, 0, [origin], set())
        return {
            "success": len(self.bestRoute) > 0,
            "bestRoute": [a.iataId for a in self.bestRoute]
        }