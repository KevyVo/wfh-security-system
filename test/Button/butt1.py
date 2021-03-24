import  RPi.GPIO as GPIO
import time

GPIO.setmode(GPIO.BCM)
GPIO.setup(6, GPIO.IN,pull_up_down=GPIO.PUD_UP)

while True:
    inputValue = GPIO.input(6)
    if (inputValue == False):
        print("Button press ")
    time.sleep(0.3)
