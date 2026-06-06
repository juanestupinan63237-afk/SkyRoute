from Classes.RouteEngine.Itinerary import Itinerary
from Classes.RouteEngine.RoutePlanner import RoutePlanner
from Classes.Domain.ActiveFly import ActiveFly
from Classes.Domain.TemporalActivity import TemporalActivity
from Classes.Domain.TemporalJob import TemporalJob
from Classes.Nucleus.Graph import Graph
from Classes.Domain.ActivityUser import Activity
from Classes.Domain.Job import Job
class Traveler:
    def __init__(self, id , name ,budget,timeAvailable , actualAirportId , timeSinceLastMeal = 0 , timeSinceLastAccommodation = 0, history = None , activeUser = True):
        self.budget = budget
        self.name = name
        self.id = id
        self.restantBudget = budget
        self.timeAvailable = timeAvailable
        self.history : Itinerary = history
        self.timeSinceLastMeal = timeSinceLastMeal
        self.timeSinceLastAccommodation = timeSinceLastAccommodation
        self.activeUser = activeUser
        self.actualAirportId = actualAirportId
        self.activities:list = []
        self.restantActivities : list= []
        self.visitedAirports = []

    def CreateItineraryPerCriterion (self ,graph ,criterion , origin , destination , allowedAircraft = None):
        self.history = RoutePlanner().calculateRoute (graph , origin , destination , criterion , allowedAircraft)

    def AddAllItineraryTravels (self , graph: Graph):
        initial = self.actualAirportId
        final = self.history.visitedDestinations [0]
        for i in range (0 , len(self.history.visitedDestinations)-1):
            route = graph.getRoute (initial , final)
            if self.restantBudget <= (route.basePrice + route.aircraft.calculateCost(route.distance)):
                self.activeUser = False
                raise Exception ("This traveler don´t have many money to buy this ticket...")
            self.restantActivities.append (ActiveFly (initial , final , route.time , route.time))
            self.restantBudget -= route.basePrice + route.aircraft.calculateCost(route.distance)
            initial = route.destination.iataId
            final = self.history.visitedDestinations [i+1]


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
                    for i in activities_of_add:
                        if type (i) == Activity:
                            if i.isImportant:
                                temp = TemporalActivity (i.id , i.duration , i.name, i.duration , i.price )
                                self.activities.append (temp)
                                self.restantActivities.insert(0, temp)
                    self.visitedAirports.append (self.actualAirportId)
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

    def AddActivitie (self , activity , apliccation_hours):
        if type(activity) == Job:
            if self.isActiveToWork():
                if activity.maxHours < apliccation_hours:
                    raise Exception(f"Max hours for this job is {activity.maxHours}")
                new_activity = TemporalJob(apliccation_hours, activity.hourlyRate, activity.jobId)
                self.restantBudget += new_activity.getTotalPay()
                idx = len(self.restantActivities)
                for i, act in enumerate(self.restantActivities):
                    if isinstance(act, ActiveFly):
                        idx = i
                        break
                self.restantActivities.insert(idx, new_activity)  # fuera del for
                self.activities.append(new_activity)              # fuera del for
            else:                                                  # else del if isActiveToWork
                raise Exception("the traveler doesn't have permission to work right now...")
        elif type (activity) == Activity:
            new_activity = TemporalActivity (activity.id , activity.duration , activity.name , activity.duration , activity.price)
            self.restantBudget -= new_activity.price
            idx = len(self.restantActivities)  
            for i, act in enumerate(self.restantActivities):
                if isinstance(act, ActiveFly):
                    idx = i  
                    break
            self.restantActivities.insert (idx , new_activity)
            self.activities.append (new_activity)