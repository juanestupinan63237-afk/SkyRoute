import json
from Classes.Nucleus.Graph import Graph
from Classes.Traveler_Logic import Traveler
from Classes.Nucleus.AirportVertex import Airport

class SimulationEngine:
    def __init__(self, travelerJsonPath, graph: Graph):
        self.jsonPath = travelerJsonPath
        self.graph = graph

    def loadTraveler(self, travelerId):
        with open(self.jsonPath, "r", encoding="utf-8") as file:
            data = json.load(file)
        travelerData = data.get(str(travelerId))
        if not travelerData:
            raise Exception("Viajero no encontrado en el archivo JSON")
        traveler = Traveler(
            id=travelerData["id"],
            name=travelerData["name"],
            budget=travelerData["budget"],
            timeAvailable=travelerData["timeAvailable"],
            actualAirportId=travelerData["actualAirportId"],
            timeSinceLastMeal=travelerData.get("timeSinceLastMeal", 0),
            timeSinceLastAccommodation=travelerData.get("timeSinceLastAccommodation", 0),
            activeUser=travelerData.get("activeUser", True)
        )
        traveler.restantBudget = travelerData.get("restantBudget", travelerData["budget"])
        traveler.visitedAirports = travelerData.get("visitedAirports", [])
        traveler.currentFlight = travelerData.get("currentFlight", None)
        return traveler

    def saveTravelerData(self, traveler: Traveler):
        with open(self.jsonPath, 'r', encoding='utf-8') as file:
            data = json.load(file)
        data[str(traveler.id)] = {
            "id": traveler.id,
            "name": traveler.name,
            "budget": traveler.budget,
            "restantBudget": traveler.restantBudget,
            "timeAvailable": traveler.timeAvailable,
            "actualAirportId": traveler.actualAirportId,
            "timeSinceLastMeal": traveler.timeSinceLastMeal,
            "timeSinceLastAccommodation": traveler.timeSinceLastAccommodation,
            "activeUser": traveler.activeUser,
            "visitedAirports": traveler.visitedAirports,
            "currentFlight": traveler.currentFlight # Persistimos el estado del vuelo en tránsito
        }
        with open(self.jsonPath, "w", encoding="utf-8") as file:
            json.dump(data, file, indent=4, ensure_ascii=False)

    def getAirportOptions(self, travelerId):
        traveler = self.loadTraveler(travelerId)
        airport: Airport = self.graph.getAirportPerCode(traveler.actualAirportId)
        return {
            "travelerStatus": {
                "currentAirport": traveler.actualAirportId,
                "budgetLeft": traveler.restantBudget,
                "timeLeft": traveler.timeAvailable,
                "canWork": traveler.isActiveToWork(),
                "inTransit": traveler.currentFlight is not None
            },
            "flights": [
                {
                    "destination": r.destination.iataId,
                    "distanceKm": r.distance,
                    "aircraftOptions": [
                        {"type": "CommercialAirplane", "cost": r.distance * 0.18, "timeMin": r.distance * 0.7},
                        {"type": "RegionalPlane", "cost": r.distance * 0.25, "timeMin": r.distance * 1.1},
                        {"type": "Propeller", "cost": r.distance * 0.12, "timeMin": r.distance * 2.5}
                    ]
                }
                for r in airport.adjacencies if not r.isBlocked
            ],
            "activities": [
                {"id": act.id, "name": act.name, "duration": act.duration, "price": act.price}
                for act in airport.activities
            ],
            "jobs": [
                {"id": j.jobId, "name": j.nameJob, "rate": j.hourlyRate, "maxHours": j.maxHours}
                for j in airport.jobs
            ]
        }

    def processAirportActivity(self, travelerId, activityId, isJob=False, jobHours=0):
        traveler = self.loadTraveler(travelerId)
        if traveler.currentFlight:
            raise Exception("No puedes hacer actividades mientras estás en vuelo")
        airport: Airport = self.graph.getAirportPerCode(traveler.actualAirportId)
        if isJob:
            job = None
            for j in airport.jobs:
                if j.jobId == activityId:
                    job = j
                    break
            if not job:
                raise Exception("Trabajo no encontrado")
            traveler.AddActivitie(job, jobHours)
            traveler.pastTime(jobHours, self.graph)
        else:
            activity = None
            for a in airport.activities:
                if a.id == activityId:
                    activity = a
                    break
            if not activity:
                raise Exception("Actividad no encontrada")
            traveler.AddActivitie(activity, activity.duration)
            traveler.pastTime(activity.duration, self.graph)
        self.saveTravelerData(traveler)
        return {"success": True, "currentBudget": traveler.restantBudget, "currentTime": traveler.timeAvailable}

    def process_flight(self, travelerId, destinationIata, aircraftType, criterion="cost"):
        traveler = self.loadTraveler(travelerId)
        if traveler.currentFlight:
            raise Exception("El viajero ya está en tránsito.")

        originIata = traveler.actualAirportId
        origin = self.graph.getAirportPerCode(originIata)
        destination = self.graph.getAirportPerCode(destinationIata)
        traveler.CreateItineraryPerCriterion(self.graph, criterion, origin, destination)
        beforeFlights = len(traveler.restantActivities)
        traveler.AddAllItineraryTravels(self.graph)
        newFlights = traveler.restantActivities[beforeFlights:]
        totalHours = 0
        for flight in newFlights:
            route = self.graph.getRoute(flight.origin, flight.destination)
            if aircraftType == "CommercialAirplane":
                totalHours += (route.distance * 0.7) / 60
            elif aircraftType == "RegionalPlane":
                totalHours += (route.distance * 1.1) / 60
            elif aircraftType == "Propeller":
                totalHours += (route.distance * 2.5) / 60
            else:
                totalHours += flight.duration
        traveler.currentFlight = {
            "origin": originIata,
            "destination": destinationIata,
            "hoursTotal": totalHours,
            "hoursProgress": 0.0,
            "aircraftType": aircraftType,
            "criterion": criterion
        }
        self.saveTravelerData(traveler)
        return {"success": True, "message": "Vuelo iniciado. Avance con ticks de simulación.", "inTransit": True}

    def tickSimulation(self, travelerId, timeStepHours=0.5):
        traveler = self.loadTraveler(travelerId)
        if traveler.currentFlight:
            flight = traveler.currentFlight
            flight["hoursProgress"] += timeStepHours
            traveler.pastTime(timeStepHours, self.graph)
            if flight["hoursProgress"] >= flight["hoursTotal"]:
                traveler.actualAirportId = flight["destination"]
                traveler.currentFlight = None
        else:
            traveler.pastTime(timeStepHours, self.graph)
        self.saveTravelerData(traveler)
        return {
            "currentAirport": traveler.actualAirportId,
            "progress": traveler.currentFlight["hoursProgress"] / traveler.currentFlight["hoursTotal"] if traveler.currentFlight else 1.0,
            "inTransit": traveler.currentFlight is not None,
            "budgetLeft": traveler.restantBudget,
            "timeLeft": traveler.timeAvailable
        }

    def interruptCurrentFlight(self, travelerId, originIata, destinationIata):
        self.graph.blockRoute(originIata, destinationIata)
        traveler = self.loadTraveler(travelerId)
        if traveler.currentFlight:
            flight = traveler.currentFlight
            if flight["origin"] == originIata and flight["destination"] == destinationIata:
                finalDestination = flight["destination"]
                criterion = flight["criterion"]
                aircraft = flight["aircraftType"]
                traveler.currentFlight = None
                traveler.restantActivities = []
                origin_vertex = self.graph.getAirportPerCode(traveler.actualAirportId)
                dest_vertex = self.graph.getAirportPerCode(finalDestination)
                traveler.CreateItineraryPerCriterion(self.graph, criterion, origin_vertex, dest_vertex)
                beforeFlights = len(traveler.restantActivities)
                traveler.AddAllItineraryTravels(self.graph)
                newFlights = traveler.restantActivities[beforeFlights:]
                if newFlights:
                    totalHours = 0
                    for f in newFlights:
                        route = self.graph.getRoute(f.origin, f.destination)
                        if aircraft == "CommercialAirplane": totalHours += (route.distance * 0.7) / 60
                        elif aircraft == "RegionalPlane": totalHours += (route.distance * 1.1) / 60
                        else: totalHours += (route.distance * 2.5) / 60
                    traveler.currentFlight = {
                        "origin": traveler.actualAirportId,
                        "destination": finalDestination,
                        "hoursTotal": totalHours,
                        "hoursProgress": 0.0,
                        "aircraftType": aircraft,
                        "criterion": criterion
                    }
        self.saveTravelerData(traveler)
        return {
            "success": True,
            "message": "Ruta bloqueada. Simulación recalculada con éxito.",
            "currentAirport": traveler.actualAirportId,
            "inTransit": traveler.currentFlight is not None
        }