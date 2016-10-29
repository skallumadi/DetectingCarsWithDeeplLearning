class Spot:
    def __init__(self, ID, location, status='empty'):
        self.id = ID
        self.location = location # should be a list 8 long, alternating x y values
        self.status = status  # string, 'occupied' or 'empty'
