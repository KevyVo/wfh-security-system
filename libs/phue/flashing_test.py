#!/usr/bin/python

from phue import Bridge
import logging
import time 
logging.basicConfig()

b = Bridge()# Your ip

# If the app is not registered and the button is not pressed, press the button and call connect() (this only needs to be run a single$
b.connect()

#Change the light state
for i in range(5):
    b.set_light(1, 'on', True)
    time.sleep(2)
    b.set_light(1, 'on', False)
    time.sleep(1)
