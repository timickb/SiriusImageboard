import re
from hashlib import sha256

LOGIN_TEMPLATE = "[a-zA-Z0-9_]"
FBD_SYMBOLS = '<>@\''
EMAIL_TEMPLATE = "[^@]+@[^@]+\.[^@]+"

class Security:
    def checkLogin(self, login):
        if len(login) > 3 and len(login) < 14:
            if re.match(LOGIN_TEMPLATE, login) is not None:
                return True
        return False
    
    def checkPassword(self, password):
        return True
    
    def checkEmail(self, email):
        if re.match(EMAIL_TEMPLATE, email) is not None:
            return True
        print('wrong email')
        return False
    
    def checkText(self, text):
        if text == '': return False
        text = list(text)
        for symbol in list(FBD_SYMBOLS):
            if symbol in text:
                return False
        return True
    
    def sha256(self, value):
        return sha256(value.encode()).hexdigest()
