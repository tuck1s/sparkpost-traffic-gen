import redis, json, platform
from flask import Flask, make_response, render_template
app = Flask(__name__)

def getResults():
    resultsFile = 'results.json'
    try:
        with open(resultsFile) as fIn:
            return json.load(fIn)
    except:
        return {'startedRunning': 'Not yet - check your Heroku Scheduler is set up'}

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

# Start the app
if __name__ == "__main__":
    app.run()

