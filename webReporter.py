import glob

import os, redis, json
from flask import Flask, make_response, render_template
app = Flask(__name__)

# Access to Redis data
def getResults():
    redisUrl = os.getenv('REDIS_URL', default='localhost')  # Env var is set by Heroku; will be unset when local
    r = redis.from_url(redisUrl, socket_timeout=5)          # shorten timeout so doesn't hang forever
    rkey = 'sparkpost-traffic-gen:' + os.getenv('RESULTS_KEY', default='0000')
    res = r.get(rkey)
    if res:
        return json.loads(res)
    else:
        return {'startedRunning': 'Not yet - waiting for scheduled running to begin'}

# returns True if data written back to Redis OK
def setResults(res):
    redisUrl = os.getenv('REDIS_URL', default='localhost')  # Env var is set by Heroku; will be unset when local
    r = redis.from_url(redisUrl, socket_timeout=5)          # shorten timeout so doesn't hang forever
    rkey = 'sparkpost-traffic-gen:' + os.getenv('RESULTS_KEY', default='0000')
    return r.set(rkey, res)

# read config from env vars, where present
def getConfig():
    return {
        'sparkpost_host':           os.getenv('SPARKPOST_HOST', 'https://api.sparkpost.com'),
        'messages_per_minute_low':  os.getenv('MESSAGES_PER_MINUTE_LOW'),
        'messages_per_minute_high': os.getenv('MESSAGES_PER_MINUTE_HIGH'),
        'from_email':               os.getenv('FROM_EMAIL')
    }

# Flask entry points
@app.route('/', methods=['GET'])
def status_html():
    r = getConfig()
    r.update(getResults())
    # pass in merged dict as named params to template substitutions
    return render_template('index.html', **r)

# This entry point returns JSON-format report on the traffic generator
@app.route('/json', methods=['GET'])
def status_json():
    flaskRes = make_response(json.dumps(getResults()))
    flaskRes.headers['Content-Type'] = 'application/json'
    return flaskRes

# Start the app
if __name__ == "__main__":
    app.run()

