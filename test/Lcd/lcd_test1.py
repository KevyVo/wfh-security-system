import RPi.GPIO as GPIO
import lcd_lib
import time

d1 = lcd_lib.lcd(7, 8, 25, 24, 23, 18, 15)
d1.backlight(True)
d1.lcd_string("Hello", 1)
d1.lcd_string("World2", 2)
