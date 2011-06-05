class LocalConfig(object):
    SQLALCHEMY_DATABASE_URI = 'sqlite:///db/election.db'    
    DEBUG = False
    TESTING = False
    LDAP = True
    SECRET_KEY = '?\xbf,\xb4\x8d\xa3"<\x9c\xb0@\x0f5\xab,w\xee\x8d$0\x13\x8b83' 
    HOST= 'localhost'
    PORT= 8000
    
class DevelopmentConfig(LocalConfig):
    DEBUG = True
    ADMINS = ['admin']

class TestingConfig(DevelopmentConfig):
    TESTING = True        

  

    



