from Classes.Nucleus.AirportVertex import Airport
class Graph:
    def __init__(self):
        self.adjacencies = {}

    def insertAirports(self, airport : Airport):
        if airport not in self.adjacencies:
            self.adjacencies[airport] = []

    def insertRout(self, origin, destination, distance, aircraft, basePrice, minStay):
        self.adjacencies[origin].append({
            "origin": origin,
            "destination": destination,
            "distance": distance,
            "aircraft": aircraft,
            "basePrice": basePrice,
            "minStay": minStay
        })

    def getNeighbors(self, vertex):
        return self.adjacencies.get(vertex, [])