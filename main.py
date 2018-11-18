from flask import Flask, request, render_template, session, redirect
from flaskext.mysql import MySQL
from database import Database
from werkzeug.utils import secure_filename
import yaml
import os

#---------------------------------------------------

config = None
with open('config.yml', 'r') as file:
    try:
        config = yaml.load(file)
    except yaml.YAMLError as ex:
        print(ex)
        exit()

#---------------------------------------------------

app = Flask(__name__)

mysql = MySQL()
 
# MySQL configurations
app.config['UPLOAD_FOLDER'] = config['uploadPath']
app.config['MYSQL_DATABASE_USER'] = config['dbUser']
app.config['MYSQL_DATABASE_PASSWORD'] = config['dbPassword']
app.config['MYSQL_DATABASE_DB'] = config['dbName']
app.config['MYSQL_DATABASE_HOST'] = config['dbHost']
mysql.init_app(app)

conn = mysql.connect()
cursor = conn.cursor()
database = Database(conn, cursor)

ALLOWED_EXTENSIONS = ['jpg', 'png', 'bmp', 'gif']

def handle_file(file_):
    print(file_)
    return True

#---------------------------------------------------

@app.route('/', methods=['GET'])
def index():
    try:
        topics = database.getTopicsList()
        result = {
            'logged': False,
            'status': -1,
            'data': topics,
            'userdata': -1
        }
        if 'login' in session:
            result['logged'] = True
            result['userdata'] = database.getUserByLogin(session['login'])
    except:
        result['status'] == 'An error occured'
    return render_template('index.html', result=result)

@app.route('/login', methods=['GET', 'POST'])
def login():
    try:
        result = {
            'logged': False,
            'status': -1,
            'data': -1,
            'userdata': -1
        }
        if request.method == 'GET':
            if 'login' in session:
                result['logged'] = True
                result['userdata'] = database.getUserByLogin(session['login'])
        elif request.method == 'POST':
            if 'login' not in session:
                rresult = database.loginUser(request.form.get('login'), request.form.get('password'))
                if rresult['status'] == 'OK':
                    session['login'] = request.form.get('login')
                    return redirect('')
                elif rresult['status'] == 'Error':
                    result['status'] = 'Wrong login or password'
            else:
                result['logged'] = True
                result['userdata'] = database.getUserByLogin(session['login'])
                result['status'] = 'You are already logged in'
    except:
        result['status'] = 'An error occured'
    return render_template('login.html', result=result)


@app.route('/register', methods=['GET', 'POST'])
def register():
    try:
        result = {
            'logged': False,
            'status': -1,
            'data': -1,
            'userdata': -1
        }
        if 'login' not in session:
            if request.method == 'GET':
                return render_template('register.html', result=result)
            elif request.method == 'POST':
                # register user
                login = request.form.get('login')
                password = request.form.get('password')
                rpassword = request.form.get('rpassword')
                email = request.form.get('email')

                rresult = database.regUser(login, password, rpassword, email)
                if rresult['status'] == 'OK':
                    session['login'] = login
                    return redirect('')
                elif rresult['status'] == 'Error':
                    result['status'] = rresult['text']
                    return render_template('register.html', result=result)
        else:
            return redirect('')
    except:
        result['status'] = 'An error occured'
        return render_template('register.html', result=result)
        
@app.route('/settings', methods=['GET', 'POST'])
def settings():
    try:
        result = {
            'logged': False,
            'status': -1,
            'data': -1,
            'userdata': -1
        }
        if 'login' in session:
            result['logged'] = True
            result['userdata'] = database.getUserByLogin(session['login'])
            if request.method == 'GET':
                return render_template('settings.html', result=result)
            elif request.method == 'POST':
                uid = database.getUserIDByLogin(session['login'])
                if request.form.get('change-email') != None:
                    print('AA  IISSJI JJKDSJKDSKJDSJKDSKJDSJK!!!')
                    oldEmail = request.form.get('change-email-old')
                    newEmail = request.form.get('change-email-new')
                    r = database.changeEmail(uid, oldEmail, newEmail)
                    if r == 'OK':
                        result['status'] == 'Success'
                    else:
                        result['status'] == 'Incorrect email'
                    return render_template('settings.html', result=result)
                elif request.form.get('change-password') != None:
                    oldPassword = request.form.get('change-password-old')
                    newPassword = request.form.get('change-password-new')
                    rnewPassword = request.form.get('change-password-rnew')
                    r = database.changePassword(uid, oldPassword, newPassword, rnewPassword)
                    if r == 'OK':
                        result['status'] == 'Success'
                    else:
                        result['status'] == 'Incorrect password or passwords do not match'
                else:
                    return render_template('settings.html', result=result)
        else:
            return redirect('login')
    except:
        result['status'] = 'An error occured'
        return render_template('settings.html', result=result)

@app.route('/topic/<topicID>/', methods=['GET', 'POST'])
def topic(topicID):
    try:
        result = {
            'logged': False,
            'status': -1,
            'data': -1,
            'userdata': -1
        }
        messages = database.getMessages(topicID)
        info = database.getTopicByID(topicID)
        result['data'] = {'info': info, 'messages': messages}
        if request.method == 'GET':
            if 'login' in session:
                result['logged'] = True
                result['userdata'] = database.getUserByLogin(session['login'])
                database.checkTopicStatus(topicID)
            return render_template('topic.html', result=result)
        elif request.method == 'POST':
            if 'login' in session:
                result['logged'] = True
                result['userdata'] = database.getUserByLogin(session['login'])

                text = request.form.get('text')

                file_ = None
                try:
                    file_ = request.files['file']
                except:
                    count = 0
                if file_: count = 1

                r = database.postMessage(text, topicID, database.getUserIDByLogin(session['login']), count)
                if r == 'Error':
                    result['status'] = 'Invalid data'
                    return render_template('topic.html', result=result)
                elif r == 'OK':
                    if file_ and handle_file(file_):
                        filename = str(database.getNextMessageID()-1)+'.jpg'
                        file_.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                return redirect('topic/'+topicID+'/')
            else:
                return redirect('login')
    except:
        result['status'] = 'An error occured'
        return render_template('topic.html', result=result)

@app.route('/logout', methods=['GET'])
def logout():
    if 'login' in session:
        del session['login']
    return redirect('')

@app.route('/create', methods=['GET', 'POST'])
def create():
    result = {
        'logged': False,
        'status': -1,
        'data': -1,
        'userdata': -1
    }
    if 'login' in session:
        result['logged'] = True
        result['userdata'] = database.getUserByLogin(session['login'])
        if request.method == 'GET':
            return render_template('create.html', result=result)
        elif request.method == 'POST':
            title = request.form.get('title')
            description = request.form.get('description')
            authorID = database.getUserIDByLogin(session['login'])
            r = database.createTopic(title, description, authorID)
            if r == 'Error':
                result['status'] = 'Invalid data'
                return render_template('create.html', result=result)
            else:
                return redirect('')
    else:
        return redirect('')

@app.errorhandler(404)
def not_found(e):
    return render_template('404.html')

@app.route('/like', methods=['GET'])
def like():
    topicID = request.args.get('id')
    database.likeTopic(topicID)
    return redirect('topic/'+str(topicID)+'/')

@app.route('/dislike', methods=['GET'])
def dislike():
    topicID = request.args.get('id')
    database.dislikeTopic(topicID)
    return redirect('topic/'+str(topicID)+'/')

app.secret_key = config['key']
app.run(host='0.0.0.0', port=config['port'], debug=True)