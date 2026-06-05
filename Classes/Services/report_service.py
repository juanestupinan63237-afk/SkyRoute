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
                  getattr(travler, "elapsed_hours",
                          traveler.budget/max(traveler.budget, 1)), 2
             ), 
    }
        
    

