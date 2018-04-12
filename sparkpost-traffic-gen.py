#!/usr/bin/env python3
#
# Simple SparkPost Traffic Generator
# Sends emails towards the Solution Engineering smart bounce/sink server domains
#
# Configurable traffic volume per minute
#
import random, os, time
from sparkpost import SparkPost
from sparkpost.exceptions import SparkPostAPIException


# -----------------------------------------------------------------------------------------
# Configurable recipient domains, recipient substitution data, html clickable link, campaign, subject etc
# -----------------------------------------------------------------------------------------
recipDomains = [
    "clicky-sink.trymsys.net",
    # "bouncy-sink.trymsys.net"
    #"db.deadboltinternet.com"
]

recipCities = ["Baltimore", "Boston", "London", "New York", "Paris", "Rio de Janeiro", "Seattle", "Sydney", "Tokyo" ]
recipGenders = ["female", "male"]

htmlLink = 'http://example.com/index.html'

content = [
    {'campaign': 'sparkpost-traffic-gen Todays_Sales', 'subject': 'Today\'s sales', 'linkname': 'Deal of the Day'},
    {'campaign': 'sparkpost-traffic-gen Newsletter', 'subject': 'Newsletter', 'linkname': 'More Daily News'},
    {'campaign': 'sparkpost-traffic-gen Last Minute Savings', 'subject': 'Savings', 'linkname': 'Last Minute Savings'},
    {'campaign': 'sparkpost-traffic-gen Password_Reset', 'subject': 'Password reset', 'linkname': 'Password Reset'},
    {'campaign': 'sparkpost-traffic-gen Welcome_Letter', 'subject': 'Welcome letter', 'linkname': 'Contact Form'},
    {'campaign': 'sparkpost-traffic-gen Holiday_Bargains', 'subject': 'Holiday bargains', 'linkname': 'Holiday Bargains'}
]

ToAddrPrefix = 'fakespark+'                          # prefix - random digits are appended to this.  Scott's script needs this prefix
ToName = 'traffic-generator'

sendInterval = 10                                   # minutes - tuned to suit Heroku dyno scheduler

# -----------------------------------------------------------------------------------------

def randomRecip():
    numDigits = 20                                  # Number of random local-part digits to generate
    localpartnum = random.randrange(0, 10**numDigits)
    domain = random.choice(recipDomains)
    # Pad the number out to a fixed length of digits
    addr = ToAddrPrefix+str(localpartnum).zfill(numDigits) + '@' + domain
    recip = {
        "address": addr,
        "name": ToName,
        "substitution_data": {
            "gender":  random.choice(recipGenders),
            "city": random.choice(recipCities),
        }
    }
    return recip

#
# Contents include a valid http(s) link with custom link name
def randomContents():
    c = random.choice(content)
    htmlBody = 'Click <a href="'+htmlLink+'" data-msys-linkname="' + c['linkname'] + '">' + htmlLink + '</a>'
    return c['campaign'], c['subject'], htmlBody

# Inject the messages into SparkPost for a batch of recipients, using the specified transmission parameters
def sendToRecips(sp, recipBatch, sendObj):
    print('To', str(len(recipBatch)).rjust(5, ' '),'recipients | campaign "'+sendObj['campaign']+'" | ', end='', flush=True)

    # Compose in additional API-call parameters
    sendObj.update({
        'recipients': recipBatch,
    })
    startT = time.time()
    try:
        res = sp.transmissions.send(**sendObj)                  # Unpack for the call
        endT = time.time()
        if res['total_accepted_recipients'] != len(recipBatch):
            print(res)
        else:
            print('OK - in', round(endT - startT, 3), 'seconds')
    except SparkPostAPIException as err:
        print('error code', err.status, ':', err.errors)
        exit(1)


# -----------------------------------------------------------------------------------------
# Main code
# -----------------------------------------------------------------------------------------
count = os.getenv('MESSAGES_PER_MINUTE', '1')
if count.isnumeric():
    count = int(count)
    if count <1 or count > 10000:
        print('Invalid MESSAGES_PER_MINUTE setting - must be number 1 to 10000')
        exit(1)
else:
    print('Invalid MESSAGES_PER_MINUTE setting - must be number 1 to 10000')
    exit(1)

apiKey = os.getenv('SPARKPOST_API_KEY')        # API key is mandatory
if apiKey == None:
    print('SPARKPOST_API_KEY environment variable not set - stopping.')
    exit(1)

host = os.getenv('SPARKPOST_HOST', default='api.sparkpost.com')
if not host.startswith('https://'):
    host = 'https://' + host                    # Add schema
if host.endswith('/'):
    host = host[:-1]                            # Strip /

fromEmail = os.getenv('FROM_EMAIL')
if fromEmail == None:
    print('FROM_EMAIL environment variable not set - stopping.')
    exit(1)

sp = SparkPost(api_key = apiKey, base_uri = host)
print('Opened connection to', host)

# Send every n minutes, between fractional and full traffic rate
batchSize = 100 # int( (0.25 + (0.75 * random.random())) * sendInterval * count)
recipients = []
for i in range(0, batchSize):
    recipients.append(randomRecip())

for i in [1]:
    campaign, subject, htmlBody = randomContents()
    txObj = {
        'text': 'hello world',
        'html': htmlBody,
        'subject': subject,
        'campaign': campaign,
        'track_opens':  True,
        'track_clicks': True,
        'from_email': fromEmail,
    }
    if host.endswith('e.sparkpost.com'):            # Workaround for SPE demo system
        rp = 'bounces@' + fromEmail.split('@')[1]
        txObj.update( { 'ip_pool': 'outbound', 'return_path': rp } )
    sendToRecips(sp, recipients, txObj)
print('Done')