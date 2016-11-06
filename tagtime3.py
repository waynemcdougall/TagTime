#!/usr/bin/env python3

import time,random,tweepy,sqlite3

def get_api(cfg):
  auth = tweepy.OAuthHandler(cfg['consumer_key'], cfg['consumer_secret'])
  auth.set_access_token(cfg['access_token'], cfg['access_token_secret'])
  return tweepy.API(auth)

def pingwaittime():
  return min(1+int(random.expovariate(1/gap)),86400) # ping at least once a day

def besttagguesses():
  codes=['q','w','e','r','t','y','u','i','o','p']
  #TODO generate suggested tags dynamically
  tags=["slp","prog"]
  x=""
  for i in range (0,min(len(tags),len(codes))):
    x+=" "+codes[i]+"="+tags[i]
  return tags[0],x

def generatecode():
  newcodetimelimit = time.time() - 6 * 7 * 24 * 60 * 60 / gap # unique code over 6 week period
  while 1:
    code = "%04d" % (random.randint(0,10000),)
    cursor.execute('select * from pings where code=? and time<?',(code,newcodetimelimit))
    rows = [row for row in cursor]
    if len(rows) == 0:
      return code

def issueping(pingtime):
  code=generatecode()
  besttag,tags = besttagguesses()
  dm = ("What are you doing on "+time.strftime("%a at %H:%M:%S", time.localtime(pingtime)) + "? Code:" + code
     + "\nEnter tag or" + tags)
  storeping (pingtime,besttag,code) 
  while 1:
    try:
      api.send_direct_message(user = username, text = dm)
      return
    except tweepy.TweepError:
      time.sleep(1)

def storeping(p, tag, code):
  cursor.execute('insert into pings values (?, ?, null, ?)',
                        (p, tag , code))
  conn.commit()

def storetag(tag,username):
  cursor.execute('update pings set response=?,response_time=? where response_time is null order by time limit 1',(tag,time.time()))
  conn.commit()

#https://www.digitalocean.com/community/tutorials/how-to-authenticate-a-python-application-with-twitter-using-tweepy-on-ubuntu-14-04
# cfg = { 
#    "consumer_key"        : "www",
#    "consumer_secret"     : "xxx",
#    "access_token"        : "yyy",
#    "access_token_secret" : "zzz"
#    }

import twitter_secrets.py
api = get_api(cfg)
gap = 45 * 60 # average gap between pings of 45 minutes

username="waynemcdougall"
conn = sqlite3.connect('tagtime.{0}.db'.format(username))
cursor = conn.cursor()
cursor.execute('''create table if not exists pings
      (time bigint primary key, response text, response_time bigint, code int)''');
conn.commit()
cursor.execute('''create index if not exists codeidx on pings (code)''');
conn.commit()
cursor.execute('''select time from pings order by time desc limit 1''');
rows = [row for row in cursor]
if len(rows) == 0:
  nextping = int(time.time())
else:
  nextping = rows[0][0]
nextping += pingwaittime()
while 1:
  try:
    myDirectMsgs = api.direct_messages()
  except tweepy.TweepError:
    continue
  for status in reversed(myDirectMsgs):
    storetag(status.text.lower(),status.sender.screen_name)
    api.destroy_direct_message(status.id)
  x = nextping - time.time()
  if x > 0: 
    time.sleep(min(x,60))
  else:
    issueping (nextping)
    nextping += pingwaittime()

