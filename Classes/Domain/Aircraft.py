class Aircraft:
    def __init__(self, type, costKm, timeKm):
        self.type = type
        self.costKm = costKm
        self.timeKm = timeKm

    def calculateCost(self, distance):
        return self.costKm * distance

    def calculateCostTime(self, time):
        return self.timeKm * time
class Propeller(Aircraft):
    def __init__(self):
        super().__init__("Propeller", 0.12, 2.5)

class RegionalPlane(Aircraft):
    def __init__(self):
        super().__init__("Regional Plane", 0.25, 1.1)

class CommercialAirplane(Aircraft):
    def __init__(self):
        super().__init__("Commercial Airplane", 0.18, 0.7)