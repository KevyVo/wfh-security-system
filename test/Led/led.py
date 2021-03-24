import RPi.GPIO as GPIO
import time
from gpiozero import LED, Button
from signal import pause

Red= 19
Green= 26
ybutt= 13
gbutt= 6
FAN = LED(5)
YBUTT2 = Button(13)


GPIO.setmode(GPIO.BCM)
GPIO.setup(Red, GPIO.OUT)
GPIO.setup(Green, GPIO.OUT)
GPIO.setup(gbutt, GPIO.IN, pull_up_down=GPIO.PUD_UP)

def red():
    GPIO.output(Red, True)
    time.sleep(1.5)
    GPIO.output(Red, False)

def green():
    GPIO.output(Green, True)
    time.sleep(1.5)
    GPIO.output(Green, False)

while True:
    buttonState = GPIO.input(ybutt)
    buttonState2 = GPIO.input(gbutt)
    ybutt2.when_pressed = FAN.off
    ybutt2.when_released = FAN.on
    if buttonState == False:
        red()
    elif buttonState2 == False:
        green()
    else:
        pass

GPIO.cleanup()
