import hashlib
from gpiozero import LED, Button
from gpiozero import MotionSensor
from signal import pause
from datetime import datetime
import time
from phue import Bridge
from rgbxy import Converter
from rgbxy import GamutC
import logging
from pyfingerprint.pyfingerprint import PyFingerprint
import RPi.GPIO as GPIO
import lcd_lib
import awsIOT_lib

class lock:
    def __init__(self, RED, GREEN, REDIN, GREENIN, LOCK, BUZZ_OPEN, BUZZ_CLOSE, REED_SWITCH, thing, ip):
        self.Red = RED
        self. Green = GREEN
        self.RedIn = REDIN
        self.GreenIn = GREENIN
        self.Lock = LOCK
        self.BOpen = BUZZ_OPEN
        self.BClose = BUZZ_CLOSE
        self.Reed = REED_SWITCH
        #Make a lcd object from my lcd library
        self.lcd = lcd_lib.lcd(7, 8, 25, 24, 23, 18, 15)
        #Store AWS_IOT object ref here
        self.thing = thing
        #Converter
        self.c = Converter(GamutC)
        #Phue object
        self.b = Bridge(ip)
        #Timestamp from inexit()
        self.timestamped = 0
        #Setup the Pins
        self.setup()

    def setup(self):
        GPIO.setwarnings(False)
        GPIO.setmode(GPIO.BCM)       # Use BCM GPIO numbers
        GPIO.setup(self.Red, GPIO.OUT) #Red
        GPIO.setup(self.Green, GPIO.OUT) #Green
        GPIO.setup(self.RedIn, GPIO.OUT) #Inside Red
        GPIO.setup(self.GreenIn, GPIO.OUT) #Inside Green
        GPIO.setup(self.Lock, GPIO.OUT) #Lock/Relay
        GPIO.setup(self.BOpen, GPIO.OUT) # Opening Buzzer
        GPIO.setup(self.BClose, GPIO.OUT) # Closing Buzzer
        GPIO.setup(self.Reed, GPIO.IN) #Reed Switch
        self.b.connect()

    def access(self, userID, finger, accuracyScore):
      openonce = 0
      self.lcd.backlight(True)
      self.lcd.lcd_string('Access Granted',1)
      self.lcd.lcd_string('Welcome!',2)
      # datetime object containing current date and time
      now = datetime.now()
      self.status("Unlock", now)
      time.sleep(0.3)
      # dd/mm/YY H:M:S
      dt_string = now.strftime("%d/%m/%Y %H:%M:%S")       
      self.lcd.lcd_string('ID#' + str(userID),1)
      self.lcd.lcd_string('Accuracy: ' + str(accuracyScore),2)
      print('ID#' + str(userID) + " access: " + dt_string + ", Accuracy: " + str(accuracyScore))
      time.sleep(2)
      del now
      #Door open
      self.lcd.lcd_string('Door Status:',1)
      self.lcd.lcd_string('UNLOCKED',2)
      time.sleep(2)
      #1 is door is close and 0 is open
      while(GPIO.input(self.Reed) == 1):
        if (openonce == 0):
          self.lcd.backlight(False)
          # datetime object containing current date and time
          now = datetime.now()
          dt_string2 = now.strftime("%d/%m/%Y %H:%M:%S")
          print('ID#' + str(userID) + " opened: " + dt_string2)
          dt_string = now.strftime("%d/%m/%Y_%H:%M:%S")
          self.thing.publish("Smart_Lock", self.thing.createPayload(userID, finger, accuracyScore, self.getReedStatus(), dt_string))
          del now
          openonce = 1
        pass
      self.relock(userID, accuracyScore, finger)

    def relock(self, userID, accuracyScore, finger):
      self.lcd.backlight(True)
      #Set Light back to white
      self.b.set_light(1, 'xy', self.c.rgb_to_xy(253, 244, 220))
      self.b.set_light(2, 'xy', self.c.rgb_to_xy(253, 244, 220))
      self.lcd.lcd_string('Door Status:',1)
      self.lcd.lcd_string('LOCKED',2)
      # datetime object containing current date and time
      now = datetime.now()
      self.status("Lock", now)
      dt_string = now.strftime("%d/%m/%Y %H:%M:%S")
      print('ID#' + userID + " closed: " + dt_string) 
      dt_string = now.strftime("%d/%m/%Y_%H:%M:%S")
      self.thing.publish("Smart_Lock", self.thing.createPayload(userID, finger, accuracyScore, self.getReedStatus(), dt_string))
      del now

    def status(self, state, now):
        if (state == "Lock"):
          if (now.hour < 20 and now.hour >= 8):
            GPIO.output(self.Lock, True)#Lock 
            GPIO.output(self.Red, True)
            GPIO.output(self.RedIn, True)
            GPIO.output(self.Green, False)
            GPIO.output(self.GreenIn, False)
            GPIO.output(self.BClose, True)
            time.sleep(0.3)
            GPIO.output(self.BClose, False)
            time.sleep(0.3)
            GPIO.output(self.BClose, True)
            time.sleep(0.3)
            GPIO.output(self.BClose, False)
            time.sleep(0.3)
            GPIO.output(self.RedIn, False)
            GPIO.output(self.GreenIn, False)
          else:
            GPIO.output(self.Lock, True)#Lock 
            GPIO.output(self.Red, True)
            GPIO.output(self.RedIn, True)
            GPIO.output(self.Green, False)
            GPIO.output(self.GreenIn, False)
            time.sleep(0.5)
            GPIO.output(self.RedIn, False)
            GPIO.output(self.GreenIn, False)
        elif (state == "Unlock"):
          if (now.hour < 20 and now.hour >= 8):
            GPIO.output(self.Lock, False)#Unlock 
            GPIO.output(self.Red, False)
            GPIO.output(self.RedIn, False)
            GPIO.output(self.Green, True)
            GPIO.output(self.GreenIn, True)
            GPIO.output(self.BOpen, True)
            time.sleep(0.25)
            GPIO.output(self.BOpen, False)
            GPIO.output(self.BOpen, True)
            time.sleep(0.25)
            GPIO.output(self.BOpen, False)
            GPIO.output(self.Green, False)
            GPIO.output(self.GreenIn, False)
          else:
            GPIO.output(self.Lock, False)#Unlock 
            GPIO.output(self.Red, False)
            GPIO.output(self.RedIn, False)
            GPIO.output(self.Green, True)
            GPIO.output(self.GreenIn, True)
            time.sleep(0.5)
            GPIO.output(self.Green, False)
            GPIO.output(self.GreenIn, False)
            
    def inExit(self):
      self.b.set_light(1, 'on', True)
      self.b.set_light(2, 'on', True)
      openonce = 0
      userID = "inExit()"
      finger = "Accessed"
      accuracyScore = 0
      # datetime object containing current date and time
      now = datetime.now()
      self.status("Unlock", now)
      dt_string = now.strftime("%d/%m/%Y %H:%M:%S")
      print("Accessed: " + dt_string) 
      dt_string = now.strftime("%d/%m/%Y_%H:%M:%S")
      self.thing.publish("Smart_Lock", self.thing.createPayload(userID, finger, accuracyScore, self.getReedStatus(), dt_string))
      self.lcd.backlight("Unlock")
      self.lcd.lcd_string('Door Status:',1)
      self.lcd.lcd_string('UNLOCKED',2)
      del now
      time.sleep(3)
      while (GPIO.input(self.Reed) == 1):
          #Set lights on
          self.b.set_light(1, 'on', True)
          self.b.set_light(2, 'on', True)
          self.b.set_light(1, 'xy', self.c.rgb_to_xy(253, 244, 220))
          self.b.set_light(2, 'xy', self.c.rgb_to_xy(253, 244, 220))
          print ("Inside inexit() loop")
          if (openonce == 0):
              # datetime object containing current date and time
              now = datetime.now()
              dt_string = now.strftime("%d/%m/%Y %H:%M:%S")
              print("Opened: " + dt_string)
              dt_string = now.strftime("%d/%m/%Y_%H:%M:%S")
              access = "Opened"
              self.thing.publish("Smart_Lock", self.thing.createPayload(userID, finger, accuracyScore, self.getReedStatus(), dt_string)) 
              del now
              self.lcd.backlight(False)
              openonce = 1
          pass
      now = datetime.now()
      self.timestamped = int(now.timestamp()) + 300
      self.status("Lock", now)
      dt_string = now.strftime("%d/%m/%Y %H:%M:%S")
      print("Closed: " + dt_string) 
      access = "Closed"
      dt_string = now.strftime("%d/%m/%Y_%H:%M:%S")
      self.thing.publish("Smart_Lock", self.thing.createPayload(userID, finger, accuracyScore, self.getReedStatus(), dt_string))
      self.lcd.backlight(True) #LCD ON
      self.lcd.lcd_string('Door Status:', 1)
      self.lcd.lcd_string('LOCKED', 2)
      time.sleep(2) 
      self.lcd.backlight(False)
      del now

    def getReed(self):
        return (GPIO.input(self.Reed))

    def getReedStatus(self):
      if (self.getReed() == 0):
        return ("Closed")
      elif (self.getReed() == 1):
        return ("Open")

    def SetLock(self):
      GPIO.output(self.Lock, True)#Lock
      GPIO.output(self.Red, True)
      GPIO.output(self.RedIn, True)
      time.sleep(0.5)
      GPIO.output(self.RedIn, False)
      GPIO.output(self.Green, False)
      GPIO.output(self.GreenIn, False)

    def SetUnlock(self):
      GPIO.output(self.Lock, False)#UnLock
      GPIO.output(self.Red, False)
      GPIO.output(self.RedIn, False)
      GPIO.output(self.Green, True)
      GPIO.output(self.GreenIn, True)
      time.sleep(0.5)
      GPIO.output(self.Green, False)
      GPIO.output(self.GreenIn, False)


