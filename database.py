from security import Security
from time import time
from flaskext.mysql import MySQL
import datetime

def getStrDate(unix):
    return datetime.datetime.fromtimestamp(int(unix)).strftime('%d.%m.%y %H:%M')

def getDictFromTuple(tpl, table):
    USERS = ('id', 'login', 'password', 'email', 'regTime')
    TOPICS = ('id', 'title', 'creationTime', 'authorID', 'rating')
    MESSAGES = ('id', 'text', 'creationTime', 'topicID', 'authorID', 'image')
    gresult = []
    for element in tpl:
        result = {}
        if table == 'users':
            for i in range(len(element)):
                result[USERS[i]] = element[i]
        elif table == 'topics':
            for i in range(len(element)):
                result[TOPICS[i]] = element[i]
        else:
            for i in range(len(tpl)):
                result[MESSAGES[i]] = element[i]
        gresult.append(result)
    return gresult

class Database():
    def __init__(self, conn, cursor):
        self.conn = conn
        self.cursor = cursor
        self.s = Security()

    # Sign in operation
    def loginUser(self, login, password):
        if (self.s.checkLogin(login) and (self.s.checkPassword(password))):
            password = self.s.sha256(password)
            self.cursor.execute("SELECT * FROM users WHERE login='"+login+"' AND password='"+password+"'")
            data = self.cursor.fetchall()
            if len(data) == 1:
                return {'status': 'OK', 'data': data[0]}
            else:
                return {'status': 'Error'}

    # Get user login by ID
    def getUserLoginByID(self, id):
        self.cursor.execute("SELECT * FROM users WHERE id="+str(id))
        data = self.cursor.fetchone()
        return data[1]

    # Post message
    def postMessage(self, text, topicID, authorID):
        if self.s.checkText(text):
            _id = self.getNextMessageID()
            sql = "INSERT INTO messages VALUES ({}, '{}', {}, {}, {}, {})".format(
                str(_id), text, int(time()), topicID, authorID, 0
            )
            self.cursor.execute(sql)
            self.conn.commit()

    
    # Get topics
    def getTopicsList(self):
        self.cursor.execute("SELECT * FROM topics")
        data = self.cursor.fetchall()
        data = getDictFromTuple(data, 'topics')
        for i in range(len(data)):
            data[i]['authorLogin'] = self.getUserLoginByID(data[i]['authorID'])
            data[i]['creationTime'] = getStrDate(data[i]['creationTime'])
        return data
    
    # Get topic by id
    def getTopicByID(self, id):
        self.cursor.execute("SELECT * FROM topics WHERE id="+str(id))
        data = getDictFromTuple([self.cursor.fetchone()], 'topics')
        data[0]['authorLogin'] = self.getUserLoginByID(data[0]['authorID'])
        data[0]['creationTime'] = getStrDate(data[0]['creationTime'])
        return data[0]
        

    # Get next id's
    def getNextUserID(self):
        self.cursor.execute("SELECT * FROM users ORDER BY id DESC LIMIT 1")
        result = self.cursor.fetchone()
        return result[0]+1
    def getNextTopicID(self):
        self.cursor.execute("SELECT * FROM topics ORDER BY id DESC LIMIT 1")
        result = self.cursor.fetchone()
        return result[0]+1
    def getNextMessageID(self):
        self.cursor.execute("SELECT * FROM messages ORDER BY id DESC LIMIT 1")
        result = self.cursor.fetchone()
        return result[0]+1

    # Register operation
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