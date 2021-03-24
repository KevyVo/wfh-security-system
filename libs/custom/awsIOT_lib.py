# importing libraries
import paho.mqtt.client as paho
import os
import socket
import ssl
import random
import string
import json
from time import sleep
from random import uniform

class awsIOT:

    def __init__(self, awshost, awsport, cilentid, thingname, caPath, certPath, keyPath):
        self.connflag = False
        self.mqttc = paho.Client()                                       # mqttc object
        self.mqttc.on_connect = self.on_connect                               # assign on_connect func
        self.mqttc.on_message = self.on_message                               # assign on_message func
        self.mqttc.tls_set(caPath, certfile=certPath, keyfile=keyPath, cert_reqs=ssl.CERT_REQUIRED, tls_version=ssl.PROTOCOL_TLSv1_2, ciphers=None)  # pass parameters
        self.mqttc.connect(awshost, awsport, keepalive=60)               # connect to aws server
        self.mqttc.loop_start()                                          # Start the loop

    def on_connect(self, client, userdata, flags, rc):                # func for making connection
        self.connflag
        print ("Connected to AWS")
        connflag = True
        print("Connection returned result: " + str(rc) )

    def on_message(self, client, userdata, msg):                      # Func for Sending msg
        print(msg.topic+" "+str(msg.payload))

    def getMAC(self, interface='eth0'):
        # Return the MAC address of the specified interface
        try:
            str = open('/sys/class/net/%s/address' %interface).read()
        except:
            str = "00:00:00:00:00:00"
        return str[0:17]

    def getEthName(self):
        # Get name of the Ethernet interface
        try:
            for root,dirs,files in os.walk('/sys/class/net'):
                for dir in dirs:
                    if dir[:3]=='enx' or dir[:3]=='eth':
                        interface=dir
        except:
            interface="None"
        return interface

    def createPayload(self, userID, finger, accuracy, door, timestamp, unix, date):
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

    def publish(self, topic, payload):
        self.mqttc.publish(topic, payload , qos=1)        # topic: Publish Log
        print("msg sent: " + topic ) # Print topic
        print(payload)
