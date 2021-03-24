#!/usr/bin/env python
# -*- coding: utf-8 -*-

import hashlib
from gpiozero import LED, Button
from gpiozero import MotionSensor
from signal import pause
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
pir2 = 4
YBUTT = 13
GBUTT = 6
YBUTT2 = Button(13)
GBUTT2 = Button(6)
RELAY = LED(17)
LED_ON2 = LED(15)
# Define some device constants
LCD_WIDTH = 16    # Maximum characters per line
LCD_CHR = True
LCD_CMD = False

LCD_LINE_1 = 0x80 # LCD RAM address for the 1st line
LCD_LINE_2 = 0xC0 # LCD RAM address for the 2nd line

# Timing constants
E_PULSE = 0.0005
E_DELAY = 0.0005

def main():
  # Main program block
  
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
  GPIO.setup(pir2, GPIO.IN, pull_up_down=GPIO.PUD_UP) #Manual pir
  GPIO.setup(RED, GPIO.OUT) #Red
  GPIO.setup(GREEN, GPIO.OUT) #Green
  GPIO.setup(BUZZO, GPIO.OUT) #Opening Buzzer
  GPIO.setup(BUZZC, GPIO.OUT) #Closing Buzzer
  GPIO.setup(REDIN, GPIO.OUT) #Red inside
  GPIO.setup(GREENIN, GPIO.OUT) #Green inside
  GPIO.setup(YBUTT, GPIO.IN, pull_up_down=GPIO.PUD_UP) #Yellow Button
  GPIO.setup(GBUTT, GPIO.IN, pull_up_down=GPIO.PUD_UP) #Green Button

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
    
##def yellowbutton():
##  GPIO.output(LOCK, False)
##  time.sleep(3)
##  GPIO.output(LOCK, True)
##
##def greenbutton():
##  GPIO.output(LOCK, False)
##  time.sleep(3)
##  GPIO.output(LOCK, True)

## Search for a finger
## Tries to initialize the sensor
# Toggle backlight on
#ButtonStates Var
##buttonState = GPIO.input(YBUTT)
##buttonState2 = GPIO.input(GBUTT)

#Master Script
def master():
  #Fingerprint authentication          
  if(pir.wait_for_motion()):
      GPIO.output(LED_ON, False)
      try:
          f = PyFingerprint('/dev/ttyUSB0', 57600, 0xFFFFFFFF, 0x00000000)

          if ( f.verifyPassword() == False ):
              raise ValueError('The given fingerprint sensor password is wrong!')

      except Exception as e:
          print('The fingerprint sensor could not be initialized!')
          print('Exception message: ' + str(e))
          exit(1)

      ## Gets some sensor information
      print('Currently used templates: ' + str(f.getTemplateCount()) +'/'+ str(f.getStorageCapacity()))

      ## Tries to search the finger and calculate hash
      try:
          lcd_string('Waiting for',LCD_LINE_1)
          lcd_string('finger...',LCD_LINE_2)
          
          ## Wait that finger is read
          while ( f.readImage() == False ):
              pass

          ## Converts read image to characteristics and stores it in charbuffer 1
          f.convertImage(0x01)

          ## Searchs template
          result = f.searchTemplate()

          positionNumber = result[0]
          accuracyScore = result[1]
          #Not found and not match
          if (positionNumber == -1):
              GPIO.output(BUZZC, True)
              GPIO.output(RED, True)
              GPIO.output(REDIN, True)
              time.sleep(0.6)
              GPIO.output(BUZZC, False)
              lcd_string('No match found!',LCD_LINE_1)
              lcd_string('Please try again.', LCD_LINE_2)
              time.sleep(1.8)
              GPIO.output(RED, False)
              GPIO.output(REDIN, False)
          #Found and match     
          elif (positionNumber == 0 or positionNumber == 1):
              GPIO.output(BUZZO, True)
              time.sleep(0.2)
              GPIO.output(BUZZO, False)
              time.sleep(0.1)
              GPIO.output(BUZZO, True)
              time.sleep(0.2)
              GPIO.output(BUZZO, False)
              GPIO.output(LOCK, False)
              lcd_string('Access Granted',LCD_LINE_1)
              lcd_string('Welcome!',LCD_LINE_2)
              GPIO.output(GREEN, True)
              GPIO.output(GREENIN, True)
              time.sleep(1.5)
              lcd_string('ID#' + str(positionNumber),LCD_LINE_1)
              lcd_string('Accuracy: ' + str(accuracyScore),LCD_LINE_2)
              time.sleep(2.3)
              lcd_string('Time remaining:',LCD_LINE_1)
              lcd_string('10',LCD_LINE_2)
              time.sleep(1)
              lcd_string('Time remaining:',LCD_LINE_1)
              lcd_string('9',LCD_LINE_2)
              time.sleep(1)
              lcd_string('Time remaining:',LCD_LINE_1)
              lcd_string('8',LCD_LINE_2)
              time.sleep(1)
              lcd_string('Time remaining:',LCD_LINE_1)
              lcd_string('7',LCD_LINE_2)
              time.sleep(1)
              lcd_string('Time remaining:',LCD_LINE_1)
              lcd_string('6',LCD_LINE_2)
              time.sleep(1)
              lcd_string('Time remaining:',LCD_LINE_1)
              lcd_string('5',LCD_LINE_2)
              time.sleep(1)
              lcd_string('Time remaining:',LCD_LINE_1)
              lcd_string('4',LCD_LINE_2)
              time.sleep(1)
              lcd_string('Time remaining:',LCD_LINE_1)
              lcd_string('3',LCD_LINE_2)
              GPIO.output(BUZZO, True)
              time.sleep(0.1)
              GPIO.output(BUZZO, False)
              time.sleep(0.1)
              GPIO.output(BUZZO, True)
              time.sleep(0.1)
              GPIO.output(BUZZO, False)
              time.sleep(0.1)
              GPIO.output(BUZZO, True)
              time.sleep(0.1)
              GPIO.output(BUZZO, False)
              time.sleep(0.5)
              lcd_string('Time remaining:',LCD_LINE_1)
              lcd_string('2',LCD_LINE_2)
              time.sleep(1)
              lcd_string('Time remaining:',LCD_LINE_1)
              lcd_string('1',LCD_LINE_2)
              time.sleep(1)
              lcd_string('LOCKED', LCD_LINE_1)
              lcd_string('0',LCD_LINE_2)
              GPIO.output(GREEN, False)
              GPIO.output(RED, True)
              GPIO.output(GREENIN, False)
              GPIO.output(REDIN, True)
              GPIO.output(LOCK, True)
              GPIO.output(BUZZC, True)
              time.sleep(1.3)
              GPIO.output(BUZZC, False)
              time.sleep(3)
              GPIO.output(RED, False)
              GPIO.output(GREEN, False)
              GPIO.output(REDIN, False)
              GPIO.output(GREENIN, False)
              
      except Exception as e:
          lcd_string('Operation failed!',LCD_LINE_1)
          lcd_string(str(e),LCD_LINE_2)

main()
GPIO.output(LOCK, True)
GPIO.output(LED_ON, False)
          
while True:
  #Pir State
  pirState = GPIO.input(pir2)
  #Master Buttons
  YBUTT2.when_pressed = RELAY.off 
  YBUTT2.when_released = RELAY.on
  GBUTT2.when_pressed = RELAY.off
  GBUTT2.when_released = RELAY.on
  #Pir Controls
  if (pirState == False):
    master()
  elif (pirState == True):
    GPIO.output(LED_ON, True)
    
lcd_byte(0x01, LCD_CMD)
lcd_string("Goodbye!",LCD_LINE_1)
lcd_string("",LCD_LINE_2)
GPIO.cleanup()
