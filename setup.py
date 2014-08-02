# Some setup: schedule first batch of ping emails, create pending.log

import io
import sys

import pings
import mailgun
import settings

# Create pending.log if doesn't exist, else change nothing
io.open('pending.log', 'a').close()

with io.open('pending.log', 'r') as f:
  pending = f.read()
if pending != u'':
  print "Error: pending.log not empty. You likely ran setup before."
  sys.exit(1)

# Compute upcoming ping times and schedule emails
upcoming = pings.upcoming_pings(settings.ndays)
for i in upcoming:
  mailgun.schedule_bot_email(i)

print 'Scheduled %s bot emails.' % len(upcoming)

pending = [unicode(str(x), 'utf-8') for x in upcoming]
with io.open('pending.log', 'w', newline = '') as f:
  f.write('\n'.join(pending) + '\n')

print """Updated pending.log.
Setup complete. Manually run or schedule update.py at least daily to \
keep things going."""
