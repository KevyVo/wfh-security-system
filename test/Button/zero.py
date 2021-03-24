from gpiozero import LED, Button
from signal import pause

rled = LED(19)
gled = LED(26)
ybutt = Button(13)
gbutt = Button(6)
relay = LED(17)

ybutt.when_pressed = relay.off
ybutt.when_released = relay.

gbutt.when_pressed = gled.on
gbutt.when_released = gled.off

pause()
