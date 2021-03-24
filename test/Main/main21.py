#!/usr/bin/env python
# -*- coding: utf-8 -*-
import warnings
import hashlib
from gpiozero import LED
from gpiozero import MotionSensor
from signal import pause
from datetime import datetime
from phue import Bridge
from rgbxy import Converter
from rgbxy import GamutC
import logging
import time
from pyfingerprint.pyfingerprint import PyFingerprint
import RPi.GPIO as GPIO
import lcd_lib
import lock_lib
import db_lib
import awsIOT_lib
import awsIOT_sub
import GCAL_lib
import mail_lib

#Logging enable
logging.basicConfig()

#Suppress Warnings
warnings.simplefilter('ignore')

#Import e-mail cred
file = open("users.txt", "r")

#Prase cred
user = file.readline().rstrip("\n")
sender=(user.split(";")[0])
pas=(user.split(";")[1])
#comfirm that the server STMP working
if ((sender is not None) and (pas is not None)):
    print("STMP Server is connected")
else:
    print("STMP Server is not connected")

#### AWS Cert Files Publish#### 
awshost = "xxxxxxxxxx-ats.iot.us-west-2.amazonaws.com"      # Endpoint
awsport = 8883                                              # Port no.
clientId = "Smart_Lock_Client"                                     # Thing_Name
thingName = "Smart_Lock_Client"                                    # Thing_Name
caPath = "/home/pi/Desktop/Smart-Doorlock/Components/Cred/Lock_smart/AmazonRootCA1.pem"                    # Root_CA_Certificate_Name
certPath = "/home/pi/Desktop/Smart-Doorlock/Components/Cred/Lock_smart/xxxxxxxxxx-certificate.pem.crt"     # <Thing_Name>.cert.pem
keyPath = "/home/pi/Desktop/Smart-Doorlock/Components/Cred/Lock_smart/xxxxxxxxxx-private.pem.key"          # <Thing_Name>.private.key

#### AWS Cert Files Sub #### 
awshost2 = "xxxxxxxxxx-ats.iot.us-west-2.amazonaws.com"      # Endpoint
awsport2 = 8883                                              # Port no.   
clientId2 = "Override"                                     # Thing_Name
thingName2 = "Override"                                    # Thing_Name
caPath2 = "/home/pi/Desktop/Smart-Doorlock/Components/Cred/Override/AmazonRootCA1.pem"                    # Root_CA_Certificate_Name
certPath2 = "/home/pi/Desktop/Smart-Doorlock/Components/Cred/Override/xxxxxxxxxx-certificate.pem.crt"     # <Thing_Name>.cert.pem
keyPath2 = "/home/pi/Desktop/Smart-Doorlock/Components/Cred/Override/xxxxxxxxxx-private.pem.key"          # <Thing_Name>.private.key

#Objects
thing = awsIOT_lib.awsIOT(awshost, awsport, clientId, thingName, caPath, certPath, keyPath)
sub = awsIOT_sub.awsIOT_subscribe(awshost2, awsport2, clientId2, thingName2, caPath2, certPath2, keyPath2, "Override")
Lock = lock_lib.lock(27, 16, 19, 26, 17, 21, 20, 5, thing)
DB = db_lib.db("Users")
Lcd = Lock.lcd
b = Lock.b#Bridge
c = Lock.c#converter
cal = GCAL_lib.Gcal()
mail = mail_lib.mail(sender, pas)

#Motion
Pir = MotionSensor(4)

#Buzzers
GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)
GPIO.setup(Lock.BOpen, GPIO.OUT) #Open
GPIO.setup(Lock.BClose, GPIO.OUT) #Close

#Buzzer
GPIO.setup(6, GPIO.IN, pull_up_down=GPIO.PUD_UP)

#Reader Flag
readerState = False

#Printonce Flag
templates = 0

#Attempt Loop
count = 1

#Set the lights to white
b.set_light(1, 'on', True)
b.set_light(2, 'on', True)
b.set_light(1, 'xy', c.rgb_to_xy(253, 244, 220))
b.set_light(2, 'xy', c.rgb_to_xy(253, 244, 220))
b.set_light(1, 'on', False)
b.set_light(2, 'on', False)

#Colour var
RED = (255, 0, 0)
Green = (0, 255, 0)
White = (253, 244, 220)

#5 Min timer
timer = 300

#Last recored timestamp
ts=0

#Timestamp expire
ts_expire = Lock.timestamped

#Msg push
##def on_message(client, userdata, msg):                      # Func for receiving msgs
##    print("topic: "+msg.topic)
##    print("payload: "+str(msg.payload))
##    return (str(msg.payload))

#Lock right at the beginnig
Lock.SetLock()

#Set the alarm off
GPIO.output(Lock.BClose, False)
GPIO.output(Lock.BOpen, False)

#Main Loop
try:
    while True:
        #This will trigger a exit pushbutton(Green) for exiting from the inside
        if (GPIO.input(6) == False):
            #Set lights on
            b.set_light(1, 'on', True)
            b.set_light(2, 'on', True)
            b.set_light(1, 'xy', c.rgb_to_xy(253, 244, 220))
            b.set_light(2, 'xy', c.rgb_to_xy(253, 244, 220))
            Lock.inExit() #while loop
            ts_expire = Lock.timestamped

        #Force Entry detection (if the door with any authentication)
        if ((Lock.getReed() == 1)):#Door is open

            # Sound alarm, If both go off the frequency cancel each other out
            #GPIO.output(Lock.BClose, True)
            GPIO.output(Lock.BOpen, True)
            
            #Log event
            now = datetime.now() #datetime object containing current date and time
            date = str(now.date())
            unix = int(datetime.timestamp(now))
            dt_string = now.strftime("%d/%m/%Y_%H:%M:%S")
            userID = 'Force Entry'
            finger = "None"
            accuracyScore = -1
            status = Lock.getReedStatus()
            thing.publish("Smart_Lock", thing.createPayload(userID, finger, accuracyScore, Lock.getReedStatus(), dt_string, unix, date))

            #Send e-mail
            mail.sendMessage("example@mail.com", "Forced Entry: " + dt_string, "There was a Forced Entry Detected at " +  dt_string + ". Please go reset the door alarm by fingerprint authentication and asset situation." )

            #Delete 
            del now

            #Wait for correct fingerprint authentication
            try:  #Intialize finger print reader
                f = PyFingerprint('/dev/ttyUSB0', 57600, 0xFFFFFFFF, 0x00000000)
                
                if ( f.verifyPassword() == False ):
                    raise ValueError('The given fingerprint sensor password is wrong!')

            except Exception as e:
                print('The fingerprint sensor could not be initialized!')
                print('Exception message: ' + str(e))
                exit(1)
            ## Gets some sensor information
            if (templates == 0):
                print('Currently used templates: ' + str(f.getTemplateCount()) +'/'+ str(f.getStorageCapacity()))
                templates=1
            
            #Turn on LCD
            Lcd.backlight(True)
            Lcd.lcd_string('Waiting for', 1)
            Lcd.lcd_string('finger...', 2)

            #Enter a loop to wait for a finger print
            while True:
                #Reset lights back to white
                b.set_light(1, 'on', True)
                b.set_light(2, 'on', True)
                b.set_light(1, 'xy', c.rgb_to_xy(253, 244, 220))
                b.set_light(2, 'xy', c.rgb_to_xy(253, 244, 220))

                #Display to place finger on scanner
                Lcd.lcd_string('Waiting for', 1)
                Lcd.lcd_string('finger...', 2)

                if (f.readImage() == True): #READ if finger is read
                    Lcd.backlight(True)
                    Lcd.lcd_string("Attempt #", 1)
                    Lcd.lcd_string(str(count), 2)
                    ## Converts read image to characteristics and stores it in charbuffer 1
                    f.convertImage(0x01)

                    ## Searchs template
                    result = f.searchTemplate()

                    #Selecting index for match
                    positionNumber = result[0]
                    accuracyScore = result[1]

                    #Check buffer template against stored template
                    if ((positionNumber == 0 and accuracyScore >=50) or (positionNumber == 1 and accuracyScore >= 50) or (positionNumber == 2 and accuracyScore >= 50)): #Finger is in database if true
                        response = DB.getItem(positionNumber)
                        userID = response["userID"]
                        finger = response["finger"]

                        #Turn off alarm
                        #GPIO.output(Lock.BClose, False)
                        GPIO.output(Lock.BOpen, False)

                        #Display to LCD that fingerprint is correct
                        Lcd.backlight(True)
                        Lcd.lcd_string("Fingerprint Correct", 1)
                        Lcd.lcd_string("ID:" + userID, 2)

                        # datetime object containing current date and time
                        now = datetime.now()
                        dt_string = now.strftime("%d/%m/%Y_%H:%M:%S")
                        date = str(now.date())
                        unix = int(datetime.timestamp(now))

                        #Upload data to IOT CORE
                        thing.publish("Smart_Lock", thing.createPayload(userID, finger, accuracyScore, "Reset Alarm Correct", dt_string, unix, date))
                        
                        #Set Lights to Green
                        b.set_light(1, 'xy', c.rgb_to_xy(0, 250, 0))
                        b.set_light(2, 'xy', c.rgb_to_xy(0, 250, 0))

                        #Send e-mail
                        mail.sendMessage("example@mail.com", "Alarm Reset Correctly", "The alarm was reset by: " + userID + " at " + dt_string + " with the finger " + finger + " and with the accuracy of " + str(accuracyScore) + "%" )
                        
                        count = 1
                        # erase stored results in memory
                        del now
                        del result
                        del positionNumber
                        del accuracyScore
                        break

                    #Fingerprint authentication
                    else: 
                        #Set Lights to Red
                        b.set_light(1, 'xy', c.rgb_to_xy(250, 0, 0))
                        b.set_light(2, 'xy', c.rgb_to_xy(250, 0, 0))

                        # Records the fail thumb print and stores it locally
                        print('Downloading image (this take a while)...')

                        #Display to LCD that fingerprint is correct
                        Lcd.backlight(True)
                        Lcd.lcd_string("Fingerprint Fail", 1)
                        Lcd.lcd_string("Piss Off", 2)

                        # datetime object containing current date and time
                        now = datetime.now()
                        dt_string = now.strftime("%d/%m/%Y_%H:%M:%S")
                        d_string = now.strftime("%d_%m_%Y-%H_%M_%S")
                        date = str(now.date())
                        unix = int(datetime.timestamp(now))
                        userID = "Alarm Failed"
                        finger = "Recored"
                        status = Lock.getReedStatus() + ", Reset Alarm Failed"

                        #Downlaod Fingerprint
                        imageDestination = '/home/pi/Pictures/failPrints/' + d_string + 'fingerprint.bmp'
                        f.downloadImage(imageDestination)

                        #This is for less then 3 attempts
                        if (count < 4):

                            #Upload data to IOT CORE
                            thing.publish("Smart_Lock", thing.createPayload(userID, finger, accuracyScore, status, dt_string, unix, date))

                            # E-mail
                            mail.sendItem("example@mail.com", ("This is attempt number on Force Entry Reset: " + str(count)), ("This was capture at " + dt_string + " and Image stored locally at " + imageDestination), imageDestination)
                            print('The image was saved to "' + imageDestination + "at the time: " + d_string + '".')

                            #Timeout counter
                            count += 1
                        
                        #This is for more then 3 attempts
                        if (count >= 4):
                            del now
                            # datetime object containing current date and time
                            now = datetime.now()
                            dt_string = now.strftime("%d/%m/%Y_%H:%M:%S")
                            thing.publish("Smart_Lock", thing.createPayload(userID, c, accuracyScore, status, dt_string, unix, date))
                            #E-mail
                            mail.sendItem("example@mail.com", ("This is attempt number on Force Entry Reset: " + str(count)), ("A timeout was trigger at the attempt #" + str(count) + ", a timeout of " + str(count) + " mins has been set. This was capture at " + dt_string + " and Image stored locally at " + imageDestination), imageDestination)
                            print('The image was saved to "' + imageDestination + "at the time: " + d_string + '".')

                            #Timeout 
                            for i in range (5*count):
                                for j in range (60):
                                    new =(str(4-i) + ":" + str(59-j))
                                    time.sleep(1)
                                    Lcd.lcd_string('Timeout Left:', 1)
                                    Lcd.lcd_string(new, 2)
                                    print("Timeout: " + new)

                            #Timeout counter
                            count += 1

                        #Set lights on and back to white
                        b.set_light(1, 'on', True)
                        b.set_light(2, 'on', True)
                        b.set_light(1, 'xy', c.rgb_to_xy(253, 244, 220))
                        b.set_light(2, 'xy', c.rgb_to_xy(253, 244, 220))

                        # erase stored results in memory
                        del now
                        del result
                        del positionNumber
                        del accuracyScore

                #Used to slow down the scanning of the fingerprint sensor
                time.sleep(0.3)

        # if (no motion and door is closed)
        if ((Pir.value == False) and (Lock.getReed() == 0)):
            Lcd.backlight(False)

            # datetime object containing current date and time
            now = datetime.now()
            ts = int(now.timestamp())
            del now
            if ((ts - ts_expire)>=0):
                #Set lights off
                b.set_light(1, 'on', False)
                b.set_light(2, 'on', False)

        # if (motion and door is closed)
        if ((Pir.value == True) and (Lock.getReed() == 0)):
            Lcd.backlight(True)
            #Set lights on
            b.set_light(1, 'on', True)
            b.set_light(2, 'on', True)
            b.set_light(1, 'xy', c.rgb_to_xy(253, 244, 220))
            b.set_light(2, 'xy', c.rgb_to_xy(253, 244, 220))

            #Make sure Door is Lock
            Lock.SetLock()

            # datetime object containing current date and time
            now = datetime.now()
            sysDate = now.strftime("%Y-%m-%d")
            sysTime = now.strftime("%H:%M:%S")
            ts = int(now.timestamp())
            ts_expire = ts + timer
            del now
            try:  #Intialize finger print reader
              f = PyFingerprint('/dev/ttyUSB0', 57600, 0xFFFFFFFF, 0x00000000)
              
              if ( f.verifyPassword() == False ):
                raise ValueError('The given fingerprint sensor password is wrong!')

            except Exception as e:
                print('The fingerprint sensor could not be initialized!')
                print('Exception message: ' + str(e))
                exit(1)

            ## Gets some sensor information
            if (templates == 0):
              print('Currently used templates: ' + str(f.getTemplateCount()) +'/'+ str(f.getStorageCapacity()))
              templates=1
            readerState = True #FLAG

            #Call the Google calendar api to trigger for the next same day event
            calEvent = cal.nextEvent(sysDate)
            
            if calEvent is None:
                Lcd.lcd_string('Waiting for', 1)
                Lcd.lcd_string('finger...', 2)
            elif ((sysTime >= calEvent["Start"]) and (sysTime <= calEvent["End"])):
                calstart = calEvent["Start"].rstrip(":")
                calend = calEvent["End"].rstrip(":")
                Lcd.lcd_string('In Meeting', 1)
                Lcd.lcd_string(calstart + " - " + calend, 2)
                time.sleep(1)
                Lcd.lcd_string("Get off my",1)
                Lcd.lcd_string("Lawn!!!!!!!!", 2)
                time.sleep(1)
            else:
                Lcd.lcd_string('Waiting for', 1)
                Lcd.lcd_string('finger...', 2)
        if(readerState == True):
            readerState = False
            if (f.readImage() == True): #READ if finger is read
                Lcd.backlight(True)
                Lcd.lcd_string("Attempt #", 1)
                Lcd.lcd_string(str(count), 2)

                ## Converts read image to characteristics and stores it in charbuffer 1
                f.convertImage(0x01)

                ## Searchs template
                result = f.searchTemplate()

                #Selecting index for match
                positionNumber = result[0]
                accuracyScore = result[1]

                #Check buffer template against stored template
                if ((positionNumber == 0 and accuracyScore >=50) or (positionNumber == 1 and accuracyScore >= 50) or (positionNumber == 2 and accuracyScore >= 50)): #Finger is in database if true
                    response = DB.getItem(positionNumber)
                    userID = response["userID"]
                    finger = response["finger"]

                    # datetime object containing current date and time
                    now = datetime.now()
                    dt_string = now.strftime("%d/%m/%Y_%H:%M:%S")
                    date = str(now.date())
                    unix = int(datetime.timestamp(now))

                    #Upload data to IOT CORE
                    thing.publish("Smart_Lock", thing.createPayload(userID, finger, accuracyScore, "Access", dt_string, unix, date))
                    
                    #Set Lights to Green
                    b.set_light(1, 'xy', c.rgb_to_xy(0, 250, 0))
                    b.set_light(2, 'xy', c.rgb_to_xy(0, 250, 0))

                    #Unlock 
                    Lock.access(userID, finger, accuracyScore)
                    
                    count = 1
                     # erase stored results in memory
                    del now
                    del result
                    del positionNumber
                    del accuracyScore
                else: 
                    #Set Lights to Red
                    b.set_light(1, 'xy', c.rgb_to_xy(250, 0, 0))
                    b.set_light(2, 'xy', c.rgb_to_xy(250, 0, 0))

                    # Records the fail thumb print and stores it locally
                    print('Downloading image (this take a while)...')

                    #Display to LCD that fingerprint is Incorrect
                    Lcd.backlight(True)
                    Lcd.lcd_string("Fingerprint Fail", 1)
                    Lcd.lcd_string("Piss Off", 2)

                    # datetime object containing current date and time
                    now = datetime.now()
                    dt_string = now.strftime("%d/%m/%Y_%H:%M:%S")
                    d_string = now.strftime("%d_%m_%Y-%H_%M_%S")
                    date = str(now.date())
                    unix = int(datetime.timestamp(now))
                    userID = "Failed"
                    finger = "Recored"
                    status = Lock.getReedStatus()

                    #Download fingerprint
                    imageDestination = '/home/pi/Pictures/failPrints/' + d_string + 'fingerprint.bmp'
                    f.downloadImage(imageDestination)

                    #This is for less then 3 attempts
                    if (count < 4):
                        #Upload data to IOT CORE
                        thing.publish("Smart_Lock", thing.createPayload(userID, finger, accuracyScore, status, dt_string, unix, date))

                        #Send E-mail
                        mail.sendItem("example@mail.com", ("This is attempt number: " + str(count)), ("Image stored locally at " + imageDestination), imageDestination)
                        print('The image was saved to "' + imageDestination + "at the time: " + d_string + '".')

                        #Timeout counter
                        count += 1
                    
                    if (count >= 4):
                        del now
                        # datetime object containing current date and time
                        now = datetime.now()
                        dt_string = now.strftime("%d/%m/%Y_%H:%M:%S")
                        thing.publish("Smart_Lock", thing.createPayload(userID, c, accuracyScore, status, dt_string, unix, date))

                        #E-mail
                        mail.sendItem("example@mail.com", ("This is attempt number:" + str(count)), ("A timeout was trigger at the attempt #" + str(count) + ", a timeout of " + str(count) + " mins has been set. This was capture at " + dt_string + " and Image stored locally at " + imageDestination), imageDestination)
                        print('The image was saved to "' + imageDestination + "at the time: " + d_string + '".')
                        
                        for i in range (5*count):
                            for j in range (60):
                                new =(str(4-i) + ":" + str(59-j))
                                time.sleep(1)
                                Lcd.lcd_string('Timeout Left:', 1)
                                Lcd.lcd_string(new, 2)
                                print("Timeout: " + new)
                        
                        #Timeout counter
                        count += 1

                    #Set lights on
                    b.set_light(1, 'on', True)
                    b.set_light(2, 'on', True)
                    b.set_light(1, 'xy', c.rgb_to_xy(253, 244, 220))
                    b.set_light(2, 'xy', c.rgb_to_xy(253, 244, 220))

                    # erase stored results in memory
                    del now
                    del result
                    del positionNumber
                    del accuracyScore

##        if (sub.getPayload() == "true"):
##            print("true")
##            Lock.SetUnlock()
##        if (sub.getPayload() == "false"):
##            print("false")
##            Lock.SetLock()

except KeyboardInterrupt:
    print('Program Ended.')
    
finally:
    print("GPIO cleanup")
    GPIO.cleanup()
