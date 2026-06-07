class TemporalActivity:
    def __init__(self, id, hours, name="", duration=0, price=0, airportId=None, isImportant=False):
        self.id = id
        self.hours = hours
        self.name = name
        self.duration = duration
        self.price = price
        self.airportId = airportId

    def DescountHours (self , hours):
        self.hours -= hours