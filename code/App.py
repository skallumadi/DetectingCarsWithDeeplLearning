import os, sys
import cv2
import numpy as np
from Tkinter import *
import tkMessageBox
import Tkinter as tk
from PIL import Image, ImageTk  # imagetk needed to be installed manually. pip install Pillow

from ParkingLot import *


class App:
    def __init__(self, window, image_path, PKLot):
        self.parkinglot = PKLot
       

        self.window = window
        self.window.title("Display Area")
        self.window.configure(background='grey')

        self.cv2_img = self.load_cv2_image(image_path, (800, 600))
        self.tk_img = self.get_imageTK_obj(self.cv2_img)

        # image display area
        self.canvas = tk.Canvas(self.window, height=600, width=800)
        self.canvas_image = self.canvas.create_image(0, 0, image=self.tk_img, anchor=tk.NW)
        self.canvas.image = self.tk_img  # if a reference is not kept of the image, it wont stay in memory.

        self.canvas.grid(row=0, column=0, sticky='N')

        # Information Labels
        self.listBox = tk.Listbox(self.window, width=20, height=2)
        self.scrollbar = Scrollbar(self.window, orient= VERTICAL)
        self.listBox.config(yscrollcommand=self.scrollbar.set)
        self.scrollbar.config(command=self.listBox.yview)
        
        self.numMonitoredSpotsLabel = tk.Label(self.window, text='Monitored')
        self.numOccupiedSpotsLabel = tk.Label(self.window, text='Occupied')
        self.numVacantSpotsLabel = tk.Label(self.window, text='Vacant')

        self.numMonitoredSpotsLabel.grid(row=1, column=0, sticky='W')
        self.numOccupiedSpotsLabel.grid(row=2, column=0, sticky='W')
        self.numVacantSpotsLabel.grid(row=3, column=0, sticky='W')
        self.listBox.grid(row=0, column=1, sticky='W')
        self.scrollbar.grid(row=0, column=1, sticky='E')

        # exit button
        self.exitButton = tk.Button(self.window, text='Quit', command=self.window.destroy)

        self.exitButton.grid(row=5, column=0, sticky='E')

        # bind window events
        self.window.bind('c', self.window_exit)
        self.window.bind('<B1-Motion>', self.draw_area)
        self.window.bind('<ButtonRelease-1>', self.create_rectangle)
        

        self.current_points_list = []  # definitely should be held in a pklot class or something

    def window_exit(self, event):
        """ listen for program exit button
        """
        self.window.destroy()

    def draw_area(self, events):
        """ create an area to turn into a rectangle, and draw points to show
            what is currently recorded
        """
        self.current_points_list.append((events.x, events.y))

        self.canvas.create_oval(events.x - 1, events.y - 1, events.x + 1, events.y + 1, fill="yellow", tags='indicator')

    def create_rectangle(self, events):
        """ creates a rectangle from the points stored in self.current_points_list
            using cv2 libraries. hopefully.
        """
        n_array = np.array(self.current_points_list)  # convert list of points to array

        try:  # someone clicked and released immediately. just ignore it pretty much.
            rectangle = cv2.minAreaRect(n_array)  # find points and angle of rect
            box = cv2.boxPoints(rectangle)  # convert to proper coordinate points
            box = np.int0(box)  # some numpy nonsense. required to work, dunno what it does though

            # convert array tuple thing into coordinate list for tkinter
            coord_list = []  # in format of [x,y, x,y, x,y, x,y, x,y]
            for i in range(4):  # 4 groups of coords.
                coord_list.append(box[i][0])
                coord_list.append(box[i][1])

            self.listBox.insert(END, coord_list)
            self.parkinglot.addSpot(coord_list)
            

        except cv2.error:
            pass

        self.current_points_list = []
        self.canvas.delete('indicator')
        self.draw_rectangles()

    def draw_rectangles(self):
        self.canvas.delete('parking spots')
        for spot in parkinglot.getParkingSpots():
            self.canvas.create_polygon(spot.location, fill='', outline='lime', tags='parking spots')

    def load_cv2_image(self, path, dimensions):
        """ From the given path, load and resize a jpeg
            and return a cv2 image object
        """
        if not dimensions:
            raise Exception("Must provide height and width as tuple")
        img = cv2.imread(path)
        img = cv2.resize(img, dimensions, interpolation=cv2.INTER_CUBIC)
        return img

    def get_imageTK_obj(self, cv2Img):
        """ from the given cv2 image, return a TKImage object for display
        """
        # the color channels need to be shuffled around due to differences between cv2 and tk
        b, g, r = cv2.split(cv2Img)
        shuffled_image = cv2.merge((r, g, b))

        img = Image.fromarray(shuffled_image)

        # photoimage objects can be used any place that tkinter expects an image
        im_tk = ImageTk.PhotoImage(image=img)
        return im_tk


if __name__ == "__main__":

    image_path = "Parking-Lot.jpg"
    try:
        assert os.path.isfile(image_path)
    except AssertionError:
        print "ERROR: Invalid Image Path"
        sys.exit()

    root = tk.Tk()
    parkinglot = ParkingLot()
    app = App(root, image_path, parkinglot)
    root.mainloop()
