from datetime import datetime
import time

# datetime object containing current date and time
now = datetime.now()

#now = 2020-10-31 12:11:00.160494
print("now =", now)

# dd/mm/YY H:M:S
#date and time = 31/10/2020
dt_string = now.strftime("%d/%m/%Y")
print("date and time =", dt_string)
dt_string = now.strftime("%d/%m/%Y_%H/%M/%S_")
print("date and time =", dt_string)
dt_string = now.strftime("%d/%m/%Y_%H:%M:%S")
print("date and time =", dt_string)
print(type(dt_string))




print(str(now.hour) + ":" + str(now.minute) + ":" + str(now.second))
time.sleep(2)
print(str(now.hour) + str(now.minute) + str(now.second))
print(str(now.hour))
