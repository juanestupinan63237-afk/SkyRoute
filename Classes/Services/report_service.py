from Classes.Nucleus.AirportVertex import Airport
from Classes.Traveler_Logic.Traveler import Traveler
from Classes.Nucleus.Graph import Graph
from Classes.Domain.ActiveFly import ActiveFly
from Classes.Domain.TemporalActivity import TemporalActivity
from Classes.Domain.TemporalJob import TemporalJob

class ReportService:
    def build_report(self, traveler: Traveler, graph: Graph)-> dict:
        report = {
            "Traveler": traveler.name,
            "Activities": []
        }
        for activity in traveler.activities:
            if isinstance(activity, TemporalActivity):
                report["Activities"].append({
                    "Type": "Temporal Activity",
                    "Name": activity.name,
                    "duration": activity.duration,
                    "price": activity.price
                })
            elif isinstance(activity, TemporalJob):
                report["Activities"].append({
                    "Type": "Temporal Job",
                    "id": activity.id,
                    "hours": activity.start_time,
                    "earned": activity.getTotalPay()
                })
            elif isinstance(activity, ActiveFly):
                report["Activities"].append({
                    "Type": "Active Fly",
                    "origin": activity.origin,
                    "destination": activity.final,
                    "hours": activity.hours,
                })
        return report

    def build_traveler_summary(self,traveler: Traveler)-> dict:
            total_spent = traveler.budget - traveler.restantBudget
            total_earned= self.calculate_total_earned(traveler)
            balance = traveler.restantBudget
            
            return {
                "name": getattr(traveler, "name", "viajero"),
                "initial_budget": round(traveler.budget, 2),
                "total_spent": round(total_spent, 2),
                "total_earned": round(total_earned, 2),
                "finalbalance": round(balance, 2),
                "totalTimeHours": round(
                    getattr(traveler, "elapsed_hours",
                            traveler.budget/max(traveler.budget, 1)), 2
                ), 
        }

    def calculate_total_earned(self, traveler: Traveler) -> float:
            total_earned = 0.0
            for activity in traveler.activities:
                if isinstance(activity, TemporalJob):
                    total_earned += activity.getTotalPay()
            return total_earned

    def _build_destination(self, traveler: Traveler, graph: Graph) -> list:
        destinations = []
        for iata_code in traveler.visitedAirports:
            try:
                airport: Airport = graph.getAirportPerCode(iata_code)
            except Exception:
                continue
            cost_at_destination = self.calculate_cost_at_destination(traveler, iata_code, airport)
            destinations.append({
                "iata_code": airport.iataId,
                "name": airport.name,
                "city": airport.city,
                "country": airport.country,
                "isHub": airport.isHub,
                "stayMinutes": self.
                _stay_minutes(traveler, iata_code),
                    "totalCostDestination": round(cost_at_destination, 2)
                        
                            })
            return destinations

    def _cost_at_destination(self, traveler: Traveler, iata_code: str, airport: Airport) -> float:
            total_cost = 0.0
            for activity in traveler.activities:
                if isinstance(activity, TemporalActivity):
                    cost += getattr(activity, "price", 0.0)
                return total_cost
    def _stay_minutes(self, traveler: Traveler, iata_code: str) -> int:
            total_activity_minutes = 0
            for activity in traveler.activities:
                if isinstance(activity, TemporalActivity):
                    total_activy_minutes += getattr(activity, "duration", 0)
            return total_activity_minutes 
            



    

