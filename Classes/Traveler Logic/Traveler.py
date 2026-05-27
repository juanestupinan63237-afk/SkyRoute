from Classes.RouteEngine.Itinerary import Itinerary
class Traveler:
    def __init__(self, budget, timeAvailable, history, timeSinceLastMeal, timeSinceLastAccommodation):
        self.budget = budget
        self.timeAvailable = timeAvailable
        self.history = history
        self.timeSinceLastMeal = timeSinceLastMeal
        self.timeSinceLastAccommodation = timeSinceLastAccommodation