from Classes.RouteEngine.Itinerary import Itinerary
from Classes.RouteEngine.RoutePlanner import RoutePlanner
class Traveler:
    def __init__(self, budget, timeAvailable , timeSinceLastMeal = 0 , timeSinceLastAccommodation = 0, history = None , activeUser = True):
        self.budget = budget
        self.timeAvailable = timeAvailable
        self.history = history
        self.timeSinceLastMeal = timeSinceLastMeal
        self.timeSinceLastAccommodation = timeSinceLastAccommodation
        self.activeUser = activeUser

    def CreateItineraryPerCriterion (self ,graph ,criterion , origin , destination , allowedAircraft = None):
        self.history = RoutePlanner.calculateRoute (graph , origin , destination , criterion , allowedAircraft)

    def pastTime (self , pastHours: int):
        if self.activeUser:
            self.timeSinceLastMeal += pastHours
            self.timeSinceLastAccommodation += pastHours