class Spot:
    def __init__(self, idNumber, location, status='vacant'):
        self.idNum = idNumber
        self.location = location # should be a list 8 long, alternating x y values
        self.status = status #string, 'occupied' or 'vacant'
