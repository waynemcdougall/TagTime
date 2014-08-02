# Generate random ping times (compare util.pl)

import math
import time
import settings

IA = 16807  # constant used for RNG (see p37 of Simulation by Ross)
IM = 2147483647  # constant used for RNG (2^31-1)
seed = settings.seed  # default 666;  stores RNG state
initseed = seed

# ran0 random number generator
def ran0():
  global seed
  seed = (IA * seed) % IM
  return seed

# Random variable from uniform distribution on (0,1)
def ran01():
  return ran0() / float(IM)

# Exponential random variable with parameter 1/gap
def exprand():
  return -1 * settings.gap * math.log(ran01())

# Takes previous ping time, returns next ping time (unix timestamp)
def nextping(prev):
  return max(prev + 1, int(round(prev + exprand())))

# Find last scheduled ping before time t (unix timestamp)
def prevping(t):
  global seed
  seed = initseed
  nxtping = 1184083200  # the beginning of time
  lstping = nxtping
  lstseed = seed
  while (nxtping < t):
    lstping = nxtping
    lstseed = seed
    nxtping = nextping(nxtping)
  seed = lstseed
  return lstping

# Returns a list of upcoming ping times (truncated unix timestamps),
# starting at current time by default, up until N days (24 h periods)
# from start time. Note that Mailgun allows scheduling for max 3 days
# in advance.
def upcoming_pings(N = 2, start_time = int(time.time())):
  N = N * 60 * 60 * 24  # convert to sec
  last_ping = prevping(start_time)
  pings = [0] * int(2 * N / settings.gap)  # more than enough safety
  for i in range(len(pings)):
    if i == 0:
      pings[i] = nextping(last_ping)
    else:
      pings[i] = nextping(pings[i - 1])
    if pings[i] > start_time + N: 
      break
  return [x for x in pings if x != 0]
