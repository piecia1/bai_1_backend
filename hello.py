from flask import Flask,jsonify,json,abort
from flask import request,make_response
from flask_cors import CORS, cross_origin
import cx_Oracle
import json
app = Flask(__name__)
cors = CORS(app, resources={r"/*": {"origins": "*"}}, supports_credentials=True)

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
#Logowanie
@app.route('/Ps04.php', methods=['GET'])
@cross_origin(origin='*')
def login():
    con = cx_Oracle.connect('piecia/piecia1@localhost:1521/xe')
    cur = con.cursor()
    auth = request.authorization
    login,password=auth.username, auth.password
    bind = {'login': login}
    sql = 'select * from users where name = :login'
    cur.prepare(sql)
    cur.execute(sql, bind)
    res = cur.fetchone()
    cur.close()
    con.close()
    if (not res):
        abort(401)
    if (res[2]==password):
        return 'OK'
    else:
        abort(401)

#Wyswietlanie dla niezalogowanego uzytkownika
@app.route("/Ps02.php")
@cross_origin(origin='*')
def hello():
    con = cx_Oracle.connect('piecia/piecia1@localhost:1521/xe')
    cur = con.cursor()
    cur1=con.cursor()
    cur.execute('SELECT * FROM users ORDER BY users.user_id')
    cur1.execute('SELECT * FROM messages')
    res = cur.fetchall()
    res1=cur1.fetchall()
    lista=[]	
    for result in res:
        for result1 in res1:
            if(result[0]==result1[1]):
                lista.append({'name':result[1],'text':result1[2],'edit':False,'delete':False,'message_id':result1[0]})
    
    cur.close()
    con.close()
    return jsonify(lista)


#wyswietlanie dla zalogowanego uzytkownika
@app.route('/Ps041.php', methods=['GET'])
@cross_origin(origin='*')
def edit_massage():
    auth = request.authorization
    login,password=auth.username, auth.password
    con = cx_Oracle.connect('piecia/piecia1@localhost:1521/xe')
    cur_user = con.cursor()
    cur_message=con.cursor()
    cur_user.execute('SELECT * FROM users ORDER BY users.user_id')
    cur_message.execute('SELECT * FROM messages')
    res_user = cur_user.fetchall()
    res_message=cur_message.fetchall()
    lista=[]	
    for result_user in res_user:
        if(login==result_user[1]):
            user_id=result_user[0]
            break
        else:
            user_id=None
    for result_user in res_user:
        for result_message in res_message:
            if(result_user[0]==result_message[1]):
                if(result_message[1]==user_id):
                    lista.append({'name':result_user[1],'text':result_message[2],'edit':True,'delete':True,'message_id':result_message[0]})
                else:
                    lista.append({'name':result_user[1],'text':result_message[2],'edit':False,'delete':False,'message_id':result_message[0]})
    cur_user.close()
    cur_message.close()
    con.close()
    return jsonify(lista)

#dla zalogowanego uzytkownika, rozne akcje
@app.route('/Ps042.php', methods=['GET'])
@cross_origin(origin='*')
def params():
    auth = request.authorization
    login,password=auth.username, auth.password
    con = cx_Oracle.connect('piecia/piecia1@localhost:1521/xe')
    cur_user = con.cursor()
    cur_message=con.cursor()
    bind={'login':login}
    cur_user.execute('SELECT FROM users WHERE name name=:login')
    cur_message.execute('SELECT * FROM messages')
    res_user = cur_user.fetchall()

    par = request.args.get('par')
    action = request.args.get('action')
    if (action == 'Usuń'):
        query="DELETE FROM messages WHERE message_id=%s"%par
        cur_message.execute(query)
        cur_message.close()
        con.commit()
        con.close()
    elif(action=='Dodaj'):
        pass
    return jsonify(query)



    #cur.execute('SELECT messages.text FROM messages INNER JOIN users ON users.user_id=2 ')
    #head=request.headers.get('User-Agent')
    #print(head)
    #nazwa=[{'name':'admin','text':'aaaaa','edit':True,'delete':True}]
    #zmienna=jsonify(nazwa)
    #print(res)
    #r=make_response(jsonify(nazwa))
    #r.headers.set('aaa', "default-src 'self'")


@app.route("/")
def index():
	return "Index page"

@app.route('/user/<username>')
def show_user_profile(username):
    # show the user profile for that user
    return 'User %s' % username

@app.route('/post/<int:post_id>')
def show_post(post_id):
    # show the post with the given id, the id is an integer
    return 'Post %d' % post_id

@app.route('/path/<path:subpath>')
def show_subpath(subpath):
    # show the subpath after /path/
    return 'Subpath %s' % subpath