from Classes.Nucleus.AirportVertex import Airport
from Classes.Traveler_Logic.Traveler import Traveler
from Classes.Nucleus.Graph import Graph
from Classes.Domain.ActiveFly import ActiveFly
from Classes.Domain.TemporalActivity import TemporalActivity
from Classes.Domain.TemporalJob import TemporalJob


class ReportService:

    def build_report(self, traveler: Traveler, graph: Graph) -> dict:
        return {
            "traveler":            traveler.name,
            "visitedDestinations": self._build_destinations(traveler, graph),
            "flightsFlown":        self._build_flights(traveler, graph),
            "activitiesPerformed": self._build_activities(traveler),
            "jobsPerformed":       self._build_jobs(traveler),
            "totals":              self._build_totals(traveler),
        }

    def _build_destinations(self, traveler: Traveler, graph: Graph) -> list:
        destinations = []
        for iata_code in traveler.visitedAirports:
            try:
                airport: Airport = graph.getAirportPerCode(iata_code)
            except Exception:
                continue
            destinations.append({
                "iataCode":             airport.iataId,
                "name":                 airport.name,
                "city":                 airport.city,
                "country":              airport.country,
                "isHub":                airport.isHub,
                "stayMinutes":          self._stay_minutes_at(traveler, iata_code),
                "totalCostDestination": round(
                    self._cost_at_destination(traveler, iata_code, airport), 2
                ),
            })
        return destinations

    def _cost_at_destination(self, traveler: Traveler, iata_code: str, airport: Airport) -> float:
        total_cost = 0.0
        for activity in traveler.activities:
            if isinstance(activity, TemporalActivity):
                if getattr(activity, "airportId", None) == iata_code:
                    total_cost += getattr(activity, "price", 0.0)
        return total_cost

    def _stay_minutes_at(self, traveler: Traveler, iata_code: str) -> int:
        total_minutes = 0
        for activity in traveler.activities:
            if isinstance(activity, TemporalActivity):
                if getattr(activity, "airportId", None) == iata_code:
                    total_minutes += getattr(activity, "duration", 0)
        return total_minutes

    def _build_flights(self, traveler: Traveler, graph: Graph) -> list:
        flights = []
        for activity in traveler.activities:
            if isinstance(activity, ActiveFly):
                flight_cost = 0.0
                flight_time = activity.hours
                aircraft_type = "Unknown"
                distance_km = 0.0
                try:
                    route = graph.getRoute(activity.origin, activity.final)
                    distance_km   = route.distance
                    aircraft_type = route.aircraft.type
                    flight_cost   = round(
                        route.basePrice + route.aircraft.calculateCost(route.distance), 2
                    )
                    flight_time   = route.distance * route.aircraft.timeKm / 60
                except Exception:
                    pass
                flights.append({
                    "origin":          activity.origin,
                    "destination":     activity.final,
                    "aircraftType":    aircraft_type,
                    "distanceKm":      round(distance_km, 2),
                    "flightTimeHours": round(flight_time, 2),
                    "costUSD":         flight_cost,
                })
        return flights

    def _build_activities(self, traveler: Traveler) -> list:
        activities = []
        for activity in traveler.activities:
            if isinstance(activity, TemporalActivity):
                activities.append({
                    "name":        getattr(activity, "name", "Activity"),
                    "type":        "mandatory" if getattr(activity, "isImportant", False) else "optional",
                    "durationMin": getattr(activity, "duration", 0),
                    "costUSD":     round(getattr(activity, "price", 0.0), 2),
                })
        return activities

    def _build_jobs(self, traveler: Traveler) -> list:
        jobs = []
        for activity in traveler.activities:
            if isinstance(activity, TemporalJob):
                jobs.append({
                    "jobId":       getattr(activity, "id", ""),
                    "hoursWorked": round(getattr(activity, "time", 0), 2),
                    "earnedUSD":   round(activity.getTotalPay(), 2),
                })
        return jobs

    def _build_totals(self, traveler: Traveler) -> dict:
        total_earned = sum(
            a.getTotalPay()
            for a in traveler.activities
            if isinstance(a, TemporalJob)
        )
        total_spent = traveler.budget - traveler.restantBudget

        flight_hours = sum(getattr(a, "hours", 0) for a in traveler.activities if isinstance(a, ActiveFly))
        stay_hours   = sum(getattr(a, "duration", 0) / 60 for a in traveler.activities if isinstance(a, TemporalActivity))
        job_hours    = sum(getattr(a, "time", 0) for a in traveler.activities if isinstance(a, TemporalJob))

        initial_time = getattr(traveler, "initialTimeAvailable", traveler.timeAvailable)
        return {
            "initialBudget":       round(traveler.budget, 2),
            "totalSpent":          round(total_spent, 2),
            "totalEarned":         round(total_earned, 2),
            "finalBalance":        round(traveler.restantBudget, 2),
            "timeRemainingH":      round(traveler.timeAvailable, 2),
            "destinationsVisited": len(traveler.visitedAirports),
            "totalTimeUsedH":      round(initial_time - traveler.timeAvailable, 2),
        }

    def build_traveler_summary(self, traveler: Traveler) -> dict:
        return self._build_totals(traveler)

    def calculate_total_earned(self, traveler: Traveler) -> float:
        total_earned = 0.0
        for activity in traveler.activities:
            if isinstance(activity, TemporalJob):
                total_earned += activity.getTotalPay()
        return total_earned