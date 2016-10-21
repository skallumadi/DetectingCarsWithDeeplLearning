import os, sys, cv2
import numpy as np
import Tkinter as tk
from PIL import Image, ImageTk  # imagetk needed to be installed manually. pip install Pillow

from ParkingLot import *
#this is to demonstrate

class CanvasArea(tk.Canvas):
    """ A canvas object that is to be used as the main display area in the app.
        This inherits from the Tkinter Canvas object, and adds specific functionality relating to the current project.
        This was done to reduce the complexity of the App class, and hopefully improve readability.

        (Initially this class was not going to inherit straight from the Canvas class,
            but this makes event binding possible without a bunch of headache.)

        This will hopefully serve as an example going forward if other elements of the app get too complicated
            to keep in the main class, and separating it would be of benefit.
    """

    def __init__(self, window, parkinglot, imgpath, dimensions):
        tk.Canvas.__init__(self, master=window, width=dimensions[0], height=dimensions[1])

        self.window = window
        self.dimensions = dimensions
        self.parkinglot = parkinglot

        self.cv2_img = self.load_cv2_image(imgpath, self.dimensions)
        self.tk_img = self.get_imageTK_obj(self.cv2_img)

        self.create_image(0, 0, image=self.tk_img, anchor=tk.NW)
        self.image = self.tk_img

        # bind canvas events
        # multiple functions can be bound to an event by using the 'add="+"' argument. TIL.
        self.bind('<B1-Motion>', self.drawArea)
        self.bind('<ButtonRelease-1>', self.createRectangle, add="+")
        self.bind('<ButtonRelease-1>', self.update_all, add="+")

        self.current_points_list = []  # used for the box currently being drawn
        self.highlightedLotLocation = [0, 1, 2, 3, 4, 5, 6, 7]

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

    def drawArea(self, events):
        """ create an area to turn into a rectangle, and draw points to show
            what is currently recorded
        """
        self.current_points_list.append((events.x, events.y))

        self.create_oval(events.x - 1, events.y - 1, events.x + 1, events.y + 1, fill="yellow", tags='indicator')

    def createRectangle(self, events):
        """ creates a rectangle from the points stored in self.current_points_list
            using cv2 libraries.
            adds this rectangle as a new parking spot to self.parkinglot
        """
        n_array = np.array(self.current_points_list)  # convert list of points to array

        try:  # someone clicked and released immediately. just ignore it pretty much.
            rectangle = cv2.minAreaRect(n_array)  # find points and angle of rect
            box = cv2.cv.BoxPoints(rectangle)  # convert to proper coordinate points
            box = np.int0(box)  # some numpy nonsense. required to work, dunno what it does though

            # convert array tuple thing into coordinate list for tkinter
            coord_list = []  # in format of [x,y, x,y, x,y, x,y, x,y]
            for i in range(4):  # 4 groups of coords.
                coord_list.append(box[i][0])
                coord_list.append(box[i][1])

            self.parkinglot.addSpot(coord_list)

        except cv2.error:
            pass

        self.current_points_list = []
        self.delete('indicator')  # clear out all those little dots from drawing

    def draw_rectangles(self):
        self.delete('parking spots')
        for spot in parkinglot.getParkingSpots():
            self.create_polygon(spot.location, fill='', outline='lime', tags='parking spots')

    def update_all(self, events=None):
        self.draw_rectangles()
        self.delete('highlight')
        self.create_polygon(self.highlightedLotLocation, fill='', outline='white', tags='highlight')


class SpotList(tk.Listbox):
    """ This is a list object that inherits from the Tkinter Listbox.
        Functionality has been added specific to this project, specifically regarding operations that change the list.
    """
    def __init__(self, window, parkingLot, width=20, height=30):
        self.window = window
        self.parkinglot = parkingLot
        self.width = width
        self.height = height

        tk.Listbox.__init__(self, self.window, width=self.width, height=self.height)

        # keep track of the length of the list, to use when updating
        self.current_length = 0
        self.current_selection = -1  # track current selection outside of default ANCHOR
        # bind list events
        self.bind("<<ListboxSelect>>", self.onSelect)

    def update_parkingspot_list(self):
        """ Redraw the list from the current collection of parking spaces.
            Only do this if there has been a change in the size of the parking spot list
        """

        numParkingSpots = len(self.parkinglot.getParkingSpots())

        # update if a spot has been created
        # ugly but currently it works
        if numParkingSpots != self.current_length:

            if numParkingSpots > self.current_length:
                self.current_selection = numParkingSpots -1
            self.current_length = numParkingSpots

            self.delete(0, tk.END)
            for spot in self.parkinglot.getParkingSpots():
                self.insert(tk.END, spot.idNum)

            self.select_anchor(self.current_selection)
            self.selection_set(self.current_selection)

    def onSelect(self, events):
        index = events.widget.get(int(events.widget.curselection()[0])) - 1
        self.current_selection = index
        self.update_parkingspot_list()


class App:
    def __init__(self, window, image_path, PKLot):
        self.parkinglot = PKLot

        self.window = window
        self.window.title("Display Area")
        self.window.configure(background='grey')

        self.canvas = CanvasArea(window, self.parkinglot, image_path, (800, 600))
        self.canvas.grid(row=0, column=0, sticky=tk.N)

        # Parking Spot List
        self.parkingspot_listbox = SpotList(self.window, self.parkinglot, width=20, height=30)
        self.parkingspot_listbox.grid(row=0, column=1, rowspan=3, sticky='N')

        # Information Labels
        self.numMonitoredSpotsLabel = tk.Label(self.window, text='Monitored')
        self.numOccupiedSpotsLabel = tk.Label(self.window, text='Occupied')
        self.numVacantSpotsLabel = tk.Label(self.window, text='Vacant')

        self.numMonitoredSpotsLabel.grid(row=1, column=0, sticky='W')
        self.numOccupiedSpotsLabel.grid(row=2, column=0, sticky='W')
        self.numVacantSpotsLabel.grid(row=3, column=0, sticky='W')

        # exit button
        self.exitButton = tk.Button(self.window, text='Quit', command=self.window.destroy)

        self.exitButton.grid(row=5, column=1, sticky='E')

        # bind window events
        self.window.bind('c', self.window_exit)

        self.update_all()  # this kicks off the main window calling updates ever 100 ms

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


if __name__ == "__main__":

    image_path = "Parking-Lot.jpg"
    try:
        assert os.path.isfile(image_path)
    except AssertionError:
        print "ERROR: Invalid Image Path"
        sys.exit()

    root = tk.Tk()
    parkinglot = ParkingLot()  # eventually this will be a saved parking lot i imagine.
    app = App(root, image_path, parkinglot)
    root.mainloop()
