#got rid of msvcrt. it is Windows specific and cant work on ubuntu anyways
import cv2
import numpy as np

hasDown = False;
rectangle_points = []

def mouseEvents(event, x , y, flags, params):
    global hasDown, img
    global rectangle_points

    if(event == cv2.EVENT_LBUTTONDOWN):
        hasDown=True

    if(event == cv2.EVENT_MOUSEMOVE and hasDown):
        #while the mouse is held, every time it moves add a reference point for
        #the rectangle that will be drawn at the end
        rectangle_points.append((x, y))
        cv2.circle(img, (x,y), 2, (0,255,0)) #draw circle for visual reference

    if(event== cv2.EVENT_LBUTTONUP):
        hasDown = False
        #draw rectangle
        n_array = np.array(rectangle_points) #convert list of points to array
        rectangle = cv2.minAreaRect(n_array) #find points and angle of rect
        box = cv2.cv.BoxPoints(rectangle) #convert to proper coordinate points
        box = np.int0(box) #some numpy nonsense. required to work, dunno what it does though

        cv2.drawContours(img, [box], 0, (0,255,0), 2) #draw lines based on box
        rectangle_points = [] #reset list to use for the next rectangle


img = cv2.imread('Parking-Lot.jpg')
cv2.namedWindow('image')
cv2.setMouseCallback('image', mouseEvents)

Running = True
while Running:
    cv2.imshow('image', img)

    key = cv2.waitKey(1) & 0xFF
    if key == ord('c'):
        print('escape')
        cv2.destroyAllWindows()
        Running = False
