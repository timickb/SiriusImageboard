/*
    Copyright by Timur Batrutdinov
*/

var express = require('express');
var bodyParser = require('body-parser');
var mongoose = require('mongoose');
var fs = require('fs');
var config = require('./config');
var security = require('./security');

//---------------------------------------------------

fs.mkdir('./logs', () => {});

var logger = (type, message) => {
    console.log('['+type+'] ' + message)
}

//---------------------------------------------------

var mongoDB = 'mongodb://'+config.mongodb.host+'/'+config.mongodb.database;
mongoose.connect(mongoDB);
mongoose.Promise = global.Promise;
var db = mongoose.connection;
db.on('error', console.error.bind(console, 'MongoDB connection error:'));

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
    res.render('login');
});
app.post('/login', (req, res) => {
    let login = req.body.login;
    let password = req.body.password;
});

app.get('/register', (req, res) => {
    res.render('register');
});
app.post('/register', (req, res) => {
    let status;
    let login = req.body.login;
    let password = req.body.password;
    let repassword = req.body.repassword;
    let email = req.body.email;
    if(security.checkLogin(login) && security.checkPassword(password) && security.checkEmail(email)) {
        status = 'passwords don\'t match';
        if(password === repassword) {
            status = 'correct';
        }
    } else {
        status = 'invalid data';
    }
    res.end(status);
});

app.get('/topic/:id', (req, res) => {
    res.render('topic');
});

app.get('/settings', (req, res) => {
    res.render('settings');
})

//---------------------------------------------------

app.listen(config.port, () => console.log('Server started at port ' + config.port));