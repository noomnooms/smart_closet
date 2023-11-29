#python3 face_recog.py --cascade haarcascade_frontalface_default.xml --encodings encodings.pickle --output intruder

# import the necessary packages
from imutils.video import VideoStream
from imutils.video import FPS
from imutils import paths
import face_recognition
import argparse
import imutils
import pickle
import time
import cv2
import os
import sys
from datetime import datetime

def detect_face():
    captured = False
    # construct the argument parser and parse the arguments
    ap = argparse.ArgumentParser()
    ap.add_argument("-c", "--cascade", required=True,
        help = "path to where the face cascade resides")
    ap.add_argument("-e", "--encodings", required=True,
        help="path to serialized db of facial encodings")
    ap.add_argument("-o", "--output", required=True)
    args = vars(ap.parse_args())

    #load known faces and embeddings
    data = pickle.loads(open(args["encodings"], "rb").read())
    #load OpenCV's Haar cascade for face detection
    detector = cv2.CascadeClassifier(args["cascade"])

    timeout = time.time() + 8 #set timeout as 8 seconds
    vs = VideoStream(usePiCamera=True).start() #initialize the video stream
    time.sleep(2.0) #allow camera sensor to warm up

    # start the FPS counter
    fps = FPS().start()

    name = ''
    dt_string=''
    # loop over frames from the video file stream
    while True:
         frame = vs.read() #grab frame from the threaded video stream
        orig = frame.copy() #clone the frame
        frame = imutils.resize(frame, width=500) #resize frame

        #convert input frame
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY) #BGR -> grayscale
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB) #BGR -> RGB

        # detect faces in the grayscale frame
        rects = detector.detectMultiScale(gray, scaleFactor=1.1, 
            minNeighbors=5, minSize=(30, 30),
            flags=cv2.CASCADE_SCALE_IMAGE)

        #detect faces in the grayscale frame
        rects = detector.detectMultiScale(gray, scaleFactor=1.1, 
            minNeighbors=5, minSize=(30, 30),
            flags=cv2.CASCADE_SCALE_IMAGE)

        boxes = [(y, x + w, y + h, x) for (x, y, w, h) in rects]

        #compute the facial embeddings for each face bounding box
        encodings = face_recognition.face_encodings(rgb, boxes)
        names = []

         #loop over the facial embeddings
        for encoding in encodings:
            # attempt to match each face in the input image to known encodings
            matches = face_recognition.compare_faces(data["encodings"], encoding)
            name = "Unknown" #initialize as unknown

            #check to see if we have found a match
            if True in matches:
                #find index of all matched faces
                matchedIdxs = [i for (i, b) in enumerate(matches) if b] 

                #count total number of times each face was matched
                counts = {} 
                for i in matchedIdxs:
                    name = data["names"][i]
                    counts[name] = counts.get(name, 0) + 1

                #determine the recognized face with the largest number by largest number of votes
                name = max(counts, key=counts.get)
            
            #update the list of names
            names.append(name)

            #capture face if face is unknown
            if(name == 'Unknown' and not captured):
                now = datetime.now()
                dt_string = now.strftime("%H:%M %B %d, %Y")               
                p = os.path.sep.join([args["output"], "{}.png".format(str(dt_string).zfill(5))])
                cv2.imwrite(p, orig)
                captured = True
            
        # loop over the recognized faces
        for ((top, right, bottom, left), name) in zip(boxes, names):
            # draw the predicted face name on the image
            cv2.rectangle(frame, (left, top), (right, bottom),
                (0, 255, 0), 2)
            y = top - 15 if top - 15 > 15 else top + 15
            cv2.putText(frame, name, (left, y), cv2.FONT_HERSHEY_SIMPLEX,
                0.75, (0, 255, 0), 2)

        # display the image to our screen
        cv2.imshow("Frame", frame)
        key = cv2.waitKey(1) & 0xFF

        # if the `q` key was pressed, break from the loop
        if key == ord("q") or time.time()>timeout:
            break

        # update the FPS counter
        fps.update()

    # stop the timer
    fps.stop()

    # do a bit of cleanup
    cv2.destroyAllWindows()
    vs.stop()
    return name, dt_string

if __name__ ==  '__main__':
    face, dt_string = detect_face()
    if face == 'Unknown': #unauthorized face
        address = "'./intruder/"+dt_string+".png'"
        #send warning message
        instruction = 'python3 line_notify.py "Intruder alert. Sending snapshot of intruder." --img_file '+address
        os.system(instruction)
        print(0) 
    elif face != 'Unknown':
        message = face+" has just entered the room!"
        #notify the name of who just entered the room
        instruction = 'python3 line_notify.py "'+message+'"' 
        os.system(instruction)
        print(1)