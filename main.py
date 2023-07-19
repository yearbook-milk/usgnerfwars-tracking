print("Starting up...")
import cv2
import numpy as np

device = 0
latch = True
color_bottom = 0
color_top = 0
camera_input = 0
camera_input_hsv = 0

if device == None: device = int(input("--Which device (enter an int)? "))

cap = cv2.VideoCapture(device)
if not cap.isOpened():
    println("--Webcam entry point failed to initialize!")
    exit(-1)


def onclick(event, x, y, *argv):
    global camera_input_hsv, color_bottom, color_top
    print("Selected pixel: "+ str(camera_input_hsv[y,x]) )
    color_bottom = camera_input_hsv[y,x][0] - 5
    color_top    = camera_input_hsv[y,x][0] + 5
    
    
cv2.namedWindow("input")
cv2.namedWindow("output")
cv2.setMouseCallback("input", onclick)

print("Ready!")

while latch:
    timer = cv2.getTickCount()
    ret, camera_input = cap.read()
    if (ret):
        cv2.imshow("input", camera_input)
        
        # apply a color mask
        camera_input_hsv = cv2.cvtColor(camera_input, cv2.COLOR_BGR2HSV)
        lower_bound = np.array([color_bottom,50,50])
        upper_bound = np.array([color_top,255,255])
        mask = cv2.inRange(camera_input_hsv, lower_bound, upper_bound)
        camera_input = cv2.bitwise_and(camera_input,camera_input, mask=mask)

        
        cv2.imshow("output", camera_input)
        
    # waitKey so the program doesn't crash
    # press Q to quit
    kb = cv2.waitKey(1)
    if (kb == ord("q")):
        latch = False
    
    
# release resources when done
cv2.destroyAllWindows()
cap.release()