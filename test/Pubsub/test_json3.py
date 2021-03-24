# importing libraries
import os
import string
import json
from time import sleep
from datetime import datetime

def createPayload(userID, finger, accuracy, door, timestamp):
        payload0 = "{"
        payload1 = "\"userID\": \""
        payload2 = "\", \"Finger\": \""
        payload3 = "\", \"Accuracy\":"
        payload4 = ", \"Door\":" "\""
        payload5 = "" "\", \"Timestamp\":" "\""
        payload6 = "\"""}"
        payloadmsg = "{} {} {} {} {} {} {} {} {} {} {} {}".format(payload0, payload1, userID, payload2, finger, payload3, accuracy, payload4, door, payload5, timestamp, payload6)
        payloadmsg = json.dumps(payloadmsg)
        payloadJson = json.loads(payloadmsg)
        return (payloadJson)


def createPayload2(userID, finger, accuracy, door, timestamp, unix, date):
    data = {
        'userID': userID,
        'Finger': finger,
        'Accuracy': accuracy,
        'Door': door,
        'Timestamp':timestamp,
        'unix': unix,
        'date': date
    }
    payload = json.dumps(data)
    return payload

# datetime object containing current date and time
now = datetime.now()
date = now.date()
unix = datetime.timestamp(now)
dt_string = now.strftime("%d/%m/%Y_%H:%M:%S")
print(type(dt_string))
dev = createPayload("Kevin", "Index", 100, "Open", dt_string)
print(dev)
dev2 = createPayload2("Kevin", "Index", 100, "Open", dt_string, int(unix), str(date))
print(dev2)