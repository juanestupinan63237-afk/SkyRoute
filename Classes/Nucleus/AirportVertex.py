from Classes.Domain.Job import Job
from Classes.Domain.ActivityUser import Activity
class Airport:
    def __init__(self, iataId, name, city, country, isHub, accommodationCost, foodCost, activities : Activity, jobs : Job):
        self.iataId = iataId
        self.name = name
        self.city = city
        self.country = country
        self.isHub = isHub
        self.accommodationCost = accommodationCost
        self.foodCost = foodCost
        self.activities = activities
        self.jobs = jobs
        self.adjacencies = []

    def insertAdjacencies(self, adjacency):
        self.adjacencies.append(adjacency)