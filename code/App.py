import random
import sys, os, shutil
import Tkinter as tk
import tkFileDialog
import threading
import PIL.Image
import CustomizedInterfaceElements as ui
from ParkingLot import *
from PIL import ImageTk

import time
import datetime

class RoleSelect(tk.Frame):
    def __init__(self, parent):
        self.parent = parent
        tk.Frame.__init__(self, master=self.parent)

        # add a label with the project logo
        # separate operations on loading the image because anti aliasing didn't work otherwise
        pilimage = PIL.Image.open('resources/Logo-WhiteBG.png')
        resized = pilimage.resize([784, 412], PIL.Image.ANTIALIAS)
        self.img = ImageTk.PhotoImage(resized)
        self.panel = tk.Label(self, image=self.img)
        self.panel.pack(side=tk.TOP, fill='both')

        self.selectSetupButton = tk.Button(self, text="Open Operator", command=self.start_setup)
        self.selectMonitorButton = tk.Button(self, text="Open Monitor", command=self.start_monitor)
        self.selectSetupButton.pack(side=tk.RIGHT)
        self.selectMonitorButton.pack(side=tk.RIGHT)

        self.pack()

    def start_setup(self):
        self.destroy()
        app = SetupApp(self.parent, "resources/init.jpg", ParkingLot())

    def start_monitor(self):
        self.destroy()
        app = MonitorApp(self.parent, "resources/init.jpg", ParkingLot())


class SetupApp(tk.Frame):
    def __init__(self, parent, image_path, PKLot):
        self.parent = parent
        self.parkinglot = PKLot
        self.cv2_img = cv2.imread(image_path)

        tk.Frame.__init__(self, master=self.parent)

        self.winfo_toplevel().title('Setup')
        self.winfo_toplevel().configure(background='grey')

        self.canvas = ui.CanvasArea(self, self.parkinglot, self.cv2_img)
        self.canvas.grid(row=0, column=0, sticky=tk.N)

        # Parking Spot List
        # currently an issue with scrolling on the list. it will scroll and then immediately be set back to to 0.
        self.parkingspot_listbox = ui.SpotList(self, self.parkinglot, width=20, height=34)
        self.parkingspot_listbox.grid(row=0, column=1, rowspan=3, sticky='N')

        # MenuBar
        self.menubar = ui.MenuBar(self)
        self.parent.configure(menu=self.menubar)

        # Image Processor/Parking lot update
        self.lotupdate_button = tk.Button(self, text='Update Lot', command=self.update_lot)
        self.lotupdate_button.grid(row=5, column=1, sticky='E')

        # delete spot button
        self.deleteSpotButton = tk.Button(self, text='Delete Selected', command=self.delete_selection)
        self.deleteSpotButton.grid(row=8, column=1, sticky='E')

        #single image load Button
        self.loadImageButton = tk.Button(self, text="load image", command=self.manual_set_image)
        self.loadImageButton.grid(row=9, column=1, sticky='E')

        #toggle update button
        self.toggleUpdateButton = tk.Button(self, text="toggle update", command=self.update_toggle)
        self.toggleUpdateButton.grid(row=10, column=1, sticky='E')

        # bind events
        self.parent.bind('c', self.window_exit)

        self.pack()

        self.timestamp = time.time()

        self.update_toggle_bool = False

        self.image_source_directory = os.getcwd() + "/resources/lot_images/"
        self.img_origin_directory = os.getcwd() + '/resources/source_images/'

        t = threading.Thread(target=image_swapper, args=[self.img_origin_directory, self.image_source_directory])
        t.daemon = True
        t.start()


        self.update_all()  # this kicks off the main root calling updates ever 100 ms

    def manual_set_image(self, events=None):
        filename = tkFileDialog.askopenfilename(parent=self.parent)
        if filename is not None:
            try:
                self.parkinglot.currentLotImage = cv2.imread(filename)
                self.canvas.update_image(self.parkinglot.currentLotImage)
            except (SyntaxError, AttributeError) as e:
                print "Improper File"
                print filename
                pass
        else:
            pass

    def update_lot(self):
        # there is absolutely no way this works as intended on first run. i refuse to believe it.
        # there is a secret race condition or something will be corrupted or something.
        # but it leaves the UI running while everything is going on, soooooooo.....

        # was worried about stray threads piling up, but threading.enumerate seems to show that things clean up after
        # themselves.

        #self.parkinglot.update()

        if threading.activeCount() > 2:
            print 'Warning: Images have not finished processing from the last iteration'
            pass
        else:
            threading.Thread(target=self.parkinglot.update, args=[]).start()

    def delete_selection(self):
        self.parkinglot.removeSpot(self.parkingspot_listbox.get_selection_id())

    def window_exit(self, event=None):
        self.parent.destroy()

    def return_roleselect(self):
        self.destroy()
        app=RoleSelect(self.parent)

    def update_toggle(self):
        self.update_toggle_bool = not self.update_toggle_bool

    def update_current_image(self):
        # take the image, or the first, image from the image_source_directory.
        # currently going to try just deleting the image when done with it.

        # this function relies on something else in the background supplying images.
        # so perhaps a separate thread populating the directory with an endless cycle of images.
        # (as a place holder for an actual camera system)

        # so when function call, set the image to the image in the directory.
        # then, update the parking lot image path
        # then, update the canvas.

        image = os.listdir(self.image_source_directory)
        if image:
            image = image[0]
            self.parkinglot.currentLotImage = cv2.imread(self.image_source_directory + image)
            self.canvas.update_image(self.parkinglot.currentLotImage)
            os.remove(self.image_source_directory + image)
            print "Image " + image + " Removed"
            self.update_lot()


        #images = os.listdir(self.image_source_directory)
        #images.sort()
        #if images:
        #    if self.parkinglot.currentLotImage == 'resources/init.jpg':
        #        self.parkinglot.currentLotImage = self.image_source_directory + images[0]
        #        self.canvas.update_image()

        #    else:
        #        out_dir = 'resources/old_lot_images/' + str(datetime.datetime.fromtimestamp(time.time())).split('.')[0].replace(':', '_') + '.jpg'
        #        os.rename(self.parkinglot.currentLotImage, out_dir)
        #        # repetitive. the way i handle the initial image removes the new image before it gets processed.
        #        # im tired and the only way i can think to fix it easily is to just rebuild the list here.
        #        # definitely not a good way to handle it though.
        #        images = os.listdir(self.image_source_directory)
        #        if images:  # chance of the list being empty since removing files above.
        #            images.sort()

        #            self.parkinglot.currentLotImage = self.image_source_directory + images[0]
        #            self.canvas.parkinglot.currentLotImage = self.image_source_directory + images[0]
        #            self.canvas.update_image()

        #            print 'Update Image - ' + str(datetime.datetime.fromtimestamp(time.time())).split('.')[0]

        #else:
        #    print 'No Images Found - ' + str(datetime.datetime.fromtimestamp(time.time())).split('.')[0]

    def update_all(self, event=None):
        if time.time() - self.timestamp > 10 and self.update_toggle_bool:
            self.timestamp = time.time()
            self.update_current_image()
            #maybe might crash since im trying to delete images around when i call this
            self.update_lot()

        self.parkingspot_listbox.update_parkingspot_list()
        id_number = self.parkingspot_listbox.get_selection_id()

        try:  # try to set the highlighted spot, unless it doesnt exist
            self.canvas.highlightedSpot = self.parkinglot.getSingleSpot(id_number)
        except (IndexError, AttributeError) as e:
            pass

        self.canvas.update_all()
        self.parent.after(100, self.update_all)


class MonitorApp(SetupApp):
    # since this is just a version of SetupApp with functionality removed, then it can just inherit directly from it ez.
    def __init__(self, parent, imagePath, PKLot):
        SetupApp.__init__(self, parent, imagePath, PKLot)

        # remove the ability for users to draw things in monitor mode
        self.canvas.unbind('<B1-Motion>')
        self.canvas.unbind('<ButtonRelease-1>')

        # remove delete button
        self.deleteSpotButton.grid_forget()

        #remove save lot menuitem
        self.menubar.delete(2)


def image_swapper(source_directory, populate_directory):
    # Meant to run in separate thread. DO NOT run in main thread.
    while True:
        population_images = os.listdir(populate_directory)
        if not population_images:
            print population_images
            options = os.listdir(source_directory)
            choice = random.choice(options)
            shutil.copy(source_directory + choice, populate_directory + choice)
        time.sleep(1)


if __name__ == "__main__":
    try:
        import caffe
    except ImportError:
        print "Warning: Could not locate installed Caffe, images will not be analyzed."

    root = tk.Tk()
    root.resizable(0, 0)

    app = RoleSelect(root)

    root.mainloop()
