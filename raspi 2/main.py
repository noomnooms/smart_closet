import time
import http.client, urllib
import json
import RPi.GPIO as GPIO
import requests
import socket

GPIO.setmode(GPIO.BOARD)
GPIO.setwarnings(False)

deviceId = 'DfgWZy7D'
deviceKey = '652euleCpyBGjLgq'

servoPIN = 37
IR_PIN = 40
button_PIN = 10

GPIO.setmode(GPIO.BOARD)
GPIO.setup(servoPIN, GPIO.OUT)
p = GPIO.PWM(servoPIN,20) #GPIO17 with 50Hz
p.start(0)
GPIO.setup(button_PIN, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)

def senseIR(pin):
    s = 0
    GPIO.setup(pin,GPIO.IN)
     
    if GPIO.input(pin):
        time.sleep(0.5)
    else:
        s=1
        time.sleep(0.5)
        return s

def button_push():
    if(GPIO.input(10)==GPIO.HIGH):
        return 1
    else:
        return 0
    
def moveServo(angle): #move servo into determined angle
    try:
        #while True:
        p.ChangeDutyCycle(2+(angle/18))
        time.sleep(0.25)
    except: #KeyboardInterrupt:
        p.stop()
        GPIO.cleanup()

# Set MediaTek Cloud Sandbox (MCS) Connection
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

#receive signal from MCS
def get_to_mcs():
    host = "http://api.mediatek.com"
    endpoint = "/mcs/v2/devices/" + deviceId + "/datachannels/servo/datapoints"
    url = host + endpoint
    headers = {"Content-type": "application/json", "deviceKey": deviceKey}
    r = requests.get(url,headers=headers)
    value = (r.json()["dataChannels"][0]["dataPoints"][0]["values"]["value"])
    return value

if __name__ == "__main__":
    while True:
        payload = {"datapoints":[{"dataChnId":"ctrl1","values":{"value":str(0)}}]}
        post_to_mcs(payload)
        moveServo(0) #start by making sure the door is closed at each loop
        try:
            sense = 0
            push = 0
            while True:
                sense = senseIR(IR_PIN)
                push = button_push()
                if(sense or push):
                    break
            
            if(push):
                payload = {"datapoints":[{"dataChnId":"ctrl1","values":{"value":str(2)}}]}
                post_to_mcs(payload)
                time.sleep(10)
                continue 
            elif(sense and not push):
                payload = {"datapoints":[{"dataChnId":"ctrl1","values":{"value":str(1)}}]}
                post_to_mcs(payload)
                time.sleep(20)
                a = get_to_mcs()
                if a==1:
                    print('opening door.')
                    moveServo(90)
                    time.sleep(0.5)
                if a==0:
                    print("closing door.")
                    moveServo(0)
                    time.sleep(0.5)
                time.sleep(10)
        except KeyboardInterrupt:
            print('quit')
            GPIO.cleanup()
            exit()
                