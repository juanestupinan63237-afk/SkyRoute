class TemporalJob:

    def __init__ (self , time , pay , id):
        self.time = time
        self.pay = pay
        self.id = id

    def DescountHours (self , pastHours):
        self.time -= pastHours

    def getTotalPay (self):
        return self.pay * self.time