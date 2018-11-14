import re
from hashlib import sha256

class Security:
    def checkLogin(self, login):
        if len(login) > 3 and len(login) < 21:
            count = re.findall('[a-zA-Z0-9]', login)
            if len(count) == len(login):
                return True
        return False
    
    def checkPassword(self, password):
        if len(password) > 7 and len(password) < 65:
            count = re.findall('[a-zA-Z0-9.()\#\_\*]', password)
            if len(count) == len(password):
                return True
        return False
    
    def checkEmail(self, email):
        count = re.findall('/^[0-9a-z-\.]+\@[0-9a-z-]{2,}\.[a-z]{2,}$/i', email)
        if len(count) == len(email):
            return True
        return False
    
    def sha256(self, value):
        return hashlib.sha256(value.encode()).hexdigest()
