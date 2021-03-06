from extensions.FlaskSQLAlchemy import db

from werkzeug import generate_password_hash, check_password_hash

from sqlalchemy import ForeignKey

class User(db.Model):
    __tablename__ = 'user'
    id =                db.Column(db.Integer, primary_key=True)    
    name =              db.Column(db.String(50))
    username =          db.Column(db.String(50), unique=True)
    password =          db.Column(db.String(80))
    mail =              db.Column(db.String(50), unique=True)  
    photo =             db.Column(db.String(100))
    confirm_status =    db.Column(db.String(255))

    def __init__(self, username, password, email, confirm_status=None,name=None):
        self.username = username
        self.set_password(password)
        self.mail = email

        if name:
            self.name = name
        
        if confirm_status:
            self.confirm_status = confirm_status

    def set_password(self, password):
        self.password = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password, password)

    def __repr__(self):
        return "<User ('%s','%s','%s','%s')>" % (self.name,self.username,self.mail,self.confirm_status)

class Election(db.Model):
    __tablename__ = 'election'
    id =        db.Column(db.Integer, primary_key=True)
    title =     db.Column(db.String(100))
    text =      db.Column(db.Text)
    date_from = db.Column(db.DateTime)
    date_to =   db.Column(db.DateTime)
    show  =     db.Column(db.Boolean)
    photo =     db.Column(db.String(64))

    def __init__(self, title, text, start = None, end = None, show = False):
        self.title      = title
        self.text       = text
        self.show       = show   
        if start:
            self.date_from = start
        if end:
            self.date_to = end

class Question(db.Model):
    __tablename__ = 'question'
    id =        db.Column(db.Integer, primary_key=True)
    vid =       db.Column(db.Integer, ForeignKey('election.id'))
    text =      db.Column(db.String(100))
    count =     db.Column(db.Integer)                                   # maximal count of selected answers
    moreAnsw =  db.Column(db.Boolean)                                   # if in question can be selected more than 1 answer
    candidate = db.Column(db.Boolean)                                   # if the question is with candidates
  
    def __init__(self, text, vid, count, more = False, candidate = False):
        self.text = text
        self.vid = vid
        self.count = count
        self.moreAnsw = more
        self.candidate = candidate

    def __repr__(self):
        return '<Question %r>' % self.text

class Answer(db.Model):
    __tablename__ = 'answer'
    id =        db.Column(db.Integer, primary_key=True)
    text =      db.Column(db.String(100))
    oid =       db.Column(db.Integer, ForeignKey('question.id'))
   
    def __init__(self, nazov, oid):
        self.text = nazov
        self.oid = oid

    def __repr__(self):
        return '<Answer %r>' % self.text

class Voting(db.Model):
    __tablename__ = 'voting'
    id =        db.Column(db.Integer, primary_key=True)
    uid =       db.Column(db.Integer, ForeignKey('user.id'))
    mid =       db.Column(db.Integer, ForeignKey('answer.id'))                  # answer ID
    vid =       db.Column(db.Integer, ForeignKey('election.id'))                # election ID

    def __init__(self, uid, mid,vid):
        self.uid = uid
        self.mid = mid
        self.vid = vid
