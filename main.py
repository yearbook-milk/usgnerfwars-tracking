print("Starting up...")
import cv2
import numpy as np
import color_track_return_rectangle as ct2r
import helpers

# set up webcam acs
device = 0
latch = True
polygons = []

if device == None: device = int(input("--Which device (enter an int)? "))

cap = cv2.VideoCapture(device)
if not cap.isOpened():
    println("--Webcam entry point failed to initialize!")
    exit(-1)


# set up tracker with default parameters
ct2r._init(lhs = 20, lha = 20, lss = 75, lblur = 15, lminPolygonWidth = 50, lminPolygonHeight = 50)

only_draw_biggest_polygon = True

lock = "SCAN"
the_tracker = None

rescan_on_lockbreak = True
failed_tracks = 0
failed_tracks_thresh = 100


# onlock handler
def onclick(event, x, y, *argv):
    pass
    
# set up output windows
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

        # get polygons back out of the detection method if we are scanning
        polygons, output = ct2r._attempt_detection(camera_input, {"colormasks":
            [
                {"colormask_upper": ct2r.colors["upper_dark_blue"], "colormask_lower": ct2r.colors["lower_dark_blue"]},
                {"colormask_upper": ct2r.colors["upper_light_blue"], "colormask_lower": ct2r.colors["lower_light_blue"]},
                {"colormask_upper": ct2r.colors["upper_green"], "colormask_lower": ct2r.colors["lower_green"]},
            ]
        })
            
        if (lock == "SCAN"):

            if not only_draw_biggest_polygon:
                indice = 0
                for i in polygons:
                    x, y, w, h = i
                    cv2.rectangle(camera_input, (x,y), (x+w,y+h), (255, 255, 0), 2)
                    cv2.putText(
                        camera_input,
                        "detection#"+str(indice),
                        (x, y-10),
                        cv2.FONT_HERSHEY_DUPLEX,
                        0.50,
                        (255,255,0)
                    )
                    indice += 1
                    # if all polygons that were able to be produced are to be drawn, draw in cyan
            else:
                largestPolygon = (-1, -1, -1, -1)
                for i in polygons:
                    x, y, w, h = i
                    if (w > largestPolygon[2] and h > largestPolygon[3]):
                        largestPolygon = (x, y, w, h)
                x, y, w, h = largestPolygon
                polygons = [largestPolygon]
                cv2.rectangle(camera_input, (x,y), (x+w,y+h), (255, 0, 0), 2)
                cv2.putText(
                        camera_input,
                        "sole detection#"+str(0),
                        (x, y-10),
                        cv2.FONT_HERSHEY_DUPLEX,
                        0.50,
                        (255,255,0)
                )
                # if only the largest polygon is being drawn, draw in blue
        elif (lock == "LOCK"):
            if (the_tracker == None):
                lock == "SCAN"
                
            success, box = the_tracker.update(camera_input)
            if (success):
                cv2.rectangle(camera_input, box, (0, 255, 255), 2)
                # if the polygon is being tracked, draw in yellow
                failed_tracks = 0
            elif (not success) and (rescan_on_lockbreak):
                failed_tracks += 1

            if (failed_tracks >= failed_tracks_thresh):
                the_tracker = None
                lock = "SCAN"
                failed_tracks = 0
            
           
       # list FPS
        fps = int(cv2.getTickFrequency() / (cv2.getTickCount() - timer))
        cv2.putText(
            camera_input,
            " fps:" + str(fps)
            +" mode:" + str(lock)
            +f" release:{failed_tracks}/{failed_tracks_thresh}",
            (5,35),
            cv2.FONT_HERSHEY_DUPLEX,
            0.50,
            (255,255,0)
        )
                
            
        
        cv2.imshow("output", camera_input)
        
    # waitKey so the program doesn't crash
    # press Q to quit
    kb = cv2.waitKey(1)
    if (kb == ord("q")):
        latch = False
    if (48 <= kb <= 57):
        the_tracker = cv2.TrackerKCF_create()
        the_tracker.init(camera_input, polygons[kb - 48])
        lock = "LOCK"
        failed_tracks = 0
    if (kb == ord("f")):
        the_tracker = None
        lock = "SCAN"
        failed_tracks = 0
    
    
# release resources when done
cv2.destroyAllWindows()
cap.release()
