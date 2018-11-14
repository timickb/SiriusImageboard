from flask import Flask
from flask import render_template
from flask import request
from flaskext.mysql import MySQL
from security import 

#---------------------------------------------------

app = Flask(__name__)

mysql = MySQL()
 
# MySQL configurations
app.config['MYSQL_DATABASE_USER'] = 'root'
app.config['MYSQL_DATABASE_PASSWORD'] = ''
app.config['MYSQL_DATABASE_DB'] = 'board'
app.config['MYSQL_DATABASE_HOST'] = 'localhost'
mysql.init_app(app)

conn = mysql.connect()
cursor = conn.cursor()

sec = Security()

#---------------------------------------------------

@app.route('/', methods=['GET'])
def index():
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        return render_template('login.html')

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
        if sec.checkLogin(login) and sec.checkEmail(email) and sec.checkPassword(password):
            if password === rpassword:
                # Проверка логина и email на уникальность
                cursor.execute("SELECT * FROM users WHERE login={0} OR email={1}"
                    .format(login, email))
                if len(cursor.fetchall()) == 0:
                    # Записываем его в бд
                    sql = "INSERT INTO users VALUES('', '{0}', '{1}', '{3}')"
                else:
                    return render_template('register.html', status='Login or email already exists')
            else:
                return render_template('register.html', status='Passwords don\'t match')
        else:
            return render_template('register.html', status='Invalid symbols')
@app.route('/settings', methods=['GET', 'POST'])
def settings():
    if request.method == 'GET':
        return render_template('settings.html')

@app.route('/topic/<topicID>', methods=['GET', 'POST'])
def topic(topicID):
    if request.method == 'GET':
        return render_template('topic.html')

app.run(host='0.0.0.0', port=8080, debug=True)