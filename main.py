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

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS

#---------------------------------------------------

@app.route('/', methods=['GET'])
def index():
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
    return render_template('index.html', result=result)

@app.route('/login', methods=['GET', 'POST'])
def login():
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
        return render_template('login.html', result=result)
    elif request.method == 'POST':
        if 'login' not in session:
            rresult = database.loginUser(request.form.get('login'), request.form.get('password'))
            if rresult['status'] == 'OK':
                session['login'] = request.form.get('login')
                return redirect('')
            elif rresult['status'] == 'Error':
                result['status'] = 'Wrong login or password'
                return render_template('login.html', result=result)
        else:
            result['logged'] = True
            result['userdata'] = database.getUserByLogin(session['login'])
            result['status'] = 'You are already logged in'
            return render_template('login.html', result=result)

@app.route('/register', methods=['GET', 'POST'])
def register():
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
        
@app.route('/settings', methods=['GET', 'POST'])
def settings():
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
            return render_template('settings.html', result=result)
    else:
        return redirect('login')

@app.route('/topic/<topicID>/', methods=['GET', 'POST'])
def topic(topicID):
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
            elif r == 'OK':
                if file_ and allowed_file(file_.filename):
                    filename = str(database.getNextMessageID())+'.jpg'
                    file_.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            return redirect('topic/'+topicID+'/')
        else:
            return redirect('login')

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

app.secret_key = config['key']
app.run(host='0.0.0.0', port=config['port'], debug=True)