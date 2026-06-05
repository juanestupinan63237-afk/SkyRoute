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

