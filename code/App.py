import os, sys, cv2
import numpy as np
import Tkinter as tk
from CustomizedInterfaceElements import *

from ParkingLot import *


class RoleSelect(tk.Frame):
    def __init__(self, parent):
        tk.Frame.__init__(self, master=root)
        self.pack()

        self.parent = parent

        self.selectSetupButton = tk.Button(self, text="Open Operator", command=self.startSetup)
        self.selectMonitorButton = tk.Button(self, text="Open Monitor", command=self.startMonitor)
        self.selectSetupButton.pack(side=tk.TOP)
        self.selectMonitorButton.pack()

    def startSetup(self):
        app = SetupApp(self.parent, "Parking-Lot.jpg", ParkingLot())
        self.destroy()

    def startMonitor(self):
        app = MonitorApp(self.parent, "Parking-Lot.jpg", ParkingLot("testxml.xml"))
        self.destroy()


class SetupApp(tk.Frame):
    def __init__(self, root, image_path, PKLot):
        tk.Frame.__init__(self, master=root)
        self.pack()

        self.parkinglot = PKLot

        self.window = root
        self.window.title("Display Area")
        self.window.configure(background='grey')

        self.canvas = CanvasArea(self, self.parkinglot, image_path, (800, 600))
        self.canvas.grid(row=0, column=0, sticky=tk.N)

        # Parking Spot List
        # currently an issue with scrolling on the list. it will scroll and then immediately be set back to to 0.
        self.parkingspot_listbox = SpotList(self, self.parkinglot, width=20, height=37)
        self.parkingspot_listbox.grid(row=0, column=1, rowspan=3, sticky='N')

        # MenuBar
        self.menubar = MenuBar(self)
        self.window.configure(menu=self.menubar)


        # exit button
        #self.exitButton = tk.Button(self, text='Quit', command=self.window.destroy)
        #self.exitButton.grid(row=5, column=1, sticky='E')

        # test save and load file buttons
        #self.saveXMLButton = tk.Button(self, text='Save Lot', command=self.parkinglot.saveXML)
        #self.saveXMLButton.grid(row=6, column=1, sticky='E')

        #self.loadXMLButton = tk.Button(self, text='Load Lot', command=self.loadNewLot)
        #self.loadXMLButton.grid(row=7, column=1, sticky='E')

        # delete spot button
        self.deleteSpotButton = tk.Button(self, text='Delete Selected', command=self.deleteSelection)
        self.deleteSpotButton.grid(row=8, column=1, sticky='E')

        # bind root events
        self.window.bind('c', self.window_exit)

        self.update_all()  # this kicks off the main root calling updates ever 100 ms

    def deleteSelection(self):
        self.parkinglot.removeSpot(self.parkingspot_listbox.getSelectionID())

    #def loadNewLot(self):
    #    self.parkingspot_listbox.reset()
    #    self.parkinglot.loadXML('testxml.xml')


    def window_exit(self, event):
        """ listen for program exit button
        """
        self.window.destroy()

    def update_all(self, event=None):
        self.parkingspot_listbox.update_parkingspot_list()

        listpos = self.parkingspot_listbox.current_selection
        idNumber = self.parkingspot_listbox.getSelectionID()

        try:  # try to set the highlighted spot, unless it doesnt exist
            self.canvas.highlightedSpot = self.parkinglot.getSingleSpot(idNumber)
        except (IndexError, AttributeError) as e:
            pass

        self.canvas.update_all()

        self.window.after(100, self.update_all)


class MonitorApp(tk.Frame):
    def __init__(self, root, imagePath, PKLot):
        tk.Frame.__init__(self, master=root)
        self.pack()

        self.parkinglot = PKLot

        self.window = root
        self.window.title("Display Area")
        self.window.configure(background='grey')

        self.canvas = CanvasArea(self, self.parkinglot, image_path, (800, 600))
        self.canvas.grid(row=0, column=0, sticky=tk.N)

        # exit button
        self.exitButton = tk.Button(self, text='Quit', command=self.window.destroy)
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

    #PKListbox = ParkingLot()  # eventually this will be from a saved file.
    #app = SetupApp(root, image_path, PKListbox)
    
    if len(sys.argv) == 1 or sys.argv[1] == 'role':
        app = RoleSelect(root)
    elif sys.argv[1] == 'setup':
        app = SetupApp(root, image_path, ParkingLot())
    else:
        app = RoleSelect(root)
        
    root.mainloop()
