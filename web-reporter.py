import glob

import redis, json, platform
from flask import Flask, make_response, render_template
app = Flask(__name__)
resultsFile = 'results.json'

def getResults():
    try:
        with open(resultsFile) as fIn:
            return json.load(fIn)
    except:
        return {'startedRunning': 'Not yet - waiting for scheduled running to begin'}

# Flask entry points
@app.route('/', methods=['GET'])
def status_html():
    r = getResults()
    return render_template('index.html', **r, name='fred')

# This entry point returns JSON-format report on the traffic generator
@app.route('/json', methods=['GET'])
def status_json():
    flaskRes = make_response(json.dumps(getResults()))
    flaskRes.headers['Content-Type'] = 'application/json'
    return flaskRes

import os, subprocess
@app.route('/test', methods=['GET'])
def status_test():
    f = os.getcwd()
    l = subprocess.run(['ls', '-l'], stdout=subprocess.PIPE).stdout.decode('utf-8')
    l = l.replace('\n', '<br>\n')
    try:
        with open(resultsFile) as fIn:
            t = fIn.read()
    except Exception as e:
        t = str(e)

    return '<pre>' + f + '<br><br>' + l + '<br><br>' + t + '</pre>'

# Start the app
if __name__ == "__main__":
    app.run()

