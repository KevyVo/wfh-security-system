from gpiozero import LED, Button
import RPi.GPIO as GPIO
import lock_lib

##def hello():
##    print("Held the button for 3 seconds")
    
l1 = lock_lib.lock(27, 16, 19, 26, 17, 21, 20, 5)

GButt = Button(6)


print(l1.getReed())

while True:
    GButt.when_pressed = l1.inExit

    
    
