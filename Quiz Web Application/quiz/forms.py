from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, BooleanField, SelectField
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError
from quiz.models import Users, Questions
from quiz import db

class RegistrationForm(FlaskForm):
    name = StringField('Name', validators = [DataRequired(), Length(min = 5, max = 25)])
    username = StringField('Username', validators = [DataRequired(), Length(min = 2, max = 20)])
    email = StringField('Email', validators = [DataRequired(), Email()])
    password = PasswordField('Password', validators = [DataRequired()])
    confirm_password = PasswordField('Confirm Password', validators = [DataRequired(), EqualTo('password')])
    submit = SubmitField('Sign Up')

    def validate_username(self, username):
        user = Users.query.filter_by(username = username.data).first()
        if(user):
            raise(ValidationError('That username is taken. Please choose another one'))

    def validate_email(self, email):
        user = Users.query.filter_by(email = email.data).first()
        if(user):
            raise(ValidationError('That email is taken. Please choose another one'))
    
class QuestionsForm(FlaskForm):
    category = SelectField('Category', choices = ['Random', 'Mixed'] + [i[0] for i in db.session.query(Questions.category).distinct().all()])
    number_of_questions = SelectField('Number of Questions', choices = [5, 10, 20])
    submit = SubmitField('Submit')
    
class CommentsForm(FlaskForm):
    name = StringField('Your Name', validators = [DataRequired()])
    statement = StringField('Your Comments', validators = [DataRequired()])
    submit = SubmitField('Add Comment')

class LoginForm(FlaskForm):
    username = StringField('Username', validators = [DataRequired()])
    password = PasswordField('Password', validators = [DataRequired()])
    remember = BooleanField('Remember Me')
    submit = SubmitField('Login')
    
class QuizForm(FlaskForm):
    submit = SubmitField('Submit')