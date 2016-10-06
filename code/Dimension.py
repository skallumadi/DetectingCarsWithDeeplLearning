import os, sys
import cv2
import numpy as np
import Tkinter as tk
import Image, ImageTk   #imagetk needed to be installed manually through apt-get
                        #sudo apt-get install python-imaging-tk

def on_mouse(event, x, y, flags, params):
    #defined by jeswin for use on cv2
    if event == cv.CV_EVENT_LBUTTONDOWN:
        print 'Start Mouse Position: '+str(x)+', '+str(y)
        sbox = [x, y]
        boxes.append(sbox)
    elif event == cv.CV_EVENT_LBUTTONUP:
        print 'End Mouse Position: '+str(x)+', '+str(y)
        ebox = [x, y]
        boxes.append(ebox)

def cv2_loop():
    #the gui loop written by jeswin for use with cv2
    count = 0
    while(1):
        count += 1
        _,img = cap.read()
        img = cv2.blur(img, (3,3))

        cv2.namedWindow('real image')
        cv.SetMouseCallback('real image', on_mouse, 0)
        cv2.imshow('real image', img)

        if count < 50:
            if cv2.waitKey(33) == 27:
                cv2.destroyAllWindows()
                break
        elif count >= 50:
            if cv2.waitKey(0) == 27:
                cv2.destroyAllWindows()
                break
            count = 0

class App:
    def __init__(self, window, image_path):
        self.window = window
        window.title("Display Area")
        window.configure(background='grey')

        #image display area
        img = self.load_image(image_path, (800, 600))

        canvas=tk.Canvas(self.window, height=600, width=800)
        canvas_image = canvas.create_image(0,0, image=img, anchor=tk.NW)

        canvas.image = img #if a reference is not kept of the image, it will be garbage collected out of existence.
        canvas.pack(side='bottom', fill='both', expand='yes')

        self.window.bind('<Motion>', self.motion)

    def motion(self, event):
        """ Example Tk event. This will likely end up being mouse click detection
            that will go on to be used in drawing rectangles on the loaded image.
        """
        x, y = event.x, event.y
        print str(x) + " : " + str(y)

    def load_image(self, filepath, dimensions):
        """ From given filepath, load and resize an image from
            the given path string.
            Return a TkPhoto object to be used in the Tkinter window.
        """
        #gotta give a resize tuple.
        #this is mainly so simplify displaying and drawing lines on the display canvas
        if not dimensions:
            raise Exception("Must provide height and width as tuple")
        #load image through open cv library. it isnt needed right now,
        #but going forward this could be useful as an example on converting from cv2
        loaded_image = cv2.imread(filepath, cv2.IMREAD_COLOR)

        # the color channels need to be shuffled around due to differences between cv2 and tk
        b,g,r = cv2.split(loaded_image)
        shuffled_image =cv2.merge((r,g,b))

        img = Image.fromarray(shuffled_image)
        img = img.resize(dimensions, Image.ANTIALIAS)

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
