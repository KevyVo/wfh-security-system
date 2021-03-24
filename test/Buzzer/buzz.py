import time
import RPi.GPIO as GPIO

GPIO.setmode(GPIO.BCM)

Reed = 5
GPIO.setup(Reed, GPIO.IN)

while(True):
    time.sleep(0.5)
    print (GPIO.input(Reed))

