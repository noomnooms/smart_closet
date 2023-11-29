import RPi.GPIO as GPIO
import time
from Adafruit_CharLCD import Adafruit_CharLCD
from time import sleep, strftime
from datetime import datetime
import requests
import json
import http.client, urllib
import socket


deviceId = 'DfgWZy7D'
deviceKey = '652euleCpyBGjLgq'



# GPIO to LCD mapping
LCD_RS = 7 # Pi pin 26
LCD_E = 8 # Pi pin 24
LCD_D4 = 25 # Pi pin 22
LCD_D5 = 24 # Pi pin 18
LCD_D6 = 23 # Pi pin 16
LCD_D7 = 18 # Pi pin 12

# Device constants
LCD_CHR = True # Character mode
LCD_CMD = False # Command mode
LCD_CHARS = 16 # Characters per line (16 max)
LCD_LINE_1 = 0x80 # LCD memory location for 1st line
LCD_LINE_2 = 0xC0 # LCD memory location 2nd line

#OpenWeatherMap API
key = "6325267bebmsha681a6cca72656ap1eb2ffjsn082dba6593ec"
host = "community-open-weather-map.p.rapidapi.com"

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
    
def timenow():
	now = str(datetime.now())
	now_str = ""
	for i in range(len(now)):
		#if rem: break
		now_str += now[i]
		if now[i+1] == '.': break
	nowlist = now_str.split(now_str[10]) #split by space
	timefrag = nowlist[1].split(':') #fragment time into hrs, mins, secs
	hrs = timefrag[0]
	fctime = [] #forecast time

	for i in range(int(hrs)+1, int(hrs)+5):
		later = "{}:{}:{}".format(str(i),"00","00")
		fctime.append(later)

	return nowlist, timefrag

def get_current():
	url = "https://community-open-weather-map.p.rapidapi.com/weather"

	querystring = {"q":"Hsinchu,tw","lat":"24.7877929","lon":"120.9965016","lang":"null","units":"metric","mode":"json"}

	headers = {
	    'x-rapidapi-key': key,
	    'x-rapidapi-host': host
	    }

	response = requests.request("GET", url, headers=headers, params=querystring)

	#print(response.text)
	json_data = json.loads(response.text)

	#example response
	#response = {"coord":{"lon":120.9686,"lat":24.8036},"weather":[{"id":801,"main":"Clouds","description":"few clouds","icon":"02d"}],"base":"stations","main":{"temp":286.71,"feels_like":283.27,"temp_min":285.37,"temp_max":287.59,"pressure":1017,"humidity":60},"visibility":10000,"wind":{"speed":3.58,"deg":30,"gust":11.18},"clouds":{"all":19},"dt":1610269940,"sys":{"type":3,"id":205017,"country":"TW","sunrise":1610232139,"sunset":1610270661},"timezone":28800,"id":1675151,"name":"Hsinchu","cod":200}
	#print(json_data['main'])

	dtnow, curtimefrag = timenow()
	hrs, mins = (int(curtimefrag[0]), int(curtimefrag[1]))
	maintemp = json_data['main']
	#tempr = str(round(fc_maintemp['temp'])) + '°C'
	#feelslike = str(round(fc_maintemp['feels_like'])) + '°C'
	#windspd = str(round(json_data['wind']['speed'])) + ' m/s'
	tempr = round(maintemp['temp']) 
	feelslike = round(maintemp['feels_like'])
	windspd = round(json_data['wind']['speed']) 

	return tempr, feelslike, windspd


def get_forecast():
	url = "https://community-open-weather-map.p.rapidapi.com/forecast"

	querystring = {"q":"Hsinchu,tw","units":"metric","mode":"json","lat":"24.8036","lon":"120.9686","cnt":"20"}

	headers = {
	    'x-rapidapi-key': key,
	    'x-rapidapi-host': host
	    }

	#query to REST API
	response = requests.request("GET", url, headers=headers, params=querystring)

	json_data = json.loads(response.text)
	#print(response.text)
	dtnow, curtimefrag = timenow()
	curhrs = int(curtimefrag[0])

	idx = 0

	#extract index for several hours after current time
	for i in range(len(json_data['list'])):
		dt = json_data['list'][i]['dt']
		dt = int(dt)
		
		#print(nowlist)
		dt_str = datetime.utcfromtimestamp(dt).strftime('%Y-%m-%d %H:%M:%S')
		dt_list = dt_str.split(dt_str[10])
		#print(dt_list)
		timefrag = dt_list[1].split(':') #fragment time into hrs, mins, secs
		hrs = int(timefrag[0])+8
		#print(curhrs)
		if hrs in range(curhrs,curhrs+3):
			idx = i
			break

	data = json_data['list'][idx] #nanti ganti idx jd i, example jadi json_data
	dt = data['dt']
	dt = int(dt)
	dt_str = datetime.utcfromtimestamp(dt).strftime('%Y-%m-%d %H:%M:%S')
	dt_list = dt_str.split(dt_str[10])
	#print(dt_list)

	fc_maintemp = data['main']
	fc_tempr = round(fc_maintemp['temp'])
	fc_feelslike = round(fc_maintemp['feels_like']) 
	fc_windspd = round(data['wind']['speed'])

	return fc_tempr, fc_feelslike, fc_windspd 

	#print('date now', dt_str)


def get_to_dbio():

	url = "https://clothes-a7ad.restdb.io/rest/clothes"

	headers = {
	    'content-type': "application/json",
	    'x-apikey': "e9d41e865cfca1db8149878191c1384dc1eee",
	    'cache-control': "no-cache"
	    }

	response = requests.request("GET", url, headers=headers)

	print(response.text)

	return json.loads(response.text)

def setmain():
    it = 0 #variable for while loop
    curtemp, curfeels, curwind = get_current()
    fctemp, fcfeels, fcwind = get_forecast()
    
    db = get_to_dbio()
    
    summer = []
    winter = []
    for outfit in db:
        if outfit['category'] == 'summer':
            summer.append(outfit['name'])
        else:
            winter.append(outfit['name'])
    
    
    payload = {"datapoints":[{"dataChnId":"tempr","values":{"value":str(curtemp)}}]}
    post_to_mcs(payload)
    
    try:
        while it < 7: 
            nowlist,_ = timenow()
            lcd_text(nowlist[0],LCD_LINE_1)
            lcd_text(nowlist[1],LCD_LINE_2)
            time.sleep(3)
            
            
            lcd_text("Today's tempr.:",LCD_LINE_1)
            lcd_text(str(curtemp)+'°C',LCD_LINE_2)
            time.sleep(3)
            
            lcd_text("It feels like",LCD_LINE_1)
            lcd_text(str(curfeels)+'°C',LCD_LINE_2)
            time.sleep(3)
            
            if curtemp <= 18 and curwind <= 20:
                lcd_text("Today's cold!",LCD_LINE_1)
                lcd_text('But not windy..',LCD_LINE_2)
                time.sleep(3)
                for cl in winter:
                    lcd_text("Best to use:",LCD_LINE_1)
                    lcd_text(cl ,LCD_LINE_2)
                    time.sleep(2)
            elif curtemp >= 18 and curwind <= 20:
                lcd_text("Today's warm!",LCD_LINE_1)
                lcd_text('and not windy!',LCD_LINE_2)
                time.sleep(3)
                for cl in summer:
                    lcd_text("Best to use:",LCD_LINE_1)
                    lcd_text(cl ,LCD_LINE_2)
                    time.sleep(2)
            elif curtemp <= 18 and curwind >= 20:
                lcd_text("Today's cold!",LCD_LINE_1)
                lcd_text('And windy!',LCD_LINE_2)
                time.sleep(3)
                for cl in winter:
                    lcd_text("Best to use:",LCD_LINE_1)
                    lcd_text(cl ,LCD_LINE_2)
                    time.sleep(2)
                
            elif curtemp >= 15 and curwind >= 20:
                lcd_text("Hot",LCD_LINE_1)
                lcd_text('and windy..',LCD_LINE_2)
                time.sleep(3)
                for cl in summer:
                    lcd_text("Best to use:",LCD_LINE_1)
                    lcd_text(cl ,LCD_LINE_2)
                    time.sleep(2)
            lcd_text("Weather",LCD_LINE_1)
            lcd_text('forecast',LCD_LINE_2)
            time.sleep(3)
            lcd_text("For the ",LCD_LINE_1)
            lcd_text('next few hours',LCD_LINE_2)
            time.sleep(3)
            t1 = 'tempr: '+ str(fctemp) +'°C'
            t2 = 'windspeed: ' + str(fcwind) + ' m/s'
            lcd_text(t1,LCD_LINE_1)
            lcd_text(t2,LCD_LINE_2)
            time.sleep(3)
            it += 1
            print(it)
             
    except KeyboardInterrupt:
        lcd_text("Bye!",LCD_LINE_1)
        lcd_text("See you!",LCD_LINE_2)
        GPIO.cleanup()
        exit()
#main
def main(): #°
    GPIO.setwarnings(False)
    GPIO.setmode(GPIO.BCM) # Use BCM GPIO numbers
    GPIO.setup(LCD_E, GPIO.OUT) # Set GPIO's to output mode
    GPIO.setup(LCD_RS, GPIO.OUT)
    GPIO.setup(LCD_D4, GPIO.OUT)
    GPIO.setup(LCD_D5, GPIO.OUT)
    GPIO.setup(LCD_D6, GPIO.OUT)
    GPIO.setup(LCD_D7, GPIO.OUT)

    # Initialize display
    lcd_init()
        
    while True: #iterate 100 times and then update
    #get weather data
         setmain()
    
       

# Initialize and clear display
def lcd_init():
    lcd_write(0x33,LCD_CMD) # Initialize
    lcd_write(0x32,LCD_CMD) # Set to 4-bit mode
    lcd_write(0x06,LCD_CMD) # Cursor move direction
    lcd_write(0x0C,LCD_CMD) # Turn cursor off
    lcd_write(0x28,LCD_CMD) # 2 line display
    lcd_write(0x01,LCD_CMD) # Clear display
    time.sleep(0.0005) # Delay to allow commands to process

def lcd_write(bits, mode):
# High bits
    GPIO.output(LCD_RS, mode) # RS

    GPIO.output(LCD_D4, False)
    GPIO.output(LCD_D5, False)
    GPIO.output(LCD_D6, False)
    GPIO.output(LCD_D7, False)
    if bits&0x10==0x10:
        GPIO.output(LCD_D4, True)
    if bits&0x20==0x20:
        GPIO.output(LCD_D5, True)
    if bits&0x40==0x40:
        GPIO.output(LCD_D6, True)
    if bits&0x80==0x80:
        GPIO.output(LCD_D7, True)

    # Toggle 'Enable' pin
    lcd_toggle_enable()

    # Low bits
    GPIO.output(LCD_D4, False)
    GPIO.output(LCD_D5, False)
    GPIO.output(LCD_D6, False)
    GPIO.output(LCD_D7, False)
    if bits&0x01==0x01:
        GPIO.output(LCD_D4, True)
    if bits&0x02==0x02:
        GPIO.output(LCD_D5, True)
    if bits&0x04==0x04:
        GPIO.output(LCD_D6, True)
    if bits&0x08==0x08:
        GPIO.output(LCD_D7, True)

    # Toggle 'Enable' pin
    lcd_toggle_enable()

def lcd_toggle_enable():
    time.sleep(0.0005)
    GPIO.output(LCD_E, True)
    time.sleep(0.0005)
    GPIO.output(LCD_E, False)
    time.sleep(0.0005)

def lcd_text(message,line):
 # Send text to display
    message = message.ljust(LCD_CHARS," ")

    lcd_write(line, LCD_CMD)

    for i in range(LCD_CHARS):
        lcd_write(ord(message[i]),LCD_CHR)


#Begin program
try: main()
 
except KeyboardInterrupt: pass
 
finally:
    lcd_write(0x01, LCD_CMD)
    lcd_text("Hey!",LCD_LINE_1)
    lcd_text("Welcome!",LCD_LINE_2)
    GPIO.cleanup()
