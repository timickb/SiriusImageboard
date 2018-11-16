from security import Security
from time import time
from flaskext.mysql import MySQL

class Database():
    def __init__(self, conn, cursor):
        self.conn = conn
        self.cursor = cursor
        self.s = Security()
    
    def loginUser(self, login, password):
        if (self.s.checkLogin(login) and (self.s.checkPassword(password))):
            self.cursor.execute("SELECT * FROM users WHERE login='"+login+"' AND password='"+password+"'")
            data = self.cursor.fetchall()
            if len(len(data) == 1):
                return {'status': 'OK', 'data': data[0]}
            else:
                return {'status': 'Error'}
    
    def getUserLoginByID(self, id):
        self.cursor.execute("SELECT * FROM users WHERE id="+str(id))
        data = self.cursor.fetchone()
        return data[1]
    
    def getTopicsList(self):
        self.cursor.execute("SELECT * FROM topics")
        data = self.cursor.fetchall()
        for i in range(len(data)):
            data[i]['authorLogin'] = self.getUserLoginByID(data[i]['authorID'])
        return data

    def getNextUserID(self):
        self.cursor.execute("SELECT * FROM users ORDER BY id DESC LIMIT 1")
        result = self.cursor.fetchone()
        return result[0]+1

    def regUser(self, login, password, rpassword, email):
        if (self.s.checkLogin(login)) and (self.s.checkEmail(email)) and (self.s.checkPassword(password)):
            if password == rpassword:
                # Проверка логина и email на уникальность
                self.cursor.execute("SELECT * FROM users WHERE login='{}' OR email='{}'"
                    .format(login, email))
                if len(self.cursor.fetchall()) == 0:
                    # Записываем его в бд
                    password = self.s.sha256(password)
                    sql = "INSERT INTO users VALUES ('"+str(self.getNextUserID())+"', '"+login+"', '"+password+"', '"+email+"', '"+str(int(time()))+"')"
                    self.cursor.execute(sql)
                    self.conn.commit()
                    data = self.cursor.fetchone()
                    print(data)
                    return {'status': 'OK', 'data': data}
                else:
                    return {'status': 'Error','text': 'Login or email already exists'}
            else:
                return {'status': 'Error', 'text': 'Passwords do not match'}
        else:
            return {'status': 'Error', 'text': 'Invalid symbols in login/email/password'}