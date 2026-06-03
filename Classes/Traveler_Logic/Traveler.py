from Classes.RouteEngine.Itinerary import Itinerary
from Classes.RouteEngine.RoutePlanner import RoutePlanner
from Classes.Domain.ActiveFly import ActiveFly
from Classes.Domain.TemporalActivity import TemporalActivity
from Classes.Domain.TemporalJob import TemporalJob
from Classes.Nucleus.Graph import Graph
from Classes.Domain.ActivityUser import Activity
from Classes.Nucleus.Route import Route
class Traveler:
    def __init__(self, budget,timeAvailable , actualAirportId , timeSinceLastMeal = 0 , timeSinceLastAccommodation = 0, history = None , activeUser = True , activities = [] , restantActivities=[]):
        self.budget = budget
        self.restantBudget = budget
        self.timeAvailable = timeAvailable
        self.history : Itinerary = history
        self.timeSinceLastMeal = timeSinceLastMeal
        self.timeSinceLastAccommodation = timeSinceLastAccommodation
        self.activeUser = activeUser
        self.actualAirportId = actualAirportId
        self.activities:list = activities
        self.restantActivities : list= restantActivities

    def CreateItineraryPerCriterion (self ,graph ,criterion , origin , destination , allowedAircraft = None):
        self.history = RoutePlanner().calculateRoute (graph , origin , destination , criterion , allowedAircraft)

    def AddAllItineraryTravels (self , graph: Graph):
        initial = self.actualAirportId
        final = self.history.visitedDestinations [0]
        for i in range (0 , len(self.history.visitedDestinations)):
            route = graph.getRoute (initial , final)
            if self.restantBudget <= route.basePrice:
                self.activeUser = False
                raise Exception ("This traveler don´t have many money to buy this ticket...")
            self.restantActivities.append (ActiveFly (initial , final , route.time , route.time))
            self.restantBudget -= route.basePrice


    def pastTime (self , pastHours: int , graph: Graph):
        if self.activeUser:
            if self.timeAvailable <= 0 or self.restantBudget <= 0:
                self.activeUser = False
                raise Exception ("This traveler had been inhabilited for the excess of time or cost...")
            self.timeSinceLastMeal += pastHours
            self.timeSinceLastAccommodation += pastHours
            self.timeAvailable -= pastHours
            if len(self.restantActivities) == 0:
                return 
            if type (self.restantActivities[0]) == ActiveFly:
                self.restantActivities[0].DescountHours (pastHours)
                if self.restantActivities[0].restantHours <= 0:
                    self.actualAirportId = self.restantActivities[0].final
                    self.PopActualActivity ()
                    activities_of_add = graph.getAirportPerCode (self.actualAirportId).activities
                    for i in self.activities_of_add:
                        if type (i) == Activity:
                            if i.isImportant:
                                temp = TemporalActivity (i.id , i.duration , i.name, i.duration , i.price )
                                self.activities.append (temp)
                                self.restantActivities.append (temp)
            elif type (self.restantActivities[0]) == TemporalActivity:
                self.restantActivities[0].DescountHours (pastHours)
                if self.restantActivities[0].hours <= 0:
                    self.PopActualActivity ()
            elif type (self.restantActivities[0]) == TemporalJob:
                self.restantActivities[0].DescountHours (pastHours)
                if self.restantActivities[0].time <= 0:
                    self.PopActualActivity ()
            self.DescountToFood (graph.getAirportPerCode(self.actualAirportId).foodCost)
            self.descountToAcommodation (graph.getAirportPerCode(self.actualAirportId).accommodationCost)


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
            percent_of_budget = (self.restantBudget/ self.budget) * 100
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
            idx = 0
            for i, act in enumerate(self.restantActivities):
                if not isinstance(act, ActiveFly):
                    idx += 1
            self.restantActivities.insert (idx , activity)
            self.activities.append (activity)