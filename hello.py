# -*- coding: utf-8 -*-

from flask import Flask,jsonify,json,abort
from flask import request,make_response
from flask_cors import CORS, cross_origin
import cx_Oracle
import json
#import connect

app = Flask(__name__)
cors = CORS(app, resources={r"/*": {"origins": "*"}}, supports_credentials=True)
database_url='piecia/piecia1@localhost:1521/xe'

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

"""Formularz I
Wyświetlanie dla niezalogowanego uzytkownika
Zwracay json dla niezalogowanego użytkownika
"""
@app.route("/Ps02.php")
@cross_origin(origin='*')
def notLogIn():
    con = cx_Oracle.connect('piecia/piecia1@localhost:1521/xe')
    cur = con.cursor()
    cur.execute('SELECT * FROM users ORDER BY users.user_id')
    result_users = cur.fetchall()
    cur.execute('SELECT * FROM messages')
    result_messages=cur.fetchall()
    lista=[]	
    for res_user in result_users:
        for res_message in result_messages:
            if(res_user[0]==res_message[1]):
                lista.append({'name':res_user[1],'text':res_message[2],'edit':False,'delete':False,'message_id':res_message[0]})   
    cur.close()
    con.close()
    return jsonify(lista)

"""Formularz II
Logowanie - zwracany json dla zalogowanego użytkownika
"""
@app.route('/Ps04.php', methods=['GET'])
@cross_origin(origin='*')
def login():
    auth = request.authorization
    if(not auth):
        abort(401)
    login,password=auth.username, auth.password
    con = cx_Oracle.connect(database_url)
    cur = con.cursor()
    logged_user=checkUser(cur,login,password)
    #Jezeli nie ma tekiego uzytkownika zwroc 401
    if (not logged_user):
        cur.close()
        con.close()
        abort(401)
    else:
        lista=dataFromBase(cur,logged_user[0])
        cur.close()
        con.close()
        return jsonify(lista)

"""Formularz 3
Różne akcje dla zalogowanego użytkownika
"""
@app.route('/Ps042.php', methods=['GET'])
@cross_origin(origin='*')
def params():
    # W pierwszej kolejnosci sprawdzenie czy uzytkownik jest w bazie 
    auth = request.authorization
    if(not auth):
        abort(401)
    login,password=auth.username, auth.password
    con = cx_Oracle.connect(database_url)
    cur = con.cursor()
    logged_user=checkUser(cur,login,password)
    if (not logged_user):
        cur.close()
        con.close()
        abort(401)
    else:
        id_logged_user=logged_user[0]
 
    #Tylko zalogowany uzytkownik, moze wykonywać akcje 
    action = request.args.get('action')
    if (action == 'Usuń'):
        id_message_to_delete=request.args.get('par')
        message_owner=checkMessageOwner(cur,id_message_to_delete,id_logged_user)
        #jesli jest wiadomosc o takim id oraz jej wlascicielem jest obecnie zalogowany uzytkownik to usun wiadomosc
        if(message_owner):
            #Usuwam wiadomosc 
            bind={'id_message':id_message_to_delete}
            sql='DELETE FROM messages WHERE message_id=:id_message'
            cur.prepare(sql)
            cur.execute(sql,bind)
            con.commit() # zatwierdzenie operacji usuniecia wiadomosci
            #usuwanie z allowed_messages
            bind={'id_message':id_message_to_delete}
            sql='DELETE FROM allowed_messages WHERE message_id=:id_message'
            cur.prepare(sql)
            cur.execute(sql,bind)
            con.commit() # zatwierdzenie operacji usuniecia wiadomosci
            lista=dataFromBase(cur,id_logged_user)
            cur.close()
            con.close()
            return jsonify(lista)
        #jesli nie ma wiadomosci o takim id lub uzytkownik nie jest wlascicielem zwroc wyjatek
        else: 
            cur.close()
            con.close()
            abort(401)

    elif(action=='Dodaj'):
        text_message=request.args.get('par')
        bind={'wiadomosc':text_message,'id_user':id_logged_user}
        sql='insert into messages values(message_id.nextval, :id_user,:wiadomosc)'
        cur.prepare(sql)
        cur.execute(sql,bind)
        con.commit()
        lista=dataFromBase(cur,id_logged_user)
        cur.close()
        con.close()
        return jsonify(lista)

    elif(action=='Edytuj'):     
        id_message=request.args.get('par')
        result_message=checkMessage(cur,id_message)
        if(not result_message):
            cur.close()
            con.close()
            #abort(make_response("Nie ma wiadomosci o takim Id w bazie"))
            abort(401)
        #Pobranie uzytkownikow ktorzy maja uprawnienia do edycji
        bind={'id_message':id_message}
        sql='SELECT user_id FROM allowed_messages WHERE message_id=:id_message'
        cur.prepare(sql)
        cur.execute(sql,bind)
        allowed_users_prepare=cur.fetchall()
        allowed_users=[]#lista uzytkownikow ktorzy maja prawo edycji
        if(allowed_users_prepare):
            for element in allowed_users_prepare:
                for item in element:
                    allowed_users.append(item)

        #sprawdzenie czy zalogowany uzytkownik ma mozliwosc edytowania
        user_can_edit=False 
        for allowed_user in allowed_users:
            if(allowed_user==id_logged_user):
                user_can_edit=True
        #sprawdzenie czy zalogowany uzytkownik jest wlascicielem
        user_is_owner=False
        if(id_logged_user==result_message[1]):
            user_is_owner=True

        #Przypadek 1 nie jest ani wlascicielem ani nie ma uprawnien
        if(not user_can_edit and not user_is_owner):
            cur.close()
            con.close()
            #abort(make_response("Nie jestes ani wlascicielem ani nie masz uprawnien"))
            abort(401)
        #Przypadek 2 nie jest wlascicielem ale ma uprawnienia
        elif(not user_is_owner and user_can_edit):
            cur.close()
            con.close()
            return jsonify({'message_id':result_message[0],'text':result_message[2]})
        #Przypadek 3 jest wlascicielem
        elif(user_is_owner):
            #Pobieranie wszystkich uzytkownikow
            sql='SELECT * FROM users'
            cur.execute(sql)
            all_users=cur.fetchall()
            #Sprawdznie nazw uzytkownikow ktorzy uzytkownicy maja prawo edycji
            list_user=[]
            for user in all_users:
                #jezeli ma prawo edycji 
                if(user[0] in allowed_users):
                    list_user.append({'user_id': user[0], 'name':user[1],'edit':True})
                #jezeli jest wlascicielem
                elif(user[0]==id_logged_user):
                    pass
                #nie ma praw edycji
                else:
                    list_user.append({'user_id': user[0], 'name':user[1],'edit':False})
            list_return={'message_id':result_message[0],'text':result_message[2],'users':list_user}
            cur.close()
            con.close()
            return jsonify(list_return)
    
    elif(action=='Zatwierdź'):
        id_message=request.args.get('par2')
        result_message=checkMessage(cur,id_message)
        if(not result_message):
            cur.close()
            con.close()
            #abort(make_response("Nie ma wiadomosci o takim Id w bazie"))
            abort(401)
        #Pobranie uzytkownikow ktorzy maja uprawnienia do edycji
        allowed_users=selectAllowedUser(cur, id_message)
        #sprawdzenie czy zalogowany uzytkownik ma mozliwosc edytowania
        user_can_edit=False 
        for allowed_user in allowed_users:
            if(allowed_user==id_logged_user):
                user_can_edit=True
        #sprawdzenie czy jest wlascicielem
        user_is_owner=False
        if(id_logged_user==result_message[1]):
            user_is_owner=True

        #Przypadek 1 nie jest ani wlascicielem ani nie ma uprawnien
        if(not user_can_edit and not user_is_owner):
            abort(401)
        #Przypadek 2 nie jest wlascicielem ale ma uprawnienia czyli moze zmienic tekst, ale nie moze nadawac uprawnien
        elif(not user_is_owner and user_can_edit):
            text_message=request.args.get('par')
            if(text_message):
                bind={'text_messages':text_message,'id_message':id_message}
                sql='UPDATE messages SET text=:text_messages WHERE message_id=:id_message'
                cur.prepare(sql)
                cur.execute(sql,bind)
                con.commit()
                lista=dataFromBase(cur,id_logged_user)
                cur.close()
                con.close()
                return jsonify(lista)
            else:
                cur.close()
                con.close()
                abort(401)
            
        #Przypadek 3 jest wlascicielem
        elif(user_is_owner):
            text_messages=request.args.get('par')
            if(text_messages):
                bind={'text_messages':text_messages,'id_message':id_message}
                sql='UPDATE messages SET text=:text_messages WHERE message_id=:id_message'
                cur.prepare(sql)
                cur.execute(sql,bind)
                con.commit()

            every_good=True
            for key, value in request.args.items():
                #dla id_wiadomosci oraz akcji nie wykonuj nic
                if(key=='par' or key=='action' or key=='par2'):
                    pass
                else:
                    every_good=checkUserId(cur,value,id_message)
                    if(not every_good):
                        break
            if(every_good):    
                bind={'id_message':id_message}
                sql='DELETE FROM allowed_messages WHERE message_id=:id_message'
                cur.prepare(sql)
                cur.execute(sql,bind)
                con.commit()
                for key, value in request.args.items():
                    #dla id_wiadomosci oraz akcji nie wykonuj nic
                    if(key=='par' or key=='action' or key=='par2'):
                        pass
                    else:
                        bind={'id_message':id_message,'id_user':value}
                        sql='insert into allowed_messages values(:id_user,:id_message)'
                        cur.prepare(sql)
                        cur.execute(sql,bind)
            """else:
                bind={'id_message':id_message}
                sql='DELETE FROM allowed_messages WHERE message_id=:id_message'
                cur.prepare(sql)
                cur.execute(sql,bind)
                con.commit()
            """ 
            con.commit()
            lista=dataFromBase(cur,id_logged_user)
            cur.close()        
            con.close()
            return jsonify(lista)

    else:
        cur.close()
        con.close()
        return (jsonify('Akcja nieznana'))


"""Sprawdzenie czy jest taki uzytkownik w bazie danych
"""
def checkUserId(cur,userId,id_message):
    bind={'id_user':userId}
    sql='SELECT * FROM users WHERE user_id=:id_user'
    cur.prepare(sql)
    cur.execute(sql,bind)
    result_user=cur.fetchone()
    is_owner=checkMessageOwner(cur,id_message,userId)
    # nie ma takiego uzytkownika
    if(not result_user):
        return False
    #jest taki uzytkownika, ale jest wlascicielem
    elif(result_user and is_owner):
        return False
    #jest uzytkownik i nie jest wlacicielem
    else:
        return True

def checkUser(cur,login,password):
    bind = {'login': login,'password_check':password}
    sql = 'select * from users where name = :login AND password=:password_check'
    cur.prepare(sql)
    cur.execute(sql, bind)
    logged_user = cur.fetchone() 
    return logged_user  
"""Sprawdzenie czy jest taka wiadomosc w bazie danych
"""  
def checkMessage(cur, id_message):
  
    bind={'id_message':id_message}
    sql='SELECT * FROM messages WHERE message_id=:id_message'
    cur.prepare(sql)
    cur.execute(sql,bind)  
    return cur.fetchone()

def selectAllowedUser(cur,id_message):
    bind={'id_message':id_message}
    sql='SELECT user_id FROM allowed_messages WHERE message_id=:id_message'
    cur.prepare(sql)
    cur.execute(sql,bind)
    allowed_users_prepare=cur.fetchall()
    allowed_users=[]#lista uzytkownikow ktorzy maja prawo edycji
    if(allowed_users_prepare):
        for element in allowed_users_prepare:
            for item in element:
                allowed_users.append(item)
    return allowed_users

def checkMessageOwner(cur,id_message_to_delete,id_logged_user):
        bind={'id_message':id_message_to_delete,'id_user':id_logged_user}
        #Sprawdzam czy jest wiadomosc o takim id oraz czy jej wlascicielem jest obecnie zalogowany uzytkownik
        sql='SELECT * FROM messages WHERE message_id=:id_message AND user_id=:id_user'
        cur.prepare(sql)
        cur.execute(sql,bind)
        result_message=cur.fetchone()
        if(result_message):
            return True
        else:
            return False

def dataFromBase(cur,id_user):
    cur.execute('SELECT * FROM users')
    result_users = cur.fetchall()
    cur.execute('SELECT * FROM messages')
    result_messages=cur.fetchall()
    bind={'id_user':id_user}
    sql='SELECT message_id FROM allowed_messages WHERE user_id=:id_user'
    cur.prepare(sql)
    cur.execute(sql,bind)
    result_allowed_messages=cur.fetchall()# [[],[],[]]
    allowed_edit=[]# [id_message1,id_message2]
    if(result_allowed_messages):
        for element in result_allowed_messages:
            for item in element:
                allowed_edit.append(item)
    lista=[]	
    for res_user in result_users:
        for res_message in result_messages:                
            if(res_user[0]==res_message[1]):
                # Przypadek pierwszy jesli jest wlascicielem wiadomosci
                if(res_message[1]==id_user):
                    lista.append({'name':res_user[1],'text':res_message[2],'edit':True,'delete':True,'message_id':res_message[0]})
                #Przypadek drugi jezeli nie jest wlascicielem ale moze edytowac
                elif((res_message[1]!=id_user) and (res_message[0] in allowed_edit)):
                    lista.append({'name':res_user[1],'text':res_message[2],'edit':True,'delete':False,'message_id':res_message[0]})
                #Przypadek trzeci nie jest ani wlascicielem ani nie ma uprawnien
                else:
                    lista.append({'name':res_user[1],'text':res_message[2],'edit':False,'delete':False,'message_id':res_message[0]})
    return lista