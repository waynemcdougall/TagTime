# For debugging: prints time of most recent past ping

import time
import datetime
import pings

tm = pings.prevping(int(time.time()))
print datetime.datetime.fromtimestamp(tm).strftime('%a, %d %b %Y %H:%M:%S')
