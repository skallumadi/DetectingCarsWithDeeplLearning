import Tkinter as tk
import tkFileDialog
import cv2
from PIL import Image, ImageTk  # imagetk needed to be installed manually. pip install Pillow
import numpy as np

from Spot import Spot


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
        self.highlightedSpot = Spot('-1', [0,0,0,0,0,0,0,0])

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
            adds this rectangle as a new parking spot to self.PKListbox
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
        self.delete('parkingspot')
        self.delete('parkinglabel')
        for spot in self.parkinglot.getParkingSpots():
            self.create_polygon(spot.location, fill='', outline='lime', tags='parkingspot')
            self.create_text(spot.location[0]+10, spot.location[1]+10, text=spot.id, tags='parkinglabel', fill='lime')

    def update_all(self, events=None):
        self.draw_rectangles()
        self.delete('highlight')
        try:
            self.create_polygon(self.highlightedSpot.location, fill='', outline='white', tags='highlight', width=2)
            self.create_text(self.highlightedSpot.location[0]+10, self.highlightedSpot.location[1]+10, text=self.highlightedSpot.id, tags='highlight', fill='red')
        except AttributeError:
            pass


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
        self.current_selection = 0  # track current selection outside of default ANCHOR
        # bind list events
        self.bind("<<ListboxSelect>>", self.onSelect)
        self.bind("<Double-1>", self.onDoubleClick)

    def update_parkingspot_list(self):
        """ Redraw the list from the current collection of parking spaces.
            Only do this if there has been a change in the size of the parking spot list

            This thing has given me the largest headache. but i THINK it works like it is supposed to now. please.
            If ever there is a mysterious problem with highlighting or list things, start here.
        """

        numParkingSpots = len(self.parkinglot.getParkingSpots())

        # update if a spot has been created
        # ugly but currently it works
            #addendum: this used to only execute on changes, but it made problems with renaming spots. now its constant.
            #if numParkingSpots != self.current_length: #old conditional check
        if numParkingSpots > self.current_length:
            self.current_selection = numParkingSpots - 1

        if numParkingSpots <= self.current_selection:
            self.current_selection -= 1

        self.current_length = numParkingSpots

        self.delete(0, tk.END)
        for spot in self.parkinglot.getParkingSpots():
            self.insert(tk.END, spot.id)

        # are all of these really needed? i think the top one can be removed.
        self.select_anchor(self.current_selection)
        self.selection_set(self.current_selection)
        self.activate(self.current_selection)

    def onSelect(self, events):
        index = self.curselection()[0]
        self.current_selection = index
        self.update_parkingspot_list()

    def onDoubleClick(self, events):
        pop = NameEntryPopup(self)

    def getSelectionID(self):
        return self.get(self.current_selection)

    def reset(self):
        self.current_length = 0
        self.current_selection = 0


class NameEntryPopup:
    def __init__(self, ParkingLotListBox):
        # to keep consistent this class should really be an instance of a tk frame or something.
        self.top = tk.Toplevel()
        self.PKListbox = ParkingLotListBox

        self.label = tk.Label(self.top, text='New Name: ')
        self.button = tk.Button(self.top, text='submit', command=self.submit)
        self.entry = tk.Entry(self.top)

        self.label.pack(side=tk.LEFT)
        self.entry.pack(side=tk.LEFT)
        self.button.pack(side=tk.LEFT)

        self.top.bind('<Return>', self.submit)

    def submit(self, events=None):
        self.PKListbox.parkinglot.getSingleSpot(self.PKListbox.getSelectionID()).id = self.entry.get()
        self.top.destroy()

class MenuBar(tk.Menu):
    def __init__(self, parent):
        self.parent = parent
        tk.Menu.__init__(self, self.parent)

        self.add_command(label="Open ParkingLot", command=self.openFile)
        self.add_command(label="Save ParkingLot", command=self.saveLot)
        self.add_command(label="Quit", command=self.exitProgram)

        self.lastFileUsage = ""

    def openFile(self):
        filename = tkFileDialog.askopenfile(parent=self.parent)
        if filename is not None:
            self.lastFileUsage = filename
            try:
                self.parent.parkinglot.loadXML(filename)
            except (SyntaxError, AttributeError) as e:
                print "Improper File"
                pass
        else:
            pass

    def saveLot(self):
        filename = tkFileDialog.asksaveasfile(parent=self.parent)
        if filename is not None:
            self.lastFileUsage = filename
            self.parent.parkinglot.saveXML(self.lastFileUsage)
        else:
            pass

    def exitProgram(self):
        self.parent.window.destroy()