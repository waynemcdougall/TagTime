# Main settings

# These shouldn't need changing
gap = 60 * 45  # mean gap between pings in seconds
seed = 666  # random seed of RNG in pings.py
ndays = 2
  # Max days (24 h periods) ahead to schedule pings (Mailgun max is 3)

# Mailgun/email stuff
auth_key_mg = 'key-1234'  # your Mailgun API key
domain = 'sandbox12345.mailgun.org'
  # domain to send pings from (I use my Mailgun sandbox domain)
bot_email = 'tagtime@sandbox12345.mailgun.org'
  # ping sender email address
my_email = 'your@email.com' # where you want to receive pings

# Beeminder stuff
username = 'username'
goals = ['goal', 'etc']
  # List of slugs of all your TagTime-fed Beeminder goals
  # (Slugs aren't your goal 'titles'. A slug is what comes after
  # /username/goals/ in the URL of your goal graph). You'll need
  # to specify all of these in settings.pl
