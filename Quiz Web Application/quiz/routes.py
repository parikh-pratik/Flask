from flask import render_template, url_for, flash, redirect, request, jsonify
from quiz.forms import LoginForm, RegistrationForm, CommentsForm, QuizForm, QuestionsForm
from flask import Markup
from quiz.models import Questions, Comments, Users, Results
from quiz import app, db, bcrypt
from flask_login import login_user, current_user, logout_user, login_required
from random import shuffle, choice
import datetime
import re

@app.route("/")
@app.route("/home")
def home():
    return(render_template("home.html", title = "Home"))

@app.route("/leaderboard")
def leaderboard():
    scores = []
    all_results = Results.query.all()
    for result in all_results:
        if(result.score < 0):
            continue
        new_result = {'Player': result.json()['user'].name or 'Unknown',
        'Category': result.json()['category'],
        'Score': result.json()['score'],
        'Timestamp': result.json()['timestamp'].strftime("%d %b, %Y %I:%M %p"),
        'ID': result.resultid
        }
        scores.append(new_result)
    return(render_template("leaderboard.html", title = "Leaderboard", leaderboard = scores))

@app.route("/playquiz", methods = ["GET", "POST"])
@login_required
def playquiz():
    preform = QuestionsForm()
    print(preform)
    print(preform.category)
    return(render_template("playquiz.html", title = "Play-Quiz", preform = preform))

@app.route("/play", methods = ["GET"])
@login_required
def quiz():
    form = QuizForm()
    category = request.args.get('category')
    if(category == 'Mixed'):
        all_questions = [i.json() for i in Questions.query.all()]
    elif(category == 'Random'):
        category = choice([i[0] for i in db.session.query(Questions.category).distinct().all()])
        all_questions = [i.json() for i in Questions.query.filter_by(category = category).all()]
    else:
        all_questions = [i.json() for i in Questions.query.filter_by(category = category).all()]
    x = max(int(request.args.get('number_of_questions')),5)
    l = len(all_questions)
    number_of_questions = x if x < l else l
    shuffle(all_questions)
    all_questions = all_questions[:number_of_questions]
    db.session.commit()
    res = Results(score = -number_of_questions, player = current_user, category = category, timestamp = datetime.datetime.now())
    db.session.add(res)
    db.session.commit()
    return(render_template("playquiz.html", title = "Play-Quiz", form = form, quiz = all_questions))      

@app.route("/results", methods = ["POST"]) 
@login_required
def return_results():
    category = request.args.get('category')
    number_of_questions = request.args.get("number_of_questions")
    result = request.form
    score = 0
    wrong = 0
    qlist = {}
    for qid, answered in result.items():
        b = Questions.query.filter_by(questionid = Markup.unescape(qid)).all()
        for a in b:
            if(a):
                qlist[a.questionid] = a.answer
                if(a.answer == Markup.unescape(answered)):
                    score += 1
                else:
                    wrong += 1
    res = Results.query.filter(Results.score < 0).first()
    number_of_questions = res.score * -1
    res.score = -1 * (score * 100)/(res.score)
    [db.session.delete(i) for i in Results.query.filter_by(userid = current_user.userid).filter(Results.score < 0)]
    db.session.commit()
    resp = {
        'score': res.score,
        'qna': qlist,
        'correct_questions': score,
        'wrong_questions': wrong
    }
    db.session.commit()
    return(jsonify(resp))

@app.route("/getquestions", methods = ["POST"])
@login_required
def getquestions():
    category = request.form['category']
    if(category == 'Mixed'):
        all_questions = [i.json() for i in Questions.query.all()]
    elif(category == 'Random'):
        category = choice([i[0] for i in db.session.query(Questions.category).distinct().all()])
        all_questions = [i.json() for i in Questions.query.filter_by(category = category).all()]
    else:
        all_questions = [i.json() for i in Questions.query.filter_by(category = category).all()]
    x = int(request.form['number_of_questions'])
    l = len(all_questions)
    number_of_questions = x if x < l else l
    shuffle(all_questions)
    return(jsonify(all_questions))

@app.route("/comments", methods = ["GET", "POST"])
def comments():
    form = CommentsForm()
    comments_list = [i.json() for i in Comments.query.all()]
    return(render_template("comments.html", title = "Comments", form = form, comments = comments_list))

@app.route("/comment", methods = ["POST"])
def comment():
    new_comment = Comments(name = request.form['name'], statement = request.form['statement'])
    db.session.add(new_comment)
    db.session.commit()
    return(jsonify(new_comment.json()))


@app.route("/register", methods = ["GET", "POST"])
def register():
    if(current_user.is_authenticated):
        return(redirect(url_for('account')))
    form = RegistrationForm()
    if(form.validate_on_submit()):
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        new_user = Users(name = form.name.data, username = form.username.data, email = form.email.data,  password = hashed_password)
        db.session.add(new_user)
        db.session.commit()
        return(render_template("login.html", title = "Login", form = LoginForm(), unsuccessful = False))    
    return(render_template("register.html", title = "Register", form = form))

@app.route("/usernamecheck", methods = ["POST"])
def check_username_availability():
    check_username = request.form['username']
    if(check_username):
        all_usernames = [i.json()['username'] for i in Users.query.all()]
        if(check_username in all_usernames):
            resp = "not available"
        else:
            resp =  "available"
    else:
        resp = "<span style='color: red;'>Server Error</span>";
    return(jsonify(resp))

@app.route("/emailcheck", methods = ["POST"])
def check_email_availability():
    check_email = request.form['email']
    print(check_email)
    if(check_email):
        all_emails = [i.json()['email'] for i in Users.query.all()]
        if(check_email in all_emails):
            resp = "not available"
        else:
            resp =  "available"
    else:
        resp = "<span style='color: red;'>Server Error</span>";
    return(jsonify(resp))

@app.route("/login", methods = ["GET", "POST"])
def login():
    if(current_user.is_authenticated):
        return(redirect(url_for('playquiz')))
    form = LoginForm()
    if(form.validate_on_submit()):
        user = Users.query.filter_by(username = form.username.data).first()
        if(user and bcrypt.check_password_hash(user.password, form.password.data)):
            login_user(user, remember = form.remember.data)
            next_page = request.args.get('next')
            if(next_page):
                return(redirect(next_page))
            return(redirect(url_for('home')))
        else:
            return(render_template("login.html", title = "Login", form = form, unsuccessful = True))
    return(render_template("login.html", title = "Login", form = form, unsuccessful = False))

@app.route("/account")
@login_required
def account():
    scores = []
    avg_score = 0
    all_results = Results.query.filter_by(userid = current_user.userid)
    for result in all_results:
        if(result.score < 0):
            continue
        new_result = {'Category': result.json()['category'],
        'Score': result.json()['score'],
        'Timestamp': result.json()['timestamp'].strftime("%d %b, %Y %I:%M %p"),
        'ID': result.resultid
        }
        avg_score += result.json()['score']
        scores.append(new_result)
    if(len(scores) == 0):
        avg_score = 0
    else:
        avg_score/=len(scores)
    avg_score = round(avg_score, 2)
    return(render_template('account.html', title = 'Account', leaderboard = scores, avg_score = avg_score))

@app.route("/logout")
def logout():
    logout_user()
    return(redirect(url_for('home')))