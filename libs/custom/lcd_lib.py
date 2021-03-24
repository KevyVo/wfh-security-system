#!/usr/bin/env python
# -*- coding: utf-8 -*-

import time
import RPi.GPIO as GPIO

class lcd:

    def __init__(self, RS, E, D4, D5, D6, D7, ON):
        #GPIO PINS
        self.RS = RS
        self.E = E
        self.D4 = D4
        self.D5 = D5
        self.D6 = D6
        self.D7 = D7
        self.ON = ON
        # Define some device constants
        self.__LCD_WIDTH = 16    # Maximum characters per line
        self.__LCD_CHR = True
        self.__LCD_CMD = False

        self.__LCD_LINE_1 = 0x80 # LCD RAM address for the 1st line
        self.__LCD_LINE_2 = 0xC0 # LCD RAM address for the 2nd line

        # Timing constants
        self.__E_PULSE = 0.0005
        self.__E_DELAY = 0.0005

        #Initialising functions
        self.setup()
        print("The GPIO pins for display has been setup.")
        # Initialise display
        self.lcd_init()


    def setup(self):
        GPIO.setwarnings(False)
        GPIO.setmode(GPIO.BCM)       # Use BCM GPIO numbers
        GPIO.setup(self.E, GPIO.OUT)  # E
        GPIO.setup(self.RS, GPIO.OUT) # RS
        GPIO.setup(self.D4, GPIO.OUT) # DB4
        GPIO.setup(self.D5, GPIO.OUT) # DB5
        GPIO.setup(self.D6, GPIO.OUT) # DB6
        GPIO.setup(self.D7, GPIO.OUT) # DB7
        GPIO.setup(self.ON, GPIO.OUT) # Backlight enable

    def lcd_init(self):
        # Initialise display
        self.lcd_byte(0x33,self.__LCD_CMD) # 110011 Initialise
        self.lcd_byte(0x32,self.__LCD_CMD) # 110010 Initialise
        self.lcd_byte(0x06,self.__LCD_CMD) # 000110 Cursor move direction
        self.lcd_byte(0x0C,self.__LCD_CMD) # 001100 Display On,Cursor Off, Blink Off
        self.lcd_byte(0x28,self.__LCD_CMD) # 101000 Data length, number of lines, font size
        self.lcd_byte(0x01,self.__LCD_CMD) # 000001 Clear display
        time.sleep(self.__E_DELAY)

    def lcd_byte(self, bits, mode):
        # Send byte to data pins
        # bits = data
        # mode = True  for character
        #        False for command

        GPIO.output(self.RS, mode) # RS

        # High bits
        GPIO.output(self.D4, False)
        GPIO.output(self.D5, False)
        GPIO.output(self.D6, False)
        GPIO.output(self.D7, False)
        if bits&0x10==0x10:
            GPIO.output(self.D4, True)
        if bits&0x20==0x20:
            GPIO.output(self.D5, True)
        if bits&0x40==0x40:
            GPIO.output(self.D6, True)
        if bits&0x80==0x80:
            GPIO.output(self.D7, True)

        # Toggle 'Enable' pin
        self.lcd_toggle_enable()

        # Low bits
        GPIO.output(self.D4, False)
        GPIO.output(self.D5, False)
        GPIO.output(self.D6, False)
        GPIO.output(self.D7, False)
        if bits&0x01==0x01:
          GPIO.output(self.D4, True)
        if bits&0x02==0x02:
          GPIO.output(self.D5, True)
        if bits&0x04==0x04:
          GPIO.output(self.D6, True)
        if bits&0x08==0x08:
          GPIO.output(self.D7, True)

        # Toggle 'Enable' pin
        self.lcd_toggle_enable()

        

    #Enable the display frequency
    def lcd_toggle_enable(self):
        # Toggle enable
        time.sleep(self.__E_DELAY)
        GPIO.output(self.E, True)
        time.sleep(self.__E_PULSE)
        GPIO.output(self.E, False)
        time.sleep(self.__E_DELAY)

    #Used to print Words to display
    def lcd_string(self, message, line):

        if (line==1):
            line = self.__LCD_LINE_1
        elif (line==2):
            line = self.__LCD_LINE_2
        
        messageb = message
    
    # Send string to display
        message = message.ljust(self.__LCD_WIDTH," ")

        self.lcd_byte(line, self.__LCD_CMD)

        for i in range(self.__LCD_WIDTH):
            self.lcd_byte(ord(message[i]),self.__LCD_CHR)

    #Use to control the blacklight ON/OFF
    def backlight(self, state):
        if (state==True):
            GPIO.output(self.ON, True)
        elif (state == False):
            GPIO.output(self.ON, False)
