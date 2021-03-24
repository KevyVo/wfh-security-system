from datetime import datetime
import time

def stealth():
    print("Run lights without beeps")

def normal():
    print("This will run normal now")


try:
    while True:
        now = datetime.now()
        if (now.hour < 20 and now.hour >= 8):
            print(now.hour)
            normal()

        else:
            print(now.hour)
            stealth()

        del now
        
except KeyboardInterrupt:
    print('interrupted!')
