from datetime import datetime

#Get time and date right now

#This is a string type
#now = datetime.now().isoformat(timespec='seconds')

#This is a datetime.datetime object
now = datetime.now()

print("This is the first datetime.now():", now)

timestamp = datetime.timestamp(now)
print("This is the first timestamp on now in UNIX:", timestamp)


covertTS = datetime.fromtimestamp(timestamp)

print ("This is the reconverted from the UNIX timestamp:", covertTS)