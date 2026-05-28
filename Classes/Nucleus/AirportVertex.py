from Classes.Domain.Job import Job
from Classes.Domain.ActivityUser import Activity
class Airport:
    def __init__(self, iataId, name, city, country, isHub, accommodationCost, foodCost):
        self.iataId = iataId
        self.name = name
        self.city = city
        self.country = country
        self.isHub = isHub
        self.accommodationCost = accommodationCost
        self.foodCost = foodCost
        self.adjacencies = []
        self.activities = []
        self.jobs = []

    def insertAdjacencies(self, adjacency):
        self.adjacencies.append(adjacency)

    def insertActivity(self, activity: Activity):
        self.activities.append(activity)

    def insertJob(self, job: Job):
        self.jobs.append(job)