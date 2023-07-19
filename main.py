print("Starting up...")
import cv2
import numpy as np
import color_track_return_rectangle as ct2r
import helpers

device = 0
latch = True
detections = []

if device == None: device = int(input("--Which device (enter an int)? "))

cap = cv2.VideoCapture(device)
if not cap.isOpened():
    println("--Webcam entry point failed to initialize!")
    exit(-1)


def onclick(event, x, y, *argv):
    pass
    
    
cv2.namedWindow("input")
cv2.namedWindow("output")
cv2.setMouseCallback("input", onclick)

print("Ready!")

while latch:
    timer = cv2.getTickCount()
    ret, camera_input = cap.read()
    if (ret):
        camera_input = helpers.increase_brightness(camera_input, value=10)
        cv2.imshow("input", camera_input)
        
        # get polygons back out of the tracking methods
        camera_input = ct2r._attempt_detection(camera_input, {"colormasks":
        [
            {"colormask_upper": ct2r.colors["upper_dark_blue"], "colormask_lower": ct2r.colors["lower_dark_blue"]},
            {"colormask_upper": ct2r.colors["upper_light_blue"], "colormask_lower": ct2r.colors["lower_light_blue"]},
            {"colormask_upper": ct2r.colors["upper_cyan"], "colormask_lower": ct2r.colors["lower_cyan"]},
            
        ]
        })
        
        cv2.imshow("output", camera_input)
        
    # waitKey so the program doesn't crash
    # press Q to quit
    kb = cv2.waitKey(1)
    if (kb == ord("q")):
        latch = False
    
    
# release resources when done
cv2.destroyAllWindows()
cap.release()