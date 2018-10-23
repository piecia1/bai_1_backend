from flask import Flask, request, jsonify, Response, abort
from flask_cors import CORS, cross_origin
import connect

app = Flask(__name__)
cors = CORS(app, resources={r"/*": {"origins": "*"}}, supports_credentials=True)
# resources={r"/*": {"origins": "*"}},
# logging.getLogger('flask_cors').level = logging.DEBUG
# app.config['CORS_HEADERS'] = 'Content-Type'

@app.before_request
def option_autoreply():
    """ Always reply 200 on OPTIONS request """

    if request.method == 'OPTIONS':
        resp = app.make_default_options_response()

        headers = None
        if 'ACCESS_CONTROL_REQUEST_HEADERS' in request.headers:
            headers = request.headers['ACCESS_CONTROL_REQUEST_HEADERS']

        h = resp.headers

        # Allow the origin which made the XHR
        h['Access-Control-Allow-Origin'] = request.headers['Origin']
        # Allow the actual method
        h['Access-Control-Allow-Methods'] = request.headers['Access-Control-Request-Method']
        # Allow for 10 seconds
        h['Access-Control-Max-Age'] = "10"

        h['Access-Control-Allow-Credentials'] = "true"

        # We also keep current headers
        if headers is not None:
            h['Access-Control-Allow-Headers'] = headers

        return resp


@app.after_request
def set_allow_origin(resp):
    """ Set origin for GET, POST, PUT, DELETE requests """

    h = resp.headers

    # Allow crossdomain for other HTTP Verbs
    if request.method != 'OPTIONS' and 'Origin' in request.headers:
        h['Access-Control-Allow-Origin'] = request.headers['Origin']


    return resp

@app.route('/')
def hello():
    return 'Hello, World!'

@app.route('/Ps02.php', methods=['GET'])
def params():
    auth = request.authorization
    par = request.args.get('par')
    print(par)
    action = request.args.get('action')
    print(action)
    # if (action == 'Usuń'):
    connect.connect()
    connect.login(par, action)
    connect.close()
    return str(par) + str(action)

@app.route('/Ps04.php', methods=['GET'])
@cross_origin(origin='*')
def login():
    auth = request.authorization
    print(auth.username)
    print(auth.password)
    connect.connect()
    check_user = connect.login(auth.username, auth.password)
    connect.close()
    if (check_user):
        return 'OK'
    else:
        abort(401)
    # return str(auth.username) + str(auth.password)

if __name__ == "__main__":
    app.run()
