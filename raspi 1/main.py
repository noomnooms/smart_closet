#import libraries
import http.client, urllib
import json
import requests
import socket
import os
import sys
from datetime import datetime
import subprocess
import face_recognition
import shutil
import time
import tkinter as tk
import tkinter.scrolledtext as scrtxt
from tkinter import *
import tkinter.font as font

font_name = "SF Pro Text"

deviceId = 'DfgWZy7D'
deviceKey = '652euleCpyBGjLgq'

#---------------------------- MCS ----------------------------
def get_to_mcs():
    host = "http://api.mediatek.com"
    endpoint = "/mcs/v2/devices/" + deviceId + "/datachannels/ctrld1/datapoints"
    url = host + endpoint
    headers = {"Content-type": "application/json", "deviceKey": deviceKey}
    r = requests.get(url,headers=headers)
    value = (r.json()["dataChannels"][0]["dataPoints"][0]["values"]["value"])
    return value

def post_to_mcs(payload):
    headers = {"Content-type": "application/json", "deviceKey": deviceKey}
    not_connected = 1
    while (not_connected):
        try:
            conn = http.client.HTTPConnection("api.mediatek.com:80")
            conn.connect()
            not_connected = 0
        except (http.client.HTTPException, socket.error) as ex:
            print ("Error: %s" % ex)
            time.sleep(10) # sleep 10 seconds
    conn.request("POST", "/mcs/v2/devices/" + deviceId + "/datapoints",
    json.dumps(payload), headers)
    response = conn.getresponse()
    print( response.status, response.reason, json.dumps(payload),time.strftime("%c"))
    data = response.read()
    conn.close()

#---------------------------- Settings GUI ----------------------------
class MainApp(tk.Tk):
    def __init__(self, *args, **kwargs):
        tk.Tk.__init__(self, *args, **kwargs)
        container = tk.Frame(self)
        container.pack(side="top", fill="both", expand = True)
        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)

        self.frames = {}

        for F in (Opening, DeletePage, DeleteDone, AddFace, Face_warning, Instruction, EncodingProgress, AddDone):
            frame = F(container, self)
            self.frames[F] = frame
            frame.grid(row=0, column=0, sticky="nsew")

        self.show_frame(Opening)

    def show_frame(self, cont):
        frame = self.frames[cont]
        frame.tkraise()

class Opening(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self,parent)
        label = tk.Label(self, text="Hello! What do you want to today?", font=(font_name,15, 'bold'))
        label.place(relx = 0.5, rely = 0.3, anchor = 'center')

        button = tk.Button(self, text="Add new face", font=(font_name, 10), width=15, height=2, command=lambda: controller.show_frame(AddFace))
        button.place(relx = 0.2, rely = 0.6, anchor = 'center')

        button = tk.Button(self, text="Delete face", font=(font_name, 10), width=15, height=2, command=lambda: controller.show_frame(DeletePage))
        button.place(relx = 0.5, rely = 0.6, anchor = 'center')

        button = tk.Button(self, text="Quit", font=(font_name, 10), width=15, height=2, command=lambda: controller.destroy())
        button.place(relx = 0.8, rely = 0.6, anchor = 'center')     

class DeletePage(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self,parent)
        label = tk.Label(self, text="Which one do you want to delete?", font=(font_name, 12, 'bold'))
        label.place(relx = 0.5, rely = 0.2, anchor = 'center')

        tkvar = StringVar()
        
        #list of names
        choices = []
        directory = './dataset'
        for root, subdirectories, files in os.walk(directory):
            for subdirectory in subdirectories:
                choices.append(subdirectory)
        tkvar.set(choices[0])
        popupMenu = tk.OptionMenu(self, tkvar, *choices)
        popupMenu.config(font=(font_name, 12), width=20, height=1)
        popupMenu.place(relx = 0.5, rely = 0.4, anchor = 'center')

        value = ""
        #on change dropdown value
        def get_value(*args):
            value = tkvar.get()
            #delete face
            path = directory+'/'+value
            shutil.rmtree(path)
            instruction = "python3 encode_faces.py --dataset dataset --encodings encodings.pickle --detection-method hog"
            os.system(instruction)
            controller.show_frame(DeleteDone)

        button = tk.Button(self, text="Confirm", font=(font_name, 10), width=15, height=1, command=get_value)
        button.place(relx = 0.375, rely = 0.6, anchor = 'center')
        button = tk.Button(self, text="Cancel", font=(font_name, 10), width=15, height=1, command=lambda: controller.show_frame(Opening))
        button.place(relx = 0.625, rely = 0.6, anchor = 'center')

class DeleteDone(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self,parent)
        label = tk.Label(self, text="Face succesfully deleted!", font=(font_name, 12, 'bold'))
        label.place(relx = 0.5, rely = 0.4, anchor = 'center')

        button = tk.Button(self, text="OK", font=(font_name, 10), width=15, height=2, command=lambda: controller.destroy())
        button.place(relx = 0.5, rely = 0.6, anchor = 'center')

class newface:
    value = ''
    
class AddFace(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self,parent)
        label = tk.Label(self, text="Nice to meet you!", font=(font_name, 12, 'bold'))
        label.place(relx = 0.5, rely = 0.2, anchor = 'center')
        label = tk.Label(self, text="Tell me your name:", font=(font_name, 12))
        label.place(relx = 0.5, rely = 0.4, anchor = 'center')
        

        def Submit():
            newface.value = name.get()
            
            #check if name is taken
            name_list = [] 
            directory = './dataset'
            for root, subdirectories, files in os.walk(directory):
                for subdirectory in subdirectories:
                    name_list.append(subdirectory)
            if newface.value in name_list:
                controller.show_frame(Face_warning)
            else:
                path = "./dataset/"+newface.value
                os.mkdir(path)
                controller.show_frame(Instruction)

        name = tk.Entry(self, font=(font_name, 10), width=25)
        name.place(relx = 0.5, rely = 0.5, anchor = 'center')

        button = tk.Button(self, text="Confirm", font=(font_name, 10), width=12, height=1, command=Submit)
        button.place(relx = 0.390, rely = 0.65, anchor = 'center')

        button = tk.Button(self, text="Cancel", font=(font_name, 10), width=12, height=1, command=lambda: controller.show_frame(Opening))
        button.place(relx = 0.610, rely = 0.65, anchor = 'center')

class Face_warning(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self,parent)
        label = tk.Label(self, text="Name already taken, try again!", font=(font_name, 13, 'bold'))
        label.place(relx = 0.5, rely = 0.4, anchor = 'center')

        button = tk.Button(self, text="OK", font=(font_name, 10), width=15, height=2, command=lambda: controller.show_frame(AddFace))
        button.place(relx = 0.5, rely = 0.6, anchor = 'center')

class Instruction(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self,parent)
        label = tk.Label(self, text="Instructions:", font=(font_name, 13, 'bold'))
        label.place(relx = 0.5, rely = 0.3, anchor = 'center')
        label = tk.Label(self, text="Press 'k' to capture. Press 'q' to quit.", font=(font_name, 12))
        label.place(relx = 0.5, rely = 0.4, anchor = 'center')

        def Submit():
            #---------BUILD FACE DATASET HERE----------
            instruction = "python3 build_face_dataset.py --cascade haarcascade_frontalface_default.xml --output dataset/"+newface.value+""
            os.system(instruction)
            #---------Face dataset done-----
            controller.show_frame(EncodingProgress)

        button = tk.Button(self, text="OK", font=(font_name, 10), width=15, height=1, command=Submit)
        button.place(relx = 0.5, rely = 0.6, anchor = 'center')

class EncodingProgress(tk.Frame):
     def __init__(self, parent, controller):
        tk.Frame.__init__(self,parent)
        label = tk.Label(self, text="Encoding faces..", font=(font_name, 13, 'bold'))
        label.place(relx = 0.5, rely = 0.3, anchor = 'center')
        
        def Submit():
            instruction = "python3 encode_faces.py --dataset dataset --encodings encodings.pickle --detection-method hog"
            os.system(instruction)
            controller.show_frame(AddDone)
            
        button = tk.Button(self, text="Start Encoding", font=(font_name, 10), width=15, height=1, command=Submit)
        button.place(relx = 0.5, rely = 0.6, anchor = 'center')

class AddDone(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self,parent)
        label = tk.Label(self, text="New face succesfully added!", font=(font_name, 13, 'bold'))
        label.place(relx = 0.5, rely = 0.4, anchor = 'center')

        button = tk.Button(self, text="OK", font=(font_name, 10), width=15, height=1, command=lambda: controller.destroy())
        button.place(relx = 0.5, rely = 0.6, anchor = 'center')
#------------------------------------------------------------------------------------------

if __name__ == '__main__':
    while True: #main loop
        while True: #wait idly until receive signal
            a = get_to_mcs()
            a = int(a)
            if(a==0):
                print("waiting for signal.")
            elif (a==1):  #infrared detects motion
                print("turning camera on.")
                break
            elif (a==2): #button is pressed, either input/delete face
                print("Opening settings.")
                break
            time.sleep(1)
        if(a==1): #face recognition to open door
            face_recog = str(subprocess.check_output([sys.executable, "face_recog.py", "--cascade", "haarcascade_frontalface_default.xml", "--encodings", "encodings.pickle", "--output", "intruder"]))
            value = int(face_recog[2])
            if(value):
                #open door
                payload = {"datapoints":[{"dataChnId":"move_servo","values":{"value":str(1)}}]}
                post_to_mcs(payload)
            if(not value):
                print("Intruder detected.")
                payload = {"datapoints":[{"dataChnId":"move_servo","values":{"value":str(0)}}]}
                post_to_mcs(payload)
            
            time.sleep(15) #automatically close door after 15 seconds
            payload = {"datapoints":[{"dataChnId":"move_servo","values":{"value":str(0)}}]}
            post_to_mcs(payload)
        elif(a==2): #input/delete face
            app = MainApp()
            app.title('Settings')
            app.geometry('500x200+300+300')
            app.mainloop()
        time.sleep(5)
