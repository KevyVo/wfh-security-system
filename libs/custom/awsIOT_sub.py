# importing libraries
import paho.mqtt.client as paho
import os
import socket
import ssl

class awsIOT_subscribe:
    def __init__(self, awshost, awsport, cilentid, thingname, caPath, certPath, keyPath, topic):
        self.mqttc = paho.Client()                                       # mqttc object
        self.topic = topic                                                 #topic name
        self.mqttc.on_connect = self.on_connect                               # assign on_connect func
        self.mqttc.on_message = self.on_message                               # assign on_message func
        self.mqttc.tls_set(caPath, certfile=certPath, keyfile=keyPath, cert_reqs=ssl.CERT_REQUIRED, tls_version=ssl.PROTOCOL_TLSv1_2, ciphers=None)   # pass parameters
        self.mqttc.connect(awshost, awsport, keepalive=60)               # connect to aws server
        self.mqttc.loop_start()                                        # Start receiving in loop
        self.value = ""

    def on_connect(self, client, userdata, flags, rc):                # func for making connection
        print("Connection returned result: " + str(rc) )
        # Subscribing in on_connect() means that if we lose the connection and
        # reconnect then subscriptions will be renewed.
        client.subscribe(self.topic , 1 )                              # Subscribe to all topics
 
    def on_message(self, client, userdata, msg):                      # Func for receiving msgs
          firstedit = str(msg.payload)
          secondedit = firstedit.split(":")
          thirdedit = secondedit[1].split("}")
          self.value = thirdedit[0]
          
    def getPayload (self):
        return self.value
