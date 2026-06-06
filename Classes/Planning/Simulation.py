import json
import os
from Classes.Nucleus.Graph import Graph
from Classes.Traveler_Logic.Traveler import Traveler   # FIX: importar la clase, no el módulo
from Classes.Nucleus.AirportVertex import Airport
from Classes.Domain.ActiveFly import ActiveFly

class SimulationEngine:
    def __init__(self, travelerJsonPath, graph: Graph):
        self.jsonPath = travelerJsonPath
        self.graph = graph

    # ─────────────────────────────────────────
    # Persistencia
    # ─────────────────────────────────────────
    def _ensureFile(self):
        if not os.path.exists(self.jsonPath):
            with open(self.jsonPath, "w", encoding="utf-8") as f:
                json.dump({}, f)

    def loadTraveler(self, travelerId):
        self._ensureFile()
        with open(self.jsonPath, "r", encoding="utf-8") as file:
            data = json.load(file)
        travelerData = data.get(str(travelerId))
        if not travelerData:
            raise Exception(f"Viajero '{travelerId}' no encontrado")
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
        self._ensureFile()
        with open(self.jsonPath, "r", encoding="utf-8") as file:
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
            "currentFlight": traveler.currentFlight
        }
        with open(self.jsonPath, "w", encoding="utf-8") as file:
            json.dump(data, file, indent=4, ensure_ascii=False)

    # ─────────────────────────────────────────
    # FIX: createTraveler — faltaba este método
    # ─────────────────────────────────────────
    def createTraveler(self, travelerId, name, budget, timeAvailable, startAirportId):
        traveler = Traveler(
            id=travelerId,
            name=name,
            budget=budget,
            timeAvailable=timeAvailable,
            actualAirportId=startAirportId
        )
        self.saveTravelerData(traveler)
        return traveler

    # ─────────────────────────────────────────
    # FIX: getAirportOptions — ahora incluye todos los campos que necesita el frontend
    # ─────────────────────────────────────────
    def getAirportOptions(self, travelerId):
        traveler = self.loadTraveler(travelerId)
        airport: Airport = self.graph.getAirportPerCode(traveler.actualAirportId)
        return {
            "travelerStatus": {
                "id": traveler.id,
                "name": traveler.name,                          # FIX: faltaba
                "currentAirport": traveler.actualAirportId,
                "budgetLeft": round(traveler.restantBudget, 2),
                "initialBudget": round(traveler.budget, 2),     # FIX: faltaba
                "timeLeft": round(traveler.timeAvailable, 2),
                "canWork": traveler.isActiveToWork(),
                "inTransit": traveler.currentFlight is not None,
                "isActive": traveler.activeUser,
                "visitedAirports": traveler.visitedAirports     # FIX: faltaba
            },
            "currentAirportInfo": {
                "iataId": airport.iataId,
                "name": airport.name,
                "city": airport.city,
                "country": airport.country,
                "isHub": airport.isHub,
                "accommodationCost": airport.accommodationCost,
                "foodCost": airport.foodCost
            },
            # FIX: ahora incluye destinationName, destinationCity e isBlocked
            "flights": [
                {
                    "destination": r.destination.iataId,
                    "destinationName": r.destination.name,      # FIX: faltaba
                    "destinationCity": r.destination.city,      # FIX: faltaba
                    "distanceKm": r.distance,
                    "isBlocked": r.isBlocked,                   # FIX: faltaba
                    "aircraftOptions": [
                        {"type": "Commercial Airplane", "cost": round(r.basePrice + r.distance * 0.18, 2), "timeMin": round(r.distance * 0.7, 1)},
                        {"type": "Regional Plane",      "cost": round(r.basePrice + r.distance * 0.25, 2), "timeMin": round(r.distance * 1.1, 1)},
                        {"type": "Propeller",           "cost": round(r.basePrice + r.distance * 0.12, 2), "timeMin": round(r.distance * 2.5, 1)}
                    ]
                }
                for r in airport.adjacencies
            ],
            "activities": [
                {"id": act.id, "name": act.name, "duration": act.duration,
                 "price": act.price, "isImportant": act.isImportant}
                for act in airport.activities
            ],
            "jobs": [
                {"id": j.jobId, "name": j.nameJob, "rate": j.hourlyRate, "maxHours": j.maxHours}
                for j in airport.jobs
            ] if traveler.isActiveToWork() else []
        }

    # ─────────────────────────────────────────
    # FIX: startFlight — renombrado desde process_flight
    # ─────────────────────────────────────────
    def startFlight(self, travelerId, destinationIata, aircraftType, criterion="cost"):
        traveler = self.loadTraveler(travelerId)
        if traveler.currentFlight:
            raise Exception("El viajero ya está en tránsito.")
        originIata  = traveler.actualAirportId
        origin      = self.graph.getAirportPerCode(originIata)
        destination = self.graph.getAirportPerCode(destinationIata)
        traveler.CreateItineraryPerCriterion(self.graph, criterion, origin, destination)
        traveler.restantActivities = []
        traveler.AddAllItineraryTravels(self.graph)
        totalHours = 0
        for flight in traveler.restantActivities:
            if isinstance(flight, ActiveFly):
                route = self.graph.getRoute(flight.origin, flight.final)   # FIX: .final no .destination
                if aircraftType == "Commercial Airplane":
                    totalHours += (route.distance * 0.7) / 60
                elif aircraftType == "Regional Plane":
                    totalHours += (route.distance * 1.1) / 60
                else:
                    totalHours += (route.distance * 2.5) / 60
        traveler.currentFlight = {
            "origin": originIata,
            "destination": destinationIata,
            "hoursTotal": round(totalHours, 2),
            "hoursProgress": 0.0,
            "aircraftType": aircraftType,
            "criterion": criterion,
            "route": traveler.history.visitedDestinations if traveler.history else []
        }
        self.saveTravelerData(traveler)
        return {
            "success": True,
            "message": f"Vuelo iniciado hacia {destinationIata}",
            "flightDetails": traveler.currentFlight
        }

    # ─────────────────────────────────────────
    # tickSimulation — sin cambios de nombre, solo fixes internos
    # ─────────────────────────────────────────
    def tickSimulation(self, travelerId, timeStepHours=0.5):
        traveler = self.loadTraveler(travelerId)
        if traveler.currentFlight:
            flight = traveler.currentFlight
            flight["hoursProgress"] = round(flight["hoursProgress"] + timeStepHours, 2)
            traveler.timeAvailable  -= timeStepHours
            traveler.timeSinceLastMeal += timeStepHours
            traveler.timeSinceLastAccommodation += timeStepHours
            if flight["hoursProgress"] >= flight["hoursTotal"]:
                traveler.actualAirportId = flight["destination"]
                if traveler.actualAirportId not in traveler.visitedAirports:
                    traveler.visitedAirports.append(traveler.actualAirportId)
                traveler.currentFlight = None
        else:
            traveler.pastTime(timeStepHours, self.graph)
        self.saveTravelerData(traveler)
        return {
            "currentAirport": traveler.actualAirportId,
            "inTransit":   traveler.currentFlight is not None,
            "progress":    round(traveler.currentFlight["hoursProgress"] / traveler.currentFlight["hoursTotal"], 3) if traveler.currentFlight else 1.0,
            "hoursProgress": traveler.currentFlight["hoursProgress"] if traveler.currentFlight else 0,
            "hoursTotal":    traveler.currentFlight["hoursTotal"]    if traveler.currentFlight else 0,
            "budgetLeft":  round(traveler.restantBudget, 2),
            "timeLeft":    round(traveler.timeAvailable, 2),
            "isActive":    traveler.activeUser
        }

    # ─────────────────────────────────────────
    # FIX: doActivity — renombrado desde processAirportActivity
    # ─────────────────────────────────────────
    def doActivity(self, travelerId, activityId):
        traveler = self.loadTraveler(travelerId)
        if traveler.currentFlight:
            raise Exception("No puedes hacer actividades mientras estás en vuelo.")
        airport: Airport = self.graph.getAirportPerCode(traveler.actualAirportId)
        activity = next((a for a in airport.activities if a.id == activityId), None)
        if not activity:
            raise Exception("Actividad no encontrada.")
        traveler.AddActivitie(activity, activity.duration)
        traveler.pastTime(activity.duration / 60, self.graph)
        self.saveTravelerData(traveler)
        return {"success": True, "budgetLeft": round(traveler.restantBudget, 2), "timeLeft": round(traveler.timeAvailable, 2)}

    # ─────────────────────────────────────────
    # FIX: doJob — renombrado desde processAirportActivity con isJob=True
    # ─────────────────────────────────────────
    def doJob(self, travelerId, jobId, hours):
        traveler = self.loadTraveler(travelerId)
        if traveler.currentFlight:
            raise Exception("No puedes trabajar mientras estás en vuelo.")
        if not traveler.isActiveToWork():
            raise Exception("El viajero no puede trabajar (presupuesto > 35%).")
        airport: Airport = self.graph.getAirportPerCode(traveler.actualAirportId)
        job = next((j for j in airport.jobs if j.jobId == jobId), None)
        if not job:
            raise Exception("Trabajo no encontrado.")
        traveler.AddActivitie(job, hours)
        traveler.pastTime(hours, self.graph)
        self.saveTravelerData(traveler)
        return {"success": True, "budgetLeft": round(traveler.restantBudget, 2), "timeLeft": round(traveler.timeAvailable, 2)}

    # ─────────────────────────────────────────
    # FIX: interruptFlight — renombrado desde interruptCurrentFlight
    # ─────────────────────────────────────────
    def interruptFlight(self, travelerId, originIata, destinationIata):
        self.graph.blockRoute(originIata, destinationIata)
        traveler = self.loadTraveler(travelerId)
        result = {
            "success": True,
            "blocked": f"{originIata} -> {destinationIata}",
            "recalculated": False,
            "newRoute": []
        }
        if traveler.currentFlight:
            flight = traveler.currentFlight
            if flight["origin"] == originIata and flight["destination"] == destinationIata:
                finalDestination = flight["destination"]
                criterion = flight.get("criterion", "cost")
                aircraft  = flight["aircraftType"]
                traveler.currentFlight     = None
                traveler.restantActivities = []
                origin_vertex = self.graph.getAirportPerCode(traveler.actualAirportId)
                dest_vertex   = self.graph.getAirportPerCode(finalDestination)
                traveler.CreateItineraryPerCriterion(self.graph, criterion, origin_vertex, dest_vertex)
                traveler.AddAllItineraryTravels(self.graph)
                if traveler.restantActivities:
                    totalHours = sum(
                        (self.graph.getRoute(f.origin, f.final).distance *
                         (0.7 if aircraft == "Commercial Airplane" else 1.1 if aircraft == "Regional Plane" else 2.5)) / 60
                        for f in traveler.restantActivities if isinstance(f, ActiveFly)
                    )
                    traveler.currentFlight = {
                        "origin": traveler.actualAirportId,
                        "destination": finalDestination,
                        "hoursTotal": round(totalHours, 2),
                        "hoursProgress": 0.0,
                        "aircraftType": aircraft,
                        "criterion": criterion,
                        "route": traveler.history.visitedDestinations if traveler.history else []
                    }
                    result["recalculated"] = True
                    result["newRoute"] = traveler.history.visitedDestinations if traveler.history else []
        self.saveTravelerData(traveler)
        result["currentAirport"] = traveler.actualAirportId
        result["inTransit"]      = traveler.currentFlight is not None
        return result