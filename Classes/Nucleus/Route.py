class Route:
    def __init__(self, origin, destination, time, aircraft, distance, basePrice, minStay):
        self.origin = origin
        self.destination = destination
        self.time = time
        self.aircraft = aircraft
        self.distance = distance
        self.basePrice = basePrice
        self.minStay = minStay
        self.isBlocked = False