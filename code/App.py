import os, sys, cv2
import numpy as np
import Tkinter as tk
from CustomizedInterfaceElements import *

from ParkingLot import *


class RoleSelect(tk.Frame):
    def __init__(self, root):
        tk.Frame.__init__(self, master=root)

        self.root = root

        self.selectSetupButton = tk.Button(self.root, text="Open Operator", command=self.startSetup)
        self.selectMonitorButton = tk.Button(self.root, text="Open Monitor", command=self.startMonitor)
        self.selectSetupButton.pack(side=tk.TOP)
        self.selectMonitorButton.pack()

    def startSetup(self):
        app = SetupApp(self.root, "Parking-Lot.jpg", ParkingLot())
        self.destroy()

    def startMonitor(self):
        app = MonitorApp(self.root, "Parking-Lot.jpg", ParkingLot("testxml.xml"))


class SetupApp(tk.Frame):
    def __init__(self, root, image_path, PKLot):
        tk.Frame.__init__(self, master=root)

        self.parkinglot = PKLot

        self.window = root
        self.window.title("Display Area")
        self.window.configure(background='grey')

        self.canvas = CanvasArea(root, self.parkinglot, image_path, (800, 600))
        self.canvas.grid(row=0, column=0, sticky=tk.N)

        # Parking Spot List
        self.parkingspot_listbox = SpotList(self.window, self.parkinglot, width=20, height=30)
        self.parkingspot_listbox.grid(row=0, column=1, rowspan=3, sticky='N')

        # Information Labels
        #self.numMonitoredSpotsLabel = tk.Label(self.window, text='Monitored')
        #self.numOccupiedSpotsLabel = tk.Label(self.window, text='Occupied')
        #self.numVacantSpotsLabel = tk.Label(self.window, text='Vacant')

        #self.numMonitoredSpotsLabel.grid(row=1, column=0, sticky='W')
        #self.numOccupiedSpotsLabel.grid(row=2, column=0, sticky='W')
        #self.numVacantSpotsLabel.grid(row=3, column=0, sticky='W')

        # exit button
        self.exitButton = tk.Button(self.window, text='Quit', command=self.window.destroy)
        self.exitButton.grid(row=5, column=1, sticky='E')

        # test save and load file buttons
        self.saveXMLButton = tk.Button(self.window, text='Save Lot', command=self.parkinglot.saveXML)
        self.saveXMLButton.grid(row=6, column=1, sticky='E')

        self.loadXMLButton = tk.Button(self.window, text='Load Lot', command=self.parkinglot.loadXML)
        self.loadXMLButton.grid(row=7, column=1, sticky='E')

        # bind root events
        self.window.bind('c', self.window_exit)

        self.update_all()  # this kicks off the main root calling updates ever 100 ms


    def window_exit(self, event):
        """ listen for program exit button
        """
        self.window.destroy()

    def update_all(self, event=None):
        self.parkingspot_listbox.update_parkingspot_list()

        listpos = self.parkingspot_listbox.current_selection
        try:  # long af
            self.canvas.highlightedLotLocation = self.parkinglot.getParkingSpots()[listpos].location
        except IndexError:
            pass

        self.canvas.update_all()

        self.window.after(100, self.update_all)


class MonitorApp(tk.Frame):
    def __init__(self, root, imagePath, PKLot):
        self.parkinglot = PKLot

        self.window = root
        self.window.title("Display Area")
        self.window.configure(background='grey')

        self.canvas = CanvasArea(root, self.parkinglot, image_path, (800, 600))
        self.canvas.grid(row=0, column=0, sticky=tk.N)

        # exit button
        self.exitButton = tk.Button(self.window, text='Quit', command=self.window.destroy)
        self.exitButton.grid(row=1, column=1, sticky='E')

        #bind events
        self.window.bind('c', self.window_exit)

        self.update_all()  # this kicks off the main root calling updates ever 100 ms

    def window_exit(self):
        self.window.destroy()

    def update_all(self):

        self.canvas.update_all()
        self.window.after(100, self.update_all)

if __name__ == "__main__":

    image_path = "Parking-Lot.jpg"
    try:
        assert os.path.isfile(image_path)
    except AssertionError:
        print "ERROR: Invalid Image Path"
        sys.exit()

    root = tk.Tk()
    #parkinglot = ParkingLot()  # eventually this will be from a saved file.
    #app = SetupApp(root, image_path, parkinglot)
    app = RoleSelect(root)
    root.mainloop()
