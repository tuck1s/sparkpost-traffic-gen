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
    "mx2.deadboltemail.com",
    "mx2.deadboltemail.com",
    "mx2.deadboltemail.com",
    "mx2.deadboltemail.com",
    "mx2.deadboltemail.com",
    "mx2.deadboltemail.com",
    "mx2.deadboltemail.com",
    "mx2.deadboltemail.com",
    "mx2.deadboltemail.com",
    "mx2.deadboltemail.com",
    "eastmail.independentbeers.com",
    "eastmail.independentbeers.com",
    "eastmail.independentbeers.com",
    "eastmail.independentbeers.com",
    "eastmail.independentbeers.com",
    "eastmail.independentbeers.com",
    "eastmail.independentbeers.com",
    "eastmail.independentbeers.com",
    "eastmail.independentbeers.com",
    "eastmail.independentbeers.com",
    "spin.vinylverb.com",
    "spin.vinylverb.com",
    "spin.vinylverb.com",
    "spin.vinylverb.com",
    "spin.vinylverb.com",
    "spin.vinylverb.com",
    "spin.vinylverb.com",
    "spin.vinylverb.com",
    "spin.vinylverb.com",
    "spin.vinylverb.com",
    "server.talonphotography.com",
    "server.talonphotography.com",
    "server.talonphotography.com",
    "server.talonphotography.com",
    "server.talonphotography.com",
    "server.talonphotography.com",
    "server.talonphotography.com",
    "server.talonphotography.com",
    "server.talonphotography.com",
    "server.talonphotography.com",
    "incoming.bloggersofbeer.com",
    "incoming.bloggersofbeer.com",
    "incoming.bloggersofbeer.com",
    "incoming.bloggersofbeer.com",
    "incoming.bloggersofbeer.com",
    "incoming.bloggersofbeer.com",
    "incoming.bloggersofbeer.com",
    "incoming.bloggersofbeer.com",
    "incoming.bloggersofbeer.com",
    "incoming.bloggersofbeer.com",
    "incoming.bloggersofbeer.com",
    "incoming.bloggersofbeer.com",
    "db.deadboltinternet.com",
    "db.deadboltinternet.com",
    "db.deadboltinternet.com",
    "db.deadboltinternet.com",
    "db.deadboltinternet.com",
    "db.deadboltinternet.com",
    "db.deadboltinternet.com",
    "db.deadboltinternet.com",
    "db.deadboltinternet.com",
    "db.deadboltinternet.com",
    "tech.bloggersoftechnology.com"                         # This domain will ALWAYS bounce as it has no MX .. include it much less often
]

recipCities = ["Baltimore", "Boston", "London", "New York", "Paris", "Rio de Janeiro", "Seattle", "Sydney", "Tokyo" ]
recipGenders = ["female", "male"]

htmlLink = 'http://talonphotography.com/blank.html'

content = [
    {'campaign': 'sparkpost-traffic-gen Todays_Sales', 'subject': 'Today\'s sales', 'linkname': 'Deal of the Day'},
    {'campaign': 'sparkpost-traffic-gen Newsletter', 'subject': 'Newsletter', 'linkname': 'More Daily News'},
    {'campaign': 'sparkpost-traffic-gen Last Minute Savings', 'subject': 'Savings', 'linkname': 'Last Minute Savings'},
    {'campaign': 'sparkpost-traffic-gen Password_Reset', 'subject': 'Password reset', 'linkname': 'Password Reset'},
    {'campaign': 'sparkpost-traffic-gen Welcome_Letter', 'subject': 'Welcome letter', 'linkname': 'Contact Form'},
    {'campaign': 'sparkpost-traffic-gen Holiday_Bargains', 'subject': 'Holiday bargains', 'linkname': 'Holiday Bargains'}
]

ToAddrPrefix = 'fakespark+'                         # prefix - random digits are appended to this
ToName = 'Fake Spark'

# -----------------------------------------------------------------------------------------

def randomRecip():
    numDigits = 15                                  # Number of random local-part digits to generate
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

def randomContents():
    c = random.choice(content)
    htmlBody = 'Click <a href="http://127.0.0.1/blank.html" data-msys-linkname="' + c['linkname'] + '">' + htmlLink + '</a>'
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
sendInterval = 5                                    # minutes
while(True):
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
    if host != 'https://api.sparkpost.com':
        txObj.update( { 'metadata': { 'binding': 'outbound' } } )
    recipients = []
    # Send every n minutes, somewhere between half and full traffic rate
    batchSize = int( (0.25 + (0.75 * random.random())) * sendInterval * count)
    for i in range(0, batchSize):
        recipients.append(randomRecip())
    sendToRecips(sp, recipients, txObj)
    time.sleep(60*sendInterval)