import os, sys
import cv2
import numpy as np
import Tkinter as tk
from PIL import Image, ImageTk   #imagetk needed to be installed manually through apt-get
                        #sudo apt-get install python-imaging-tk

class App:
    def __init__(self, window, image_path):
        self.window = window
        self.window.title("Display Area")
        self.window.configure(background='grey')

        self.cv2_img = self.load_cv2_image(image_path, (800,600))
        self.tk_img = self.get_imageTK_obj(self.cv2_img)

        #image display area
        self.canvas=tk.Canvas(self.window, height=600, width=800)
        self.canvas_image = self.canvas.create_image(0,0, image=self.tk_img, anchor=tk.NW)
        self.canvas.image = self.tk_img #if a reference is not kept of the image, it will be garbage collected out of existence.

        self.canvas.pack(side='bottom', fill='both', expand='yes')

        self.window.bind('c', self.window_exit)
        self.window.bind('<B1-Motion>', self.draw_area)
        self.window.bind('<ButtonRelease-1>', self.create_rectangle)

        self.current_points_list = [] #definitely should be held in a pklot class or something

    def window_exit(self, event):
        """ listen for program exit button
        """
        self.window.destroy()

    def draw_area(self, events):
        """ create an area to turn into a rectangle, and draw points to show
            what is currently recorded
        """
        self.current_points_list.append((events.x, events.y))

        self.canvas.create_oval(events.x-1, events.y-1, events.x+1, events.y+1, fill="yellow")

    def create_rectangle(self, events):
        """ creates a rectangle from the points stored in self.current_points_list
            using cv2 libraries. hopefully.
        """
        n_array = np.array(self.current_points_list) #convert list of points to array
        rectangle = cv2.minAreaRect(n_array) #find points and angle of rect
        box = cv2.cv.BoxPoints(rectangle) #convert to proper coordinate points
        box = np.int0(box) #some numpy nonsense. required to work, dunno what it does though


        #convert array into coordinate tuple for tkinter
        coord_list = []
        for i in range(4): #4 groups of coords.
            coord_list.append(box[i][0])
            coord_list.append(box[i][1])
        self.canvas.create_polygon(coord_list, fill='', outline='lime')
        self.current_points_list = []


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
        b,g,r = cv2.split(cv2Img)
        shuffled_image = cv2.merge((r,g,b))

        img = Image.fromarray(shuffled_image)

        #photoimage objects can be used any place that tkinter expects an image
        im_tk = ImageTk.PhotoImage(image=img)
        return im_tk

if __name__ == "__main__":
    #image = cv2.imread("Parking-Lot.jpg", cv2.IMREAD_COLOR)
    #cv2.imshow('image', image)
    #cv2.waitKey(0)

    image_path = "Parking-Lot.jpg"
    try:
        assert os.path.isfile(image_path)
    except AssertionError:
        print "ERROR: Invalid Image Path"
        sys.exit()

    root = tk.Tk()
    app = App(root, image_path)
    root.mainloop()
