import cv2
import numpy as np
import config
# Create a VideoCapture object
import time
import traceback


cap = cv2.VideoCapture(config.sourc3)

# Check if camera opened successfully
if (cap.isOpened() == False):
    print("Unable to read camera feed")

# Default resolutions of the frame are obtained.The default resolutions are system dependent.
# We convert the resolutions from float to integer.
frame_width = 480  # int(cap.get(3))
frame_height = 320  # int(cap.get(4))

# Define the codec and create VideoWriter object.The output is stored in 'outpy.avi' file.
try:
    out = cv2.VideoWriter('outpy.avi', cv2.VideoWriter_fourcc('M', 'J', 'P', 'G'), 10, (frame_width, frame_height))
except:
    traceback.print_exc()
i = 0
while (True):
    i += 1
    ret, frame = cap.read()
    frame = cv2.resize(frame, (480, 320))
    if ret == True:
        # Write the frame into the file 'output.avi'
        try:
            out.write(frame)
        except:
            traceback.print_exc()
            break

# When everything done, release the video capture and video write objects
cap.release()
out.release()


cv2.destroyAllWindows() 