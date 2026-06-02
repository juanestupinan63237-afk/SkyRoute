class ActiveFly:

    def __init__ (self , origin , final , hours , restantHours):
        self.origin = origin 
        self.final = final
        self.hours = hours
        self.restantHours = restantHours

    def DescountHours (self , hours):
        self.DescountHours -= hours