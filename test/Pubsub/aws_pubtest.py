import time
from datetime import datetime
import awsIOT_lib

#### AWS Cert Files Publish#### 
awshost = "xxxxxxxxxx-ats.iot.us-west-2.amazonaws.com"      # Endpoint
awsport = 8883                                              # Port no.
clientId = "Smart_Lock_Client"                                     # Thing_Name
thingName = "Smart_Lock_Client"                                    # Thing_Name
caPath = "/home/pi/Desktop/Smart-Doorlock/Components/Cred/Lock_smart/AmazonRootCA1.pem"                    # Root_CA_Certificate_Name
certPath = "/home/pi/Desktop/Smart-Doorlock/Components/Cred/Lock_smart/xxxxxxxxxx-certificate.pem.crt"     # <Thing_Name>.cert.pem
keyPath = "/home/pi/Desktop/Smart-Doorlock/Components/Cred/Lock_smart/xxxxxxxxxx-private.pem.key"          # <Thing_Name>.private.key

#Objects
thing = awsIOT_lib.awsIOT(awshost, awsport, clientId, thingName, caPath, certPath, keyPath)

now = datetime.now()

dt_string = now.strftime("%d/%m/%Y_%H:%M:%S")

date = now.date()

unix = datetime.timestamp(now)

thing.publish("Smart_Lock", thing.createPayload("Kevin", "index", 100, "Open", dt_string, int(unix), str(date)))
