from Classes.RouteEngine.Itinerary import Itinerary
from Classes.RouteEngine.RoutePlanner import RoutePlanner
from Classes.Domain.ActiveFly import ActiveFly
class Traveler:
    def __init__(self, budget,timeAvailable , actualAirportId , timeSinceLastMeal = 0 , timeSinceLastAccommodation = 0, history = None , activeUser = True , activities = [] , restantActivities=[]):
        self.budget = budget
        self.restantBudget = budget
        self.timeAvailable = timeAvailable
        self.history = history
        self.timeSinceLastMeal = timeSinceLastMeal
        self.timeSinceLastAccommodation = timeSinceLastAccommodation
        self.activeUser = activeUser
        self.actualAirportId = actualAirportId
        self.activities:list = activities
        self.restantActivities = restantActivities

    def CreateItineraryPerCriterion (self ,graph ,criterion , origin , destination , allowedAircraft = None):
        self.history = RoutePlanner().calculateRoute (graph , origin , destination , criterion , allowedAircraft)

    def pastTime (self , pastHours: int):
        if self.activeUser:
            self.timeSinceLastMeal += pastHours
            self.timeSinceLastAccommodation += pastHours
            self.timeAvailable -= pastHours
        if self.timeAvailable <= 0:
            self.activeUser = False

    def DescountToFood (self , cost):
        if self.activeUser:
            if self.timeSinceLastMeal >= 8:
                self.timeSinceLastMeal == 0
                self.restantBudget -= cost

    def descountToAcommodation (self , cost):
        if self.activeUser:
            if self.timeSinceLastAccommodation >= 20:
                self.timeSinceLastAccommodation = 0 
                self.restantBudget -= cost

    def isActiveToWork (self):
        if self.activeUser:
            percent_of_budget = (self.budget / self.restantBudget) * 100
            if percent_of_budget <= 25:
                return True
        return False
    
    def AddActivitie (self , activity):
        idx = 0
        for i in enumerate (self.restantActivities):
            if self.activities[i] != type (ActiveFly):
                idx += 1
        self.activities.insert (idx , activity)