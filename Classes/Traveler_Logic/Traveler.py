from Classes.RouteEngine.Itinerary import Itinerary
from Classes.RouteEngine.RoutePlanner import RoutePlanner
from Classes.Domain.ActiveFly import ActiveFly
from Classes.Domain.TemporalActivity import TemporalActivity
from Classes.Domain.TemporalJob import TemporalJob
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
        self.restantActivities : list= restantActivities

    def CreateItineraryPerCriterion (self ,graph ,criterion , origin , destination , allowedAircraft = None):
        self.history = RoutePlanner().calculateRoute (graph , origin , destination , criterion , allowedAircraft)

    def pastTime (self , pastHours: int):
        if self.activeUser:
            if self.timeAvailable <= 0 or self.restantBudget <= 0:
                self.activeUser = False
                raise Exception ("This traveler had been inhabilited for the excess of time or cost...")
            self.timeSinceLastMeal += pastHours
            self.timeSinceLastAccommodation += pastHours
            self.timeAvailable -= pastHours
            if type (self.restantActivities[0]) == ActiveFly:
                self.restantActivities[0].DescountHours (pastHours)
                if self.restantActivities[0].hours <= 0:
                    self.actualAirportId = self.restantActivities[0].final
                    self.PopActualActivity ()
            elif type (self.restantActivities[0]) == TemporalActivity:
                self.restantActivities[0].DescountHours (pastHours)
                if self.restantActivities[0].hours <= 0:
                    self.PopActualActivity ()
            elif type (self.restantActivities[0]) == TemporalJob:
                self.restantActivities[0].DescountHours (pastHours)


    def DescountToFood (self , cost):
        if self.activeUser:
            if self.timeSinceLastMeal >= 8:
                self.timeSinceLastMeal = 0
                self.restantBudget -= cost

    def descountToAcommodation (self , cost):
        if self.activeUser:
            if self.timeSinceLastAccommodation >= 20:
                self.timeSinceLastAccommodation = 0 
                self.restantBudget -= cost

    def isActiveToWork (self):
        if self.activeUser:
            percent_of_budget = (self.budget / self.restantBudget) * 100
            if percent_of_budget <= 35:
                return True
        return False
    
    def PopActualActivity (self):
        self.restantActivities.remove (self.restantActivities[0])

    def AddActivitie (self , activity):
        if type (activity) == TemporalJob:
            if self.isActiveToWork ():
                self.restantBudget += activity.getTotalPay ()
                idx = 0
                for i, act in enumerate(self.restantActivities):
                    if not isinstance(act, ActiveFly):
                        idx += 1
                self.restantActivities.insert (idx , activity)
                self.activities.append (activity)
            else:
                raise Exception ("the traveler don´t have a permise to work in this moment...")
        elif type (activity) == TemporalActivity:
            self.restantBudget -= activity.price
        raise Exception ("the traveler don´t have a permise to work in this moment...")