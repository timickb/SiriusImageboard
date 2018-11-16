from flask import Flask, request, render_template, session, Session
from flaskext.mysql import MySQL
from database import Database

#---------------------------------------------------

app = Flask(__name__)

mysql = MySQL()
 
# MySQL configurations
app.config['MYSQL_DATABASE_USER'] = 'root'
app.config['MYSQL_DATABASE_PASSWORD'] = '12345'
app.config['MYSQL_DATABASE_DB'] = 'forum'
app.config['MYSQL_DATABASE_HOST'] = 'localhost'
mysql.init_app(app)

conn = mysql.connect()
cursor = conn.cursor()
database = Database(conn, cursor)

#---------------------------------------------------

@app.route('/', methods=['GET'])
def index():
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        return render_template('login.html')
    elif request.method == 'POST':
        result = database.loginUser(request.form.get('login'), request.form.get('password'))
        if result['status'] == 'OK':
            user = result['data']

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'GET':
        return render_template('register.html')
    elif request.method == 'POST':
        # register user
        login = request.form.get('login')
        password = request.form.get('password')
        rpassword = request.form.get('rpassword')
        email = request.form.get('email')

        result = database.regUser(login, password, rpassword, email)
        if result['status'] == 'OK':
            return render_template('index.html', data=result['data'])
        elif result['status'] == 'Error':
            return render_template('register.html', status=result['text'])
        
@app.route('/settings', methods=['GET', 'POST'])
def settings():
    if request.method == 'GET':
        return render_template('settings.html')

@app.route('/topic/<topicID>', methods=['GET', 'POST'])
def topic(topicID):
    if request.method == 'GET':
        return render_template('topic.html')

app.run(host='0.0.0.0', port=8080, debug=True)