# import the necessary packages
from imutils.video import VideoStream
import argparse
import imutils
import time
import cv2
import os

# construct the argument parser and parse the arguments
ap = argparse.ArgumentParser()
ap.add_argument("-c", "--cascade", required=True,
    help = "path to where the face cascade resides")
ap.add_argument("-o", "--output", required=True,
    help="path to output directory")
args = vars(ap.parse_args())

# load OpenCV's Haar cascade for face detection from disk
detector = cv2.CascadeClassifier(args["cascade"])

print("[INFO] starting video stream...") 
vs = VideoStream(usePiCamera=True).start() #initialize the video stream
time.sleep(2.0) #allow the camera sensor to warm up
total = 0 #initialize the total number of faces

#loop over the frames from the video stream
while True:
    frame = vs.read() #grab frame from the threaded video stream
    orig = frame.copy() #clone the frame
    frame = imutils.resize(frame, width=400) #resize frame
 
    #detect faces in the grayscale frame
    rects = detector.detectMultiScale(cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY), scaleFactor=1.1, minNeighbors=5, minSize=(30, 30))
 
    #loop over the face detections and draw them on the frame
    for (x, y, w, h) in rects:
        cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
 
    #show the output frame
    cv2.imshow("Frame", frame)
    key = cv2.waitKey(1) & 0xFF
 
    #if the `k` key was pressed, save the frame to disk
    if key == ord("k"):
        p = os.path.sep.join([args["output"], "{}.png".format(
            str(total).zfill(5))])
        cv2.imwrite(p, orig)
        total += 1
    #if the `q` key was pressed, break from the loop
    elif key == ord("q"):
        break
 
#print the total faces saved and do a bit of cleanup
print("[INFO] {} face images stored".format(total))
print("[INFO] cleaning up...")
cv2.destroyAllWindows()
vs.stop()
