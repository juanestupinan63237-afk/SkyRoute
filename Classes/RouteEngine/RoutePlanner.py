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

def dijkstra(graph: Graph, origin, destination, criterion):
    distances = {}
    for v in graph.airports:
        distances[v] = math.inf
    distances[origin] = 0
    fathers = {}
    count = 0
    queue = [(0, count, origin)]
    while queue:
        peso = heapq.heappop(queue)

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

