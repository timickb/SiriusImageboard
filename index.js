var express = require('express');
var bodyParser = require('body-parser');
var config = require('./config');
var security = require('./security');
var mysql = require('mysql');


console.log('Starting MySQL connection...');
var conn = mysql.createConnection({
    host: config.mysql.host,
    user: config.mysql.user,
    password: config.mysql.password
});
/*conn.connect(err => {
    if (err) throw err;
    console.log('MySQL connected');
})*/

app = express();

app.use(bodyParser.urlencoded({extended: true}));
app.use(bodyParser.json());
app.use(express.static(__dirname + '/public'));
app.set('view engine', 'ejs');

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

app.listen(config.port, () => console.log('Server started at port ' + config.port));