import cx_Oracle
con = None

def connect():
    global con
    con = cx_Oracle.connect('system/qwerty12345@127.0.0.1:1521/xe')
    print(con.version)

def close():
    global con
    con.close()

def login(login, password):
    global con
    cur = con.cursor()
    print(login)
    print(password)
    bind = {'login': login}
    sql = 'select * from users where name = :login'
    cur.prepare(sql)
    cur.execute(sql, bind)
    res = cur.fetchone()
    print(res[2])
    if (res[2] == password):
        return True
    else:
        return False
    cur.close()

def delete():
    global con
    cur = con.cursor()