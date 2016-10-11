import cv2
class ParkingLot:
    def __init__(self):
        self.infoPath = "" #xml file location for parking spots
        self.numSpots = 0 #how many spots are on record
        self.numOccupied = 0
        self.numVacant = 0
        self.parkingSpots = []  # a list of all the parking spots and status.
                                # [parkingSpot, parkingSpot, etc]
                                # parking spot = [id#, status, (coordinates)]

        self.currentLotImage = #the most recent image for the parking lot
        self.imageClassifier = #link to image classifier object to process images
    def loadXML(self, filePath):
        ''' load xml file and put information in the right places.
            number of spots, initialize parking spots list.
        '''
    def getParkingSpots(self):
        ''' return a list of all parking spots in the lot
        '''
        return self.parkingSpots
        pass

    def saveParkingSpots(self):
        ''' save the current list of parking spaces.
            meant to be used if a parking spot is added or removed.
        '''
        pass
    def saveUsage(self, filePath):
        ''' save current lot information to separate file.
            how many spots are open, which ones specifically, time, etc.
        '''
        pass
    def getOccupied(self):
        ''' get a list of all occupied spaces in the lot.
        '''
        occupiedList = []
        for spot in self.parkingSpots:
            if spot[1] == 'occupied':
                occupiedList.append(spot)
        return occupiedList
        pass
    def getVacant(self):
        ''' get a list of all vacant spaces in the lot.
        '''
        vacantList = []
        for spot in self.parkingSpots:
            if spot[1] == 'vacant':
                vacantList.append(spot)
        return vacantList
        pass
    def addSpot(self, coordinates):
        ''' add a region of the parking lot as a new space to be monitored.
            coordinates is expected to be a list or tuple 8 items long.
            4 groups of x y coordinates.
            Ex:
            [0, 0, 10, 14, 30, 30, 56, 67]
             x  y  x   y   x   y   x   y
        '''
        self.numSpots += 1
        self.parkingSpots.append([self.numSpots, 'vacant', coordinates])
        self.update(self.currentLotImage)
        pass
    def removeSpot(self, id):
        ''' remove a particular spot from the list of monitored locations.
        '''
        try:
            self.parkingSpots.pop(id) #remove the requested spot
        except IndexError:
            print "Given spot id does not exist in the current list"

        for i in range(len(self.parkingSpots)): # relabel all spots to keep the id numbers
            self.parkingSpots[i][0] = i         # representative of the number of spots
        pass
    def update(self, image):
        ''' update the current information for this parking lot.
            the image given is expected to be the most recent image for the lot.
        '''
        self.currentLotImage = image
        self.parkingSpots = self.imageClassifier.process(self.parkingSpots)
        pass
