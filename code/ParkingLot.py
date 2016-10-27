from Spot import *
import xml.etree.ElementTree as ET


class ParkingLot:
    def __init__(self, path=None):
        self.spotIDCounter = 0  # how many spots are on record
        self.numOccupied = 0
        self.numVacant = 0
        self.parkingSpots = []  # a list of all the parking spots and status.

        # self.currentLotImage = #the most recent image for the parking lot
        # self.imageClassifier = #link to image classifier object to process images

        if path:
            self.infoPath = path
            self.loadXML()
        else:
            self.infoPath = 'testxml.xml'

    def loadXML(self, filename):
        """ load xml file and put information in the right places.
            number of spots, initialize parking spots list.
        """
        self.parkingSpots = []

        tree = ET.ElementTree(file=filename)
        self.spotIDCounter = int(next(tree.iter(tag='NextAvailableID')).attrib['counter'])
        for elem in tree.iter(tag='Spot'):
            loc = elem.attrib['location']
            idNumber = elem.attrib['id']
            self.addSpot([int(x) for x in loc.split()], idNumber)

    def saveXML(self, filename):
        """ save the current list of parking spaces.
        """
        root = ET.Element('root')
        pklot = ET.SubElement(root, "ParkingLot")

        idCounter = ET.SubElement(pklot, "NextAvailableID", counter=str(self.spotIDCounter))
        for spot in self.parkingSpots:
            ET.SubElement(pklot, 'Spot', id=str(spot.id), location=' '.join(str(x) for x in spot.location))

        tree = ET.ElementTree(root)
        tree.write(filename)

    def saveUsage(self, filePath):
        """ save current lot information to separate file.
            how many spots are open, which ones specifically, time, etc.
        """
        pass

    def getParkingSpots(self):
        """ return a list of all parking spots in the lot
        """
        return self.parkingSpots

    def getOccupied(self):
        """ get a list of all occupied spaces in the lot.
        """
        occupiedList = []
        for spot in self.parkingSpots:
            if spot.status == 'occupied':
                occupiedList.append(spot)
        return occupiedList

    def getSingleSpot(self, idNum):
        for spot in self.parkingSpots:
            if spot.id == idNum:
                return spot

    def getVacant(self):
        """ get a list of all vacant spaces in the lot.
        """
        vacantList = []
        for spot in self.parkingSpots:
            if spot.status == 'vacant':
                vacantList.append(spot)
        return vacantList

    def addSpot(self, coordinates, ID=None):
        """ add a region of the parking lot as a new space to be monitored.
            coordinates is expected to be a list or tuple 8 items long.
            4 groups of x y coordinates.
            Ex:
            [0, 0, 10, 14, 30, 30, 56, 67]
             x  y  x   y   x   y   x   y
        """
        if ID:
            self.parkingSpots.append(Spot(ID, coordinates, 'vacant'))
        else:
            self.parkingSpots.append(Spot(self.spotIDCounter, coordinates, 'vacant'))
            self.spotIDCounter += 1
        # self.update(self.currentLotImage)

    def removeSpot(self, ID):
        """ remove a particular spot from the list of monitored locations.
        """
        for spot in self.parkingSpots:
            if spot.id == ID:
                self.parkingSpots.remove(spot)
                #for i in range(len(self.parkingSpots)):  # relabel all spots to keep the id numbers
                #    self.parkingSpots[i].id = i  # representative of the number of spots
                return
        raise Exception("No spot with given id " + str(ID) + " found.")

    def update(self, image):
        """ update the current information for this parking lot.
            the image given is expected to be the most recent image for the lot.
        """
        self.currentLotImage = image
        self.parkingSpots = self.imageClassifier.process(self.parkingSpots)
