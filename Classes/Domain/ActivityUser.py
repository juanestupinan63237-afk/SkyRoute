class Activity:
    def __init__(self, name , id , duration, price , isImportant = False):
        self.name = name
        self.id = id
        self.duration = duration
        self.price = price
        self.isImportant = isImportant