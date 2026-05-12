from Nucleus.Graph import Graph
from Domain.Aircraft import CommercialAirplane
from Domain.Aircraft import RegionalPlane
from Domain.Aircraft import Propeller
import math
import heapq

AIRCRAFT_FACTORY = {
    "Commercial Airplane": CommercialAirplane(),
    "Regional Plane": RegionalPlane(),
    "Propeller": Propeller()
}

def dijkstra(graph: Graph, origin, destination, criterion="cost", budget=None, maxTime=None):
    distances = {}
    for v in graph.adjacencies:
        distances[v] = math.inf
    distances[origin] = 0

    queue = [(0, origin, 0)]
    fathers = {}

    while queue:
        currentValue, currentVertex, accumulatedTime = heapq.heappop(queue)

        if currentValue > distances[currentVertex]:
            continue

        if currentVertex == destination:
            break

        for neighbor in graph.getNeighbors(currentVertex):
            neighborVertex = neighbor["destination"]
            distance = neighbor["distance"]
            basePrice = neighbor.get("basePrice", 0)

            for aircraft in neighbor["aircraft"]:
                plane = AIRCRAFT_FACTORY.get(aircraft)
                if not plane:
                    continue

                sectionCost = plane.calculateCost(distance) + basePrice
                sectionTime = plane.calculateTime(distance)

                if criterion == "cost":
                    sectionValue = sectionCost
                elif criterion == "time":
                    sectionValue = sectionTime
                else:
                    sectionValue = distance

                newValue = currentValue + sectionValue
                newTime = accumulatedTime + sectionTime

                if budget is not None and (criterion == "cost" and newValue > budget):
                    continue
                if maxTime is not None and newTime > (maxTime * 60):
                    continue

                if newValue < distances[neighborVertex]:
                    distances[neighborVertex] = newValue
                    fathers[neighborVertex] = currentVertex
                    heapq.heappush(queue, (newValue, neighborVertex, newTime))

    if distances[destination] == math.inf:
        return None, math.inf

    route = rebuildRoute(fathers, origin, destination)
    return route, distances[destination]


def rebuildRoute(fathers, origin, destination):
    route = []
    current = destination

    while current != origin:
        route.append(current)
        current = fathers.get(current)

        if current is None:
            return None

    route.append(origin)
    route.reverse()
    return route


def maximizeDestinations(graph: Graph, origin, maxTime, budget):
    visited = {}
    for v in graph.adjacencies:
        visited[v] = False
    visited[origin] = True
    currentVertex = origin
    totalCost = 0
    totalTime = 0
    route = [origin]

    while True:
        neighbors = graph.getNeighbors(currentVertex)
        bestNeighbor = None
        minSectionCost = math.inf
        bestTime = 0

        for n in neighbors:
            destination = n["destination"]
            distance = n["distance"]
            basePrice = n.get("basePrice", 0)

            if visited[destination]:
                continue

            for aircraft in n["aircraft"]:
                plane = AIRCRAFT_FACTORY.get(aircraft)
                if not plane:
                    continue

                cost = plane.calculateCost(distance) + basePrice
                time = plane.calculateTime(distance)

                if cost < minSectionCost:
                    minSectionCost = cost
                    bestNeighbor = destination
                    bestTime = time

        if bestNeighbor is None:
            break

        if totalCost + minSectionCost <= budget and totalTime + bestTime <= (maxTime * 60):
            totalCost += minSectionCost
            totalTime += bestTime
            visited[bestNeighbor] = True
            route.append(bestNeighbor)
            currentVertex = bestNeighbor
        else:
            break

    return route, totalCost, totalTime