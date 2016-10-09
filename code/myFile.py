import msvcrt
import cv2
import numpy

hasDown = False;
escape = False; 
x1 = 0;
x2 = 0;
y1 = 0;
y2 = 0;
def mouseEvents(event, x , y, flags, params):
    global hasDown
    global x1
    global x2
    global y1
    global y2
    global img
    if(event == cv2.EVENT_LBUTTONDOWN):
        hasDown=True
        x1 = x;
        y1= y;
        print("Mouse position x:" + str(x)+ " y: " + str(y))
    elif(event== cv2.EVENT_LBUTTONUP):
        print("Mouse position ending x: " + str(x) + " y: " + str(y))
        if(hasDown==True):
            x2 = x;
            y2 = y;
            cv2.rectangle(img,(x1,y1),(x2,y2),(0,255,0), 2)
            
            
        

img = cv2.imread('parkinglot.jpg', 0)
cv2.namedWindow('image', cv2.WINDOW_NORMAL)
cv2.setMouseCallback('image', mouseEvents)

while True:
    cv2.imshow('image', img)
    cv2.waitKey(0)
    if msvcrt.kbhit() and msvcrt.getch() == chr(27).encode():
        print('escape')
        cv2.destroyAllWindows()
        break;
    
