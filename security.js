/*
    Copyright by Timur Batrutdinov
*/

var crypto = require('crypto');


let checkLogin = login => {
    if(login.length > 3 && login.length < 21) {
        if(login.match('[a-zA-Z0-9]')) {
            return true;
        }
    }
    return false;
}

let checkPassword = password => {
    if(password.length > 7 && password.length < 65) {
        if(password.match('[a-zA-Z0-9.()\#\_\*]')) {
            return true;
        }
    }
    return false;
}

let checkEmail = email => {
    return email.match(/^[0-9a-z-\.]+\@[0-9a-z-]{2,}\.[a-z]{2,}$/i);
}

let sha256 = data => {
    var sha256sum = crypto.createHash('sha256');
    sha256sum.update('gucci#' + data);
    return sha256sum.digest('hex');
}

module.exports.checkLogin = checkLogin;
module.exports.checkPassword = checkPassword;
module.exports.checkEmail = checkEmail;
module.exports.sha256 = sha256;