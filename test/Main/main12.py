#!/usr/bin/env python
# -*- coding: utf-8 -*-
import warnings
import hashlib
from gpiozero import LED, Button
from gpiozero import MotionSensor
from signal import pause
from datetime import datetime
import time
from pyfingerprint.pyfingerprint import PyFingerprint
import RPi.GPIO as GPIO
import lcd_lib
import lock_lib
import db_lib
import awsIOT_lib
import awsIOT_sub

#Suppress Warnings
warnings.simplefilter('ignore')

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

#Buttons
GButt = Button(6)
YButt = Button(13)

#Motion
Pir = MotionSensor(4)

#Reader Flag
readerState = False

#Printonce Flag
templates = 0

#Attempt Loop
count = 1

#Msg push
##def on_message(client, userdata, msg):                      # Func for receiving msgs
##    print("topic: "+msg.topic)
##    print("payload: "+str(msg.payload))
##    return (str(msg.payload))

#Lock right at the beginnig
Lock.SetLock()

try:
    while True:
        #Master button
        GButt.when_pressed = Lock.inExit
##        YButt.when_pressed = Lock.SetUnlock()
##        YButt.when_released = Lock.SetLock()
        # if (no motion and door is closed)
        if ((Pir.value == False) and (Lock.getReed() == 0)):
            Lcd.backlight(False)
        # if (motion and door is closed)
        if ((Pir.value == True) and (Lock.getReed() == 0)):
            Lcd.backlight(True)
            #Make sure Door is Lock
            Lock.SetLock()
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

                    #Upload data to IOT CORE
                    thing.publish("Smart_Lock", thing.createPayload(userID, finger, accuracyScore, "Access", dt_string))

                    #Unlock 
                    Lock.access(userID, finger, accuracyScore)
                    
                    count = 1
                     # erase stored results in memory
                    del now
                    del result
                    del positionNumber
                    del accuracyScore
                else: 
                    #Timeout counter
                    count += 1
                    # Records the fail thumb print and stores it locally
                    print('Downloading image (this take a while)...')
                    # datetime object containing current date and time
                    now = datetime.now()
                    dt_string = now.strftime("%d/%m/%Y_%H:%M:%S")
                    userID = "Failed"
                    finger = "Recored"
                    status = Lock.getReedStatus()

                    #Upload data to IOT CORE
                    thing.publish("Smart_Lock", thing.createPayload(userID, finger, accuracyScore, status, dt_string))

                    d_string = now.strftime("%d_%m_%Y-%H_%M_%S")

                    imageDestination = '/home/pi/Pictures/failPrints/' + d_string + 'fingerprint.bmp'
                    f.downloadImage(imageDestination)
                    print('The image was saved to "' + imageDestination + "at the time: " + d_string + '".')
                    
                    if (count >= 3+1):
                        del now
                        # datetime object containing current date and time
                        now = datetime.now()
                        dt_string = now.strftime("%d/%m/%Y_%H:%M:%S")
                        c = (count - 3)
                        thing.publish("Smart_Lock", thing.createPayload(userID, c, accuracyScore, status, dt_string))
                        
                        for i in range (5*c):
                            for j in range (60):
                                new =(str(4-i) + ":" + str(59-j))
                                time.sleep(1)
                                Lcd.lcd_string('Timeout Left:', 1)
                                Lcd.lcd_string(new, 2)
                                print("Timeout: " + new)
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
