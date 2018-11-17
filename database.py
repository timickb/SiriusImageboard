from security import Security
from time import time
from flaskext.mysql import MySQL
import datetime

def getStrDate(unix):
    return datetime.datetime.fromtimestamp(int(unix)).strftime('%d.%m.%y %H:%M')

def getDictFromTuple(tpl, table):
    USERS = ('id', 'login', 'password', 'email', 'regTime')
    TOPICS = ('id', 'title', 'description', 'creationTime', 'authorID', 'rating')
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
        elif table == 'messages':
            for i in range(len(element)):
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
    def getUserIDByLogin(self, login):
        self.cursor.execute("SELECT * FROM users WHERE login='"+login+"'")
        data = self.cursor.fetchone()
        return data[0]
    
    # Get user by ID
    def getUserByID(self, id):
        self.cursor.execute("SELECT * FROM users WHERE id="+str(id))
        data = self.cursor.fetchall()
        data = getDictFromTuple(data, 'users')
        return data[0]
    
    def getUserByLogin(self, login):
        self.cursor.execute("SELECT * FROM users WHERE login='"+login+"'")
        data = self.cursor.fetchall()
        data = getDictFromTuple(data, 'users')
        return data[0]

    # Post message
    def postMessage(self, text, topicID, authorID):
        if self.s.checkText(text):
            _id = self.getNextMessageID()
            sql = "INSERT INTO messages VALUES ({}, '{}', {}, {}, {}, {})".format(
                str(_id), text, int(time()), topicID, authorID, 0
            )
            self.cursor.execute(sql)
            self.conn.commit()
            return 'OK'
        else:
            return 'Error'
        
    # Create topic
    def createTopic(self, title, description, authorID):
        if self.s.checkText(title) and self.s.checkText(description):
            _id = self.getNextTopicID()
            sql = "INSERT INTO topics VALUES ({}, '{}', '{}', {}, {}, {})".format(
                str(_id), title, description, int(time()), authorID, 0
            )
            self.cursor.execute(sql)
            self.conn.commit()
            return 'OK'
        else:
            return 'Error'
    
    # Get topics
    def getTopicsList(self):
        self.cursor.execute("SELECT * FROM topics ORDER BY rating DESC")
        data = self.cursor.fetchall()
        data = getDictFromTuple(data, 'topics')
        for i in range(len(data)):
            data[i]['authorLogin'] = self.getUserLoginByID(data[i]['authorID'])
            data[i]['creationTime'] = getStrDate(data[i]['creationTime'])
            data[i]['count'] = self.getMessagesCountInTopic(data[i]['id'])
        return data
    
    # Get topic by id
    def getTopicByID(self, id):
        self.cursor.execute("SELECT * FROM topics WHERE id="+str(id))
        data = getDictFromTuple([self.cursor.fetchone()], 'topics')
        data[0]['authorLogin'] = self.getUserLoginByID(data[0]['authorID'])
        data[0]['creationTime'] = getStrDate(data[0]['creationTime'])
        data[0]['count'] = self.getMessagesCountInTopic(data[0]['id'])
        return data[0]
    
    def getMessagesCountInTopic(self, id):
        self.cursor.execute("SELECT * FROM messages WHERE topicID="+str(id))
        return len(self.cursor.fetchall())
        

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
    
    # Get messages in topic
    def getMessages(self, topicID):
        self.cursor.execute("SELECT * FROM messages WHERE topicID="+str(topicID)+" ORDER BY id DESC")
        result = self.cursor.fetchall()
        data = getDictFromTuple(result, 'messages')
        for i in range(len(data)):
            print('AABLYAA: ' + str(data[i]['authorID']))
            data[i]['authorLogin'] = self.getUserLoginByID(data[i]['authorID'])
            data[i]['creationTime'] = getStrDate(data[i]['creationTime'])
            if data[i]['image'] > 0:
                data[i]['text'] += '<br><img src="/static/img/'+str(data[i]['image'])+'.jpg"></img>'
        return data

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
                    return {'status': 'OK', 'data': data}
                else:
                    return {'status': 'Error','text': 'Login or email already exists'}
            else:
                return {'status': 'Error', 'text': 'Passwords do not match'}
        else:
            return {'status': 'Error', 'text': 'Invalid symbols in login/email/password'}