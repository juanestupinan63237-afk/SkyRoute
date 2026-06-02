from Classes.Domain.ActivityUser import Activity

class TemporalActivity (Activity):

    def __init__ (self , id ,hours):
        self.id = id
        self.hours = hours

    def DescountHours (self , hours):
        self.hours -= hours