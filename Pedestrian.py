class Pedestrian:
    def __init__(self, id, genre, age, waitingTime, travelSpeed):
        self.id=id
        self.genre=genre
        self.age=age
        self.waitingTime=waitingTime
        self.travelSpeed=travelSpeed

    def getWaitingTime(self):
        return self.waitingTime

    def setWaitingTime(self,newWaitingTime):
        self.waitingTime=newWaitingTime