from quiz import db, login_manager
from datetime import datetime
from flask_login import UserMixin

@login_manager.user_loader
def load_user(user_id):
    return(Users.query.get(int(user_id)))

class Questions(db.Model):
    questionid = db.Column(db.Integer, primary_key = True)
    question = db.Column(db.String(255), nullable = False)
    category = db.Column(db.String(255), nullable = False)
    answer = db.Column(db.String(255), nullable = False)
    option1 = db.Column(db.String(255), nullable = False)
    option2 = db.Column(db.String(255), nullable = False)
    option3 = db.Column(db.String(255), nullable = False)

    def json(self):
        result = {
            'id': self.questionid,
            'question': self.question,
            'category': self.category,
            'answer': self.answer,
            'option1': self.option1,
            'option2': self.option2,
            'option3': self.option3
        }
        return(result)


class Comments(db.Model):
    commentid = db.Column(db.Integer, primary_key = True)
    statement = db.Column(db.String(255), nullable = False)
    name = db.Column(db.String(255), nullable = False)
    timestamp = db.Column(db.DateTime, nullable = False, default = datetime.utcnow)

    def json(self):
        result = {
            'name': self.name,
            'statement': self.statement,
            'timestamp': self.timestamp
        }
        return(result)

    def __repr__(self):
        return(f"'{self.name}' commented - '{self.statement}' at '{self.timestamp}'")

class Users(db.Model, UserMixin):
    userid = db.Column(db.Integer, primary_key = True)
    username = db.Column(db.String(255), unique = True, nullable = False)
    name = db.Column(db.String(255), nullable = False)
    email = db.Column(db.String(255), unique = True, nullable = False)
    password = db.Column(db.String(255), nullable = False)
    player = db.relationship('Results', backref = 'player', lazy = True)

    def get_id(self):
        return (self.userid)

    def json(self):
        result = {
            'username': self.username,
            'name': self.name,
            'email': self.email,
            'password': self.password
        }
        return(result)

class Results(db.Model):
    resultid = db.Column(db.Integer, primary_key = True)
    score = db.Column(db.Integer, nullable = False)
    timestamp = db.Column(db.DateTime, nullable = False, default = datetime.utcnow)
    userid = db.Column(db.Integer, db.ForeignKey('users.userid'))
    category = db.Column(db.String(255), nullable = False)

    def json(self):
        result = {
            'score': self.score,
            'user': self.player,
            'category': self.category,
            'timestamp': self.timestamp
        }
        return(result)