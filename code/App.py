import sys, os
import Tkinter as tk
import threading
import PIL.Image
import CustomizedInterfaceElements as ui
from ParkingLot import *
import ImageTk


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
        app = SetupApp(self.parent, "resources/Parking-Lot.jpg", ParkingLot())

    def start_monitor(self):
        self.destroy()
        app = MonitorApp(self.parent, "resources/Parking-Lot.jpg", ParkingLot())


class SetupApp(tk.Frame):
    def __init__(self, parent, image_path, PKLot):
        self.parent = parent
        self.parkinglot = PKLot
        self.image_path = image_path

        tk.Frame.__init__(self, master=self.parent)

        self.winfo_toplevel().title('Setup')
        self.winfo_toplevel().configure(background='grey')

        self.canvas = ui.CanvasArea(self, self.parkinglot, image_path)
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

        # bind events
        self.parent.bind('c', self.window_exit)
        self.update_all()  # this kicks off the main root calling updates ever 100 ms

        self.pack()

    def update_lot(self):
        # there is absolutely no way this works as intended on first run. i refuse to believe it.
        # there is a secret race condition or something will be corrupted or something.
        # but it leaves the UI running while everything is going on, soooooooo.....

        # was worried about stray threads piling up, but threading.enumerate seems to show that things clean up after
        # themselves.

        if threading.activeCount() > 1:
            print 'Warning: Images have not finished processing from the last iteration'
            pass
        else:
            threading.Thread(target=self.parkinglot.update, args=[self.image_path]).start()

    def delete_selection(self):
        self.parkinglot.removeSpot(self.parkingspot_listbox.get_selection_id())

    def window_exit(self, event=None):
        self.parent.destroy()

    def return_roleselect(self):
        self.destroy()
        app=RoleSelect(self.parent)

    def update_all(self, event=None):
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
        self.menubar.delete(1)


if __name__ == "__main__":
    try:
        import caffe
    except ImportError:
        print "Warning: Could not locate installed Caffe, images will not be analyzed."

    root = tk.Tk()
    root.resizable(0, 0)
    
    if len(sys.argv) == 1 or sys.argv[1] == 'role':
        app = RoleSelect(root)
    elif sys.argv[1] == 'imtest':
        pklot = ParkingLot()
        pklot.loadXML('testxml.xml')

        imp = ImageProcessor('model_8.tar.gz', pklot)
        imp.get_results('Parking-Lot.jpg')

        os.sys.exit(0)

    else:
        app = RoleSelect(root)
        
    root.mainloop()
