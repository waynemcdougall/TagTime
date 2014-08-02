# Misc functions: date/time, log file formatting, repetition shorthands

import datetime
import re
import string

# Unix timestamp to string (datetime format used in TagTime log file)
def unix_to_log(timestamp):
  log_time = datetime.datetime.fromtimestamp(
    timestamp).strftime('%Y.%m.%d %H:%M:%S %a')
  log_time = '[' + log_time.upper() + ']'
  return log_time

# Takes an unformatted tag set (string) from a ping reply. Discards
# duplicate tags and repetition shorthands + everything following
# them. Returns formatted tag set (string) for log file.
def format_tags(ts):
  tags = string.split(ts, sep = ' ')
  tags = [x for x in tags if x != '']
  if rep_sh_index(tags) >= 0:
    tags = tags[:rep_sh_index(tags)]
  
  uniques = []
  [uniques.append(x) for x in tags if x not in uniques]
  return pad(' '.join(uniques))

# Pads a string with spaces up to default length 43 (for log file)
def pad(s, length = 43):
  s = str(s) + ' ' * length
  return s[:length]

# Checks if any element of a list of strings matches the repetition
# shorthand pattern '...' at the beginning of the string. Returns -1
# if no match, otherwise returns index of first matching element.
def rep_sh_index(ls):
  pat = re.compile('\.\.\.')
  matches = [pat.match(x) for x in ls]
  is_match = [x != None for x in matches]
  if any(is_match):
    return is_match.index(True)
  else:
    return -1

# Returns number of repeats for a tag set (string) based on the first
# matched repetition shorthand:
#  1 if no repetition shorthand or '...1' or '...0'
#  n for bounded repeat '...n' where n >= 1
#  0 for unbounded repeat '...'
def nrep(ts):
  pat = re.compile('\.\.\.[0-9]*')
  match = pat.search(ts)
  if match:
    n = match.group()[3:]
    if n == '':
      return 0
    elif int(n) == 0:
      return 1
    else:
      return int(n)
  else:
    return 1
