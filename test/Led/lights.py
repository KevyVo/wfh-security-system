import RPi.GPIO as GPIO
import time

vib1= 18
vib2= 17
GPIO.setwarnings(False)

GPIO.setmode(GPIO.BCM)
GPIO.setup(vib1, GPIO.OUT)
GPIO.setup(vib2, GPIO.OUT)


GPIO.output(vib1, True)
#GPIO.output(vib2, True)
time.sleep(1)
GPIO.output(vib1, False)
#GPIO.output(vib2, False)
time.sleep(1)
GPIO.output(vib1, True)
#GPIO.output(vib2, True)
time.sleep(1)
GPIO.output(vib1, False)
#GPIO.output(vib2, False)
time.sleep(1)

GPIO.cleanup()
