from gpiozero import LED
from gpiozero import MotionSensor

pir = MotionSensor(4)

while True:
    if(pir.wait_for_motion()):
        print("Motion Detected")
    if(pir.wait_for_no_motion()):
        print("Motion Stopped")
