#!/usr/bin/env python
# -*- coding: utf-8 -*-

import hashlib
from gpiozero import LED, Button
from gpiozero import MotionSensor
from signal import pause
from datetime import datetime
import time
from pyfingerprint.pyfingerprint import PyFingerprint
import RPi.GPIO as GPIO


# Define GPIO to LCD mapping
RED = 27
GREEN = 16
REDIN = 19
GREENIN = 26
LOCK = 17
BUZZO = 21
BUZZC = 20
LCD_RS = 7
LCD_E  = 8
LCD_D4 = 25
LCD_D5 = 24
LCD_D6 = 23
LCD_D7 = 18
LED_ON = 15
pir = MotionSensor(4)
YBUTT = 13
GBUTT = 6
YBUTT2 = Button(13)
GBUTT2 = Button(6)
RELAY = LED(17)
LED_ON2 = LED(15)
Reed = 5
# Define some device constants
LCD_WIDTH = 16    # Maximum characters per line
LCD_CHR = True
LCD_CMD = False

LCD_LINE_1 = 0x80 # LCD RAM address for the 1st line
LCD_LINE_2 = 0xC0 # LCD RAM address for the 2nd line

# Timing constants
E_PULSE = 0.0005
E_DELAY = 0.0005

#Reader Flag
readerState = False

#Printonce Flag
templates = 0

# datetime object containing current date and time
now = datetime.now()

def setup():
  # Main setup block
  
  GPIO.setwarnings(False)
  GPIO.setmode(GPIO.BCM)       # Use BCM GPIO numbers
  GPIO.setup(LCD_E, GPIO.OUT)  # E
  GPIO.setup(LCD_RS, GPIO.OUT) # RS
  GPIO.setup(LCD_D4, GPIO.OUT) # DB4
  GPIO.setup(LCD_D5, GPIO.OUT) # DB5
  GPIO.setup(LCD_D6, GPIO.OUT) # DB6
  GPIO.setup(LCD_D7, GPIO.OUT) # DB7
  GPIO.setup(LOCK, GPIO.OUT) #Switch
  GPIO.setup(LED_ON, GPIO.OUT) # Backlight enable
  GPIO.setup(RED, GPIO.OUT) #Red
  GPIO.setup(GREEN, GPIO.OUT) #Green
  GPIO.setup(BUZZO, GPIO.OUT) #Opening Buzzer
  GPIO.setup(BUZZC, GPIO.OUT) #Closing Buzzer
  GPIO.setup(REDIN, GPIO.OUT) #Red inside
  GPIO.setup(GREENIN, GPIO.OUT) #Green inside
  GPIO.setup(YBUTT, GPIO.IN, pull_up_down=GPIO.PUD_UP) #Yellow Button
  GPIO.setup(GBUTT, GPIO.IN, pull_up_down=GPIO.PUD_UP) #Green Button
  GPIO.setup(Reed, GPIO.IN) #Reed Switch

  # Initialise display
  lcd_init()

def lcd_init():
  # Initialise display
  lcd_byte(0x33,LCD_CMD) # 110011 Initialise
  lcd_byte(0x32,LCD_CMD) # 110010 Initialise
  lcd_byte(0x06,LCD_CMD) # 000110 Cursor move direction
  lcd_byte(0x0C,LCD_CMD) # 001100 Display On,Cursor Off, Blink Off
  lcd_byte(0x28,LCD_CMD) # 101000 Data length, number of lines, font size
  lcd_byte(0x01,LCD_CMD) # 000001 Clear display
  time.sleep(E_DELAY)

def lcd_byte(bits, mode):
  # Send byte to data pins
  # bits = data
  # mode = True  for character
  #        False for command

  GPIO.output(LCD_RS, mode) # RS

  # High bits
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
  # Toggle enable
  time.sleep(E_DELAY)
  GPIO.output(LCD_E, True)
  time.sleep(E_PULSE)
  GPIO.output(LCD_E, False)
  time.sleep(E_DELAY)

def lcd_string(message,line):
  # Send string to display
  message = message.ljust(LCD_WIDTH," ")

  lcd_byte(line, LCD_CMD)

  for i in range(LCD_WIDTH):
    lcd_byte(ord(message[i]),LCD_CHR)
    
def access():
      GPIO.output(LOCK, False)
      GPIO.output(BUZZO, True)
      time.sleep(0.2)
      GPIO.output(BUZZO, False)
      lcd_string('Access Granted',LCD_LINE_1)
      lcd_string('Welcome!',LCD_LINE_2)
      GPIO.output(BUZZO, True)
      time.sleep(0.2)
      GPIO.output(BUZZO, False)
      GPIO.output(RED, False)
      GPIO.output(REDIN, False)
      GPIO.output(GREEN, True)
      GPIO.output(GREENIN, True)
      time.sleep(1.5)
      if (positionNumber == 0):        
        newPos = "Kevin`s Index"
        lcd_string('ID#' + str(newPos),LCD_LINE_1)
        lcd_string('Accuracy: ' + str(accuracyScore),LCD_LINE_2)
        time.sleep(3)
      elif (positionNumber == 1):
        newPos ="Kevin`s Thumb"
        lcd_string('ID#' + str(newPos),LCD_LINE_1)
        lcd_string('Accuracy: ' + str(accuracyScore),LCD_LINE_2)
        time.sleep(3)
      elif (positionNumber == 2):
        newPos ="Eden`s Index"
        lcd_string('ID#' + str(newPos),LCD_LINE_1)
        lcd_string('Accuracy: ' + str(accuracyScore),LCD_LINE_2)
        time.sleep(3)
      #Door open
      lcd_string('Door Status:',LCD_LINE_1)
      lcd_string('UNLOCKED',LCD_LINE_2)
      time.sleep(5)
      GPIO.output(GREEN, False)
      GPIO.output(GREENIN, False)
      GPIO.output(LED_ON, False) #LCD OFF
      while(GPIO.input(Reed) == 1):
          pass
      relock()
        
def relock():
  
      GPIO.output(LOCK, True)#Lock Lock
      GPIO.output(LED_ON, True) #LCD ON
      lcd_string('Door Status:',LCD_LINE_1)
      lcd_string('LOCKED',LCD_LINE_2)
      GPIO.output(RED, True)
      GPIO.output(REDIN, True)
      GPIO.output(GREEN, False)
      GPIO.output(GREENIN, False)
      GPIO.output(BUZZC, True)
      time.sleep(0.3)
      GPIO.output(BUZZC, False)
      time.sleep(0.3)
      GPIO.output(BUZZC, True)
      time.sleep(0.3)
      GPIO.output(BUZZC, False)
      time.sleep(0.3)
      GPIO.output(REDIN, False)
      GPIO.output(GREENIN, False)

def lock1():
      GPIO.output(LOCK, True)#Lock Lock
      GPIO.output(RED, True)
      GPIO.output(REDIN, False)
      GPIO.output(GREEN, False)
      GPIO.output(GREENIN, False)

def inExit():
      GPIO.output(LOCK, False) #unlock door
      GPIO.output(REDIN, False)
      GPIO.output(GREENIN, True)
      lcd_string('Door Status:',LCD_LINE_1)
      lcd_string('UNLOCKED',LCD_LINE_2)
      time.sleep(3)
      GPIO.output(REDIN, False)
      GPIO.output(GREENIN, False)
      GPIO.output(RED, False)
      GPIO.output(GREEN, False)
      while(GPIO.input(Reed) == 1):
          pass
      relock()
      
#Pin Setup 
setup()
#Lock On
GPIO.output(LOCK, True)
# Toggle backlight on
GPIO.output(LED_ON, True)
#attempt loop
count = 1
#void loop
while True:
      #Master button
      YBUTT2.when_pressed = RELAY.off 
      YBUTT2.when_released = RELAY.on
      GBUTT2.when_pressed = inExit
      # if (no motion and door is closed)
      if ((pir.value == False) and (GPIO.input(Reed) == 0)):
            GPIO.output(LED_ON, False) #LCD OFF
      # if (motion and door is closed)
      if ((pir.value == True) and (GPIO.input(Reed) == 0)):
            GPIO.output(LED_ON, True) #LCD ON
            lock1()
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
            lcd_string('Waiting for',LCD_LINE_1)
            lcd_string('finger...',LCD_LINE_2)
      if(readerState == True):
            readerState = False
            if (f.readImage() == True): #READ if finger is read
                   GPIO.output(LED_ON, True) #LCD ON
                   lcd_string("Attempt #",LCD_LINE_1)
                   lcd_string(str(count),LCD_LINE_2)
                   GPIO.output(BUZZO, True)
                   GPIO.output(BUZZC, True)
                   time.sleep(0.3)
                   GPIO.output(BUZZO, False)
                   GPIO.output(BUZZC, False)
                   time.sleep(0.3)
                   ## Converts read image to characteristics and stores it in charbuffer 1
                   f.convertImage(0x01)

                   ## Searchs template
                   result = f.searchTemplate()

                   positionNumber = result[0]
                   accuracyScore = result[1]
                   if ((positionNumber == 0 and accuracyScore >=50) or (positionNumber == 1 and accuracyScore >= 50) or (positionNumber == 2 and accuracyScore >= 50)): #Finger is in database if true
                         # dd/mm/YY H:M:S
                         dt_string = now.strftime("%d/%m/%Y %H:%M:%S")
                         if (positionNumber == 0):
                           print("Kevin`s Index access at: " + dt_string + ", Accuracy: " + str(accuracyScore))
                         elif (positionNumber == 1):
                           print("Kevin`s Thumb access at: " + dt_string + ", Accuracy: " + str(accuracyScore))
                         elif (positionNumber == 2):
                           print("Eden`s Thumb access at: " + dt_string + ", Accuracy: " + str(accuracyScore))
                         access()
                         count = 1
                         # erase stored results in memory
                         del result
                         del positionNumber
                         del accuracyScore
                   else: #Timeout
                       count += 1
                       # erase stored results in memory
                       del result
                       del positionNumber
                       del accuracyScore
                       if (count >= 3+1):
                         for i in range (5):
                             for j in range (60):
                                 new =(str(4-i) + ":" + str(59-j))
                                 time.sleep(1)
                                 lcd_string('Timeout Left:',LCD_LINE_1)
                                 lcd_string(new,LCD_LINE_2)
                                 print("Timeout: " + new)
                                 
                        
                                
            
