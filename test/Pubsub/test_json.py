# importing libraries
import awsIOT_lib
from datetime import datetime
import time

#### Change following parameters #### 
awshost = "xxxxxxxxxx-ats.iot.us-west-2.amazonaws.com"      # Endpoint
awsport = 8883                                              # Port no.   
clientId = "Smart_Lock_Client"                                     # Thing_Name
thingName = "Smart_Lock_Client"                                    # Thing_Name
caPath = "/home/pi/Desktop/Smart-Doorlock/Components/Cred/AmazonRootCA1.pem"                    # Root_CA_Certificate_Name
certPath = "/home/pi/Desktop/Smart-Doorlock/Components/Cred/xxxxxxxxxx-certificate.pem.crt"     # <Thing_Name>.cert.pem
keyPath = "/home/pi/Desktop/Smart-Doorlock/Components/Cred/xxxxxxxxxx-private.pem.key"          # <Thing_Name>.private.key

thing = awsIOT_lib.awsIOT(awshost, awsport, clientId, thingName, caPath, certPath, keyPath)
time.sleep(3)
# datetime object containing current date and time
now = datetime.now()
dt_string = now.strftime("%d/%m/%Y_%H:%M:%S")
thing.publish("Smart_Lock", thing.createPayload("Kevin", "Thumb", 100, "Open", dt_string))
