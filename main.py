from flask import Flask, request, jsonify, Response, abort
import connect

app = Flask(__name__)

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
    if (action == 'Usuń'):
    connect.connect()
    connect.login(par, action)
    connect.close()
    return str(par) + str(action)

@app.route('/Ps04.php', methods=['GET'])
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
