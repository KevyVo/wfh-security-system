import GCAL_lib
from datetime import datetime

now = datetime.now()
sysDate = now.strftime("%Y-%m-%d")
print(sysDate)
cal = GCAL_lib.Gcal()
print(cal.nextEvent(sysDate))

