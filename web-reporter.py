import redis, json
from flask import Flask, request
app = Flask(__name__)

config = {
    'toAddr': '',
    'fromAddr': '',
    'msgPerMinLow': 0,
    'msgPerMinHigh': 0
}

'''
Statistics
Started running:
Total sent volume
Most recent sent: in x seconds
Next send at:
'''

#
# Flask entry points
#
@app.route('/', defaults={'path': ''}, methods=['GET'])
def handle_all(path):
    print(request.method, path)
    c = r.incr('mycounter')
    r.set('config', json.dumps(config) )
    qstr = r.get('config')
    q = json.loads(qstr)
    return 'All OK here, thanks: '+str(c)

# Start the app
if __name__ == "__main__":
    r = redis.Redis()
    r.set('mycounter', 0)
    app.run(debug=True)                         # Permit Pycharm IDE debugging
