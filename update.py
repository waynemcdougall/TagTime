# This script should be run daily. It reads and logs ping replies
# stored by Mailgun, schedules a new batch of ping emails, and
# updates your TagTime-fed Beeminder goals.

import time
import io
import string
import sys
import os
#import ftplib  # for FTP upload only

import misc
import mailgun
import settings
import pings

if not os.path.isfile('pending.log'):
  print "pending.log does not exist. Did you run setup.py?"
  sys.exit(1)

# pending.log contains timestamps of all pings that are pending
# (scheduled to send but not yet read to log file, whether because
# not yet replied to or because the stored replies were not yet 
# read and logged).
with io.open('pending.log', 'r') as f:
  pending = f.read()
pending = string.split(pending, sep = '\n')
pending = [int(x) for x in pending if x != '']

if pending == []:
  print "pending.log is empty. Did you run setup.py?"
  sys.exit(1)

if pending != sorted(pending):
  print "ERROR: Timestamps in pending.log not in chronological order!"
  print "Not touching this one..."
  sys.exit(1)

# Get and parse pending ping replies stored by Mailgun
time_0 = min(pending)
time_1 = int(time.time())
urls = mailgun.event_urls(time_0, time_1)
replies = mailgun.parse_replies(urls)

print 'Fetched %s ping replies from Mailgun.' % len(replies.times)

# Dump email contents (for debugging)
with io.open('emaildump.txt', 'w') as f:
  f.write(unicode(str(replies), 'utf-8'))

# Empty check
if (replies.tag_sets == []) | (replies.reps == []) | (replies.times == []):
  print 'No ping replies available to be logged.'
  
  # Schedule new batch of emails
  upcoming = pings.upcoming_pings(settings.ndays)
  to_schedule = [x for x in upcoming if x not in pending]
  for i in to_schedule:
    mailgun.schedule_bot_email(i)
  print 'Scheduled %s bot emails.' % len(to_schedule)
  sys.exit(0)

# Generate TagTime log file from replies

log_timestamps = [x for x in pending if x <= max(replies.times)]
  # List of consecutive timestamps from oldest pending to most
  # recent ping that was replied to. Note that the latter,
  # max(replies.times), need not equal replies.times[-1] as
  # the replies need not be sent in the order of the ping
  # times.
  #
  # Note, however, that after the code herein is run to log
  # replies up to some timestamp t, any subsequent replies to
  # earlier pings won't be read because the respective timestamps
  # are no longer in pending.log.
log_tag_sets = [''] * len(log_timestamps)

# All those rules about how to reply to multiple pings in a single
# email are instantiated in the following:
for i in range(len(replies.times)):
# Loop over emails
  if replies.times[i] in log_timestamps:
    log_index = log_timestamps.index(replies.times[i])
  else:
    continue
  
  for j in range(len(replies.tag_sets[i]))[::-1]:
  # Loop over tag sets in each email, in reverse order
    nr = replies.reps[i][j]
    if nr == 1:
      if log_tag_sets[log_index] == '':
        log_tag_sets[log_index] = replies.tag_sets[i][j]
        log_index -= 1
      else:
        break
    elif nr > 1:
      lim = log_index - nr + 1
      while (log_tag_sets[log_index] == '') & (log_index >= lim):
        log_tag_sets[log_index] = replies.tag_sets[i][j]
        log_index -= 1
      if log_tag_sets[log_index] != '':
        break
    elif nr == 0:
      while (log_tag_sets[log_index] == '') & (log_index >= 0):
        log_tag_sets[log_index] = replies.tag_sets[i][j]
        log_index -= 1
      break

for i in range(len(log_tag_sets)):
  if log_tag_sets[i] == '':
    log_tag_sets[i] = misc.pad('RETRO')

log_timestamps_text = [misc.unix_to_log(x) for x in log_timestamps]

log_lines = [u''] * len(log_timestamps)
for i in range(len(log_timestamps)):
  log_lines[i] = unicode(''.join([str(log_timestamps[i]), ' ',
                                  log_tag_sets[i],
                                  log_timestamps_text[i]]),
                        'utf-8')

# Append log file (if doesn't exist, create and write)
with io.open('%s.log' % settings.username, 'a', newline = '') as f:
  f.write('\n'.join(log_lines) + '\n')

print 'Updated %s.log file.' % settings.username

# Optional: Upload log file to FTP server (used by the Shiny app)
# you'll have to import ftplib (see above)
#with io.open('%s.log' % settings.username, 'r', newline = '') as f:
#  ftp = ftplib.FTP("ftp.your.server")  # CHANGEME
#  ftp.login("username", "password")  # CHANGEME
#  ftp.storlines("STOR path/to/destination", f)  # CHANGEME
#print 'Uploaded %s.log to FTP server.' % settings.username

# Optional: Copy log file to another location (e.g. Dropbox public folder)
#alt_path = 'alternative\path\to\log\username.log'  # CHANGEME
#with io.open('%s.log' % settings.username, 'r', newline = '') as f:
#  logfile = f.read()
#with io.open(alt_path, 'w', newline = '') as f:
#  f.write(logfile)
#print 'Copied log file to %s' % alt_path

# Schedule upcoming emails that aren't already pending
pending = [x for x in pending if x not in log_timestamps]
upcoming = pings.upcoming_pings(settings.ndays)
to_schedule = [x for x in upcoming if x not in pending]
for i in to_schedule:
  mailgun.schedule_bot_email(i)

print 'Scheduled %s bot emails.' % len(to_schedule)

# Append scheduled ping timestamps to pending, write to pending.log
pending = pending + to_schedule
pending = [unicode(str(x), 'utf-8') for x in pending]
with io.open('pending.log', 'w', newline = '') as f:
  f.write('\n'.join(pending) + '\n')

print 'Updated pending.log file.'

# Update TagTime-fed Beeminder goals
print 'Sending data to Beeminder...'
for i in settings.goals:
  os.system("perl beeminder.pl %s.log %s/%s" % (settings.username,
    settings.username, i))
