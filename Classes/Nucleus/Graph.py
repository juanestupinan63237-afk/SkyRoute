from Classes.Nucleus.AirportVertex import Airport
from Classes.Nucleus.Route import Route
class Graph:
    def __init__(self):
        self.airports = []
        self.routes = []

    def insertAirports(self, airport : Airport):
        if airport not in self.airports:
            self.airports.append(airport)

    def insertRoute(self, origin, destination, time, distance, aircraft, basePrice, minStay):
        route = Route(origin, destination, time, aircraft, distance, basePrice, minStay)
        self.routes.append(route)
        origin.insertAdjacencies(route)

    def validateExistence(self, iataId):
        isIata = False
        for a in self.airports:
            if iataId == a.iataId:
                isIata = True
        return isIata

    def getNeighbors(self, iataId):
        airport = None
        for a in self.airports:
            if iataId == a.iataId:
                airport = a
        if airport is not None:
            return airport.adjacencies
        return airport

    def blockRoute(self, originIata, destinationIata):
        for s in self.routes:
            if s.origin.iataId == originIata and s.destination.iataId == destinationIata:
                s.isBlocked = True