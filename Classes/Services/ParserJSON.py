import json
from Classes.Nucleus.AirportVertex import Airport
from Classes.Nucleus.Graph import Graph
from Classes.Domain.ActivityUser import Activity
from Classes.Domain.Job import Job
from Classes.Domain.Aircraft import CommercialAirplane, Propeller, RegionalPlane

class ParserJSON:
    def parse(self, filePath):
        graph = Graph()
        with open(filePath, 'r', encoding='utf-8') as file:
            data = json.load(file)

        for d in data["airport"]:
            iataId = d["iataId"]
            name = d["name"]
            city = d["city"]
            country = d["country"]
            isHub = d["isHub"]
            accommodationCost = d["accommodationCost"]
            foodCost = d["foodCost"]

            airport = Airport(iataId, name, city, country, isHub, accommodationCost, foodCost)

            for activ in d.get("activity", []):
                nameAct = activ["name"]
                typeAct = activ["type"]
                duration = activ["duration"]
                price = activ["price"]
                activity = Activity(nameAct, typeAct, duration, price)
                airport.insertActivity(activity)

            for j in d.get("job", []):
                jobId = j["jobId"]
                nameJob = j["nameJob"]
                hourlyRate = j["hourlyRate"]
                maxHours = j["maxHours"]
                job = Job(jobId, nameJob, hourlyRate, maxHours)
                airport.insertJob(job)

            graph.insertAirports(airport)

        for route in data["route"]:
            temporalOrigin = route["origin"]
            temporalDestination = route["destination"]
            origin = None
            destination = None

            for a in graph.airports:
                if a.iataId == temporalOrigin:
                    origin = a
                if a.iataId == temporalDestination:
                    destination = a
            time = route["time"]
            distance = route["distance"]
            basePrice = route["basePrice"]
            minStay = route["minStay"]
            aircraftStr = route["aircraft"]
            aircraftObj = None

            if aircraftStr == "Commercial Airplane":
                aircraftObj = CommercialAirplane()
            elif aircraftStr == "Regional Plane":
                aircraftObj = RegionalPlane()
            elif aircraftStr == "Propeller":
                aircraftObj = Propeller()

            if origin is not None and destination is not None and aircraftObj is not None:
                graph.insertRoute(origin, destination, route["time"], route["distance"], aircraftObj, route["basePrice"], route["minStay"])
        return graph