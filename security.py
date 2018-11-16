import re
from hashlib import sha256

class Security:
    def checkLogin(self, login):
        return True
    
    def checkPassword(self, password):
        return True
    
    def checkEmail(self, email):
        return True
    
    def checkText(self, text):
        return True
    
    def sha256(self, value):
        return sha256(value.encode()).hexdigest()
