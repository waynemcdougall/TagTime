import requests
import re
import string
from collections import namedtuple
from email.utils import formatdate

import settings
import misc

# Schedules a bot email to be sent at a certain time (unix timestamp)
def schedule_bot_email(delivery_time):
  delivery_time_string = formatdate(delivery_time, localtime = True)

# If you change the body, make sure the regular expressions in
# parse_replies() still correctly match the smiley face (string
# marking end of reply) and the timestamp.
  body = """What were you doing RIGHT AT THE MOMENT you got this \
email? (around %s)
Use this format: tag1 tag2 tag3 :)
\nOnly alphanumeric tags please, 43 or fewer characters, and do \
include the smiley face at the end of your reply. If you have any \
prior unanswered pings, you can enter multiple sets of tags, \
separated by commas, in chronological order. You can repeat sets of \
tags by shorthand like so (for 3 times and indefinitely, respectively):
work mtg ...3 :)
slp ... , eat :)
\nDETAILS: Multiple sets of tags are really read from last to first. \
The last set is always your reply to the current ping (this email). \
Then the previous set is read and matched to the previous ping, and \
so on. So if you reply with too few sets, the oldest pings stay \
unanswered. If you reply with too many, the extra sets at the \
beginning are ignored. The repetition shorthands act as if they \
actually replicated those sets of tags, so for example everything \
before a set ending in "..." is ignored!
\nPing timestamp: %s (%s)""" %(
  delivery_time_string[17:-9], delivery_time, delivery_time_string)
  
  return requests.post(
    'https://api.mailgun.net/v2/%s/messages' % settings.domain,
    auth=('api', settings.auth_key_mg),
    data={'from': "TagTime Bot <%s>" % settings.bot_email,
        'to': [settings.my_email],
        'subject': "It's tag time!",
        'text': body,
        'o:deliverytime': delivery_time_string})

# To access an email temporarily stored by Mailgun, we need a URL from
# the Events API. We can then get the email as a JSON object with this
# URL via the Messages API.
#
# This function returns a list of unicode URLs to stored ping replies.
# It returns the URL of every stored email sent from my email address,
# from the timestamp of the oldest pending ping to the present, in
# chronological order of email send time.
def event_urls(t_0, t_1):
  events = requests.get(
    'https://api.mailgun.net/v2/%s/events' % settings.domain,
    auth=('api', settings.auth_key_mg),
    params={'begin': formatdate(t_0),
            'end': formatdate(t_1),
            'limit': 100,
              # max 100 items per request; ok with use every 24-48 h
            'event': 'stored'}).json()
  
  urls = [u''] * len(events['items'])
  for i in range(len(events['items'])):
    pat = re.compile(settings.my_email)
    if pat.search(events['items'][i]['message']['headers']['from']):
      # include only URLs to emails sent from settings.my_email
      urls[i] = events['items'][i]['storage']['url']
  
  return [x for x in urls if x != u'']

# GETs and parses emails via the Messages API.
# Returns a named tuple containing three lists:
#
# tag_sets: contains every tag set (formatted) from every ping reply
# (list of lists of strings)
#
# reps: number of repetitions of every tag set from every ping reply
# (list of lists of integers; no-repetition default is 1; bounded
# repetitions are >= 1; unbounded repetition is 0)
#
# times: timestamp of the ping that each reply replies to
# (list of integers)
Parsed_batch = namedtuple('Parsed_batch', 'tag_sets reps times')
def parse_replies(urls):
# TODO:
# Add checks for invalid / empty replies
# Consider deleting stored emails after reading
  if len(urls) == 0:
    return Parsed_batch([], [], [])
  
  tag_sets = [['']] * len(urls)
  reps = [[1]] * len(urls)
  timestamps = [0] * len(urls)
  for i in range(len(urls)):
    msg = requests.get(urls[i], auth=('api', settings.auth_key_mg)).json()
    plaintext = str(msg['body-plain'])
    pat = re.compile('.*?:\)')
    reply_text = pat.search(plaintext).group()[:-2]
      # string: comma-separated sets of space-separated tags
    
    sets = string.split(reply_text, sep = ",")
      # list of strings: list of space-separated tags
    sets = [x for x in sets if x != '']  # shouldn't be necessary
    tag_sets[i] = [misc.format_tags(x) for x in sets]
      # formatted strings for log file
    
    nrep = [misc.nrep(x) for x in sets]
    reps[i] = nrep
    
    pat = re.compile('timestamp: [0-9]+ \(')
    match = pat.search(plaintext)
    if match:
      timestamp = match.group()
      timestamps[i] = int(timestamp[11:-2])

  return Parsed_batch(tag_sets, reps, timestamps)
