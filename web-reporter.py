from flask import Flask, request, Response, make_response

app = Flask(__name__)
#
# Flask entry points
#
@app.route('/', defaults={'path': ''}, methods=['GET'])
def handle_all(path):
    print(request.method, path)
    return 'All OK here, thanks'

# Start the app
if __name__ == "__main__":
    app.run(debug=True)