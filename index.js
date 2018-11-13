/*
    Copyright by Timur Batrutdinov
*/

var express = require('express');
var bodyParser = require('body-parser');
//var session = require('express-session');
//var cookieParser = require('cookie-parser');
var fs = require('fs');
var mysql = require('mysql');
var config = require('./config');
var security = require('./security');

//---------------------------------------------------

fs.mkdir('./logs', () => {});

var logger = (type, message) => {
    console.log('['+type+'] ' + message)
}

//---------------------------------------------------

var connection = mysql.createConnection({
    host     : config.mysql.host,
    user     : config.mysql.user,
    password : config.mysql.password,
    database : config.mysql.database
  });
  
connection.connect(err => {
    if (err) throw err;
    console.log('MySQL connected');
});
//---------------------------------------------------

app = express();
app.use(bodyParser.urlencoded({extended: true}));
app.use(bodyParser.json());
app.use(express.static(__dirname + '/public'));
app.set('view engine', 'ejs');

//---------------------------------------------------

app.get('/', (req, res) => {
    res.render('index');
});

app.get('/login', (req, res) => {
    res.render('login', {status: undefined});
});
app.post('/login', (req, res) => {
    let login = req.body.login;
    let password = req.body.password;
    if(security.checkLogin(login) && security.checkPassword(password)) {
        password = security.sha256(password);
        let query = "SELECT * FROM users WHERE login='"+login+"' AND password='"+password+"'";
        connection.query(query, (err, result) => {
            if(err) {
                res.render('login', {status: 'MySQL error'});
            } else {
                if(result.length > 0) {
                    res.render('index', {session: 'authorized'});
                } else {
                    res.render('login', {status: 'Wrong login or password'});
                }
        }
        });
    } else {
        res.render('login', {status: 'Disallowed characters'});
    }
    
});

app.get('/register', (req, res) => {
    res.render('register', {status: undefined});
});
app.post('/register', (req, res) => {
    let status;
    let login = req.body.login;
    let password = req.body.password;
    let repassword = req.body.repassword;
    let email = req.body.email;
    if(security.checkLogin(login) && security.checkPassword(password) && security.checkEmail(email)) {
        if(password === repassword) {
            //Проверим логин и email на уникальность
            connection.query("SELECT * FROM users", (err, result) => {
                for(var i = 0 ; i < result.length; i++) {
                    if(result[i].login == login || result[i].email == email) {
                        res.render('register', {status: 'Login or email already exist'});
                        return;
                    }
                }
            });
            password = security.sha256(password);
            query = "INSERT INTO users " + 
                "VALUES('', '"+login+"', '"+password+"', '"+email+"', "+Date.now()+")";
            connection.query(query, (err, result) => {
                if(!err) {
                    res.render('login', {status: 'You was successfully registered'});
                } else {
                    res.render('register', {status: 'MySQL error occured'});
                }
            });
        } else {
            res.render('register', {status: 'Passwords don\'t match'});
        }
    } else {
        res.render('register', {status: 'Incorrect data'});
    }
});

app.get('/topic/:id', (req, res) => {
    res.render('topic');
});

app.get('/settings', (req, res) => {
    res.render('settings');
})

//---------------------------------------------------

app.listen(config.port, () => console.log('Server started at port ' + config.port));