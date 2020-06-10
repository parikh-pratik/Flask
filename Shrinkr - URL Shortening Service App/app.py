#Importing the modules
from flask import Flask, render_template, redirect, url_for, request
from forms import URLForm
import string
import random
import sqlite3

#CONFIGURATIONS
DATABASE = 'shorten.db'
DEBUG = False
SECRET_KEY = 'mysegjhfygtr3w456tygfvcret'
PORT = 8000

#Variables
allowed_chars = string.ascii_letters + string.digits

def connect_db():
    return(sqlite3.connect(DATABASE))

def start_db():
    conn = connect_db()
    curr = conn.cursor()
    curr.execute('CREATE TABLE IF NOT EXISTS short (id INTEGER PRIMARY KEY, key TEXT, URL TEXT, hits INTEGER);')
    conn.commit()
    conn.close()

def run_select_query(query, args = ()):
    conn = connect_db()
    curr = conn.cursor()
    curr.execute(query, args)
    rows = curr.fetchall()
    conn.close()
    return(rows)

def insert_db(fields = (), values = ()):
    conn = connect_db()
    curr = conn.cursor()
    query = "INSERT INTO short (id, %s) VALUES (NULL, %s)" % (', '.join(fields), ', '.join(['?'] * len(values)) )
    curr.execute(query, values)
    conn.commit()
    conn.close()

def view_all_entries(sortby):
    if(sortby == 'hitsasc'):
        query = 'SELECT key, URL, hits FROM short ORDER BY hits ASC;'
    elif(sortby == 'hitsdesc'):
        query = 'SELECT key, URL, hits FROM short ORDER BY hits DESC;'
    elif(sortby == 'dateasc'):
        query = 'SELECT key, URL, hits FROM short ORDER BY id ASC;'
    elif(sortby == 'datedesc' or sortby == ''):
        query = 'SELECT key, URL, hits FROM short ORDER BY id DESC;'
    else:
        return("")
    return(run_select_query(query))

def increment_hits(key):
    conn = connect_db()
    curr = conn.cursor()
    hits = run_select_query("SELECT hits from short WHERE key = ?", (key,))[0][0] + 1
    curr.execute("UPDATE short SET hits = ? WHERE key = ?", (hits, key))
    conn.commit()
    conn.close()

def shorten_it(URL, length):
    do_it_again = True
    while(do_it_again is True):
        key = ''.join([random.choice(allowed_chars) for _ in range(length)])
        do_it_again = False
        all_entries = view_all_entries(sortby = None)
        if(all_entries is None):
            break
        for i in all_entries:
            if(i[1] == key):
                do_it_again = True
    insert_db(fields = ("key", "URL", 'hits'), values = (key, URL, 0))
    return(key)
    
app = Flask(__name__)
app.config['SECRET_KEY'] = SECRET_KEY
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0

@app.route("/visit/<entered_key>")
def visit(entered_key):
    record = run_select_query("SELECT URL from short WHERE key = ?", args = (entered_key,))
    if(len(record) == 0):
        return(render_template("404.html", key = entered_key))
    else:
        increment_hits(key = entered_key)
        return(redirect(record[0][0], code = 302))

@app.route("/shorten", methods = ["POST"])
def shorten():
    URL = request.form['url']
    if(len(URL) <= 5):
        return(redirect(url_for('index', msg = "tooshort")))
    elif(len(URL) >= 255):
        return(redirect(url_for('index', msg = "toolong")))
    else:
        record = run_select_query("SELECT key from short WHERE URL = ?", args = (URL,))
        if(len(record) == 0):
            key = shorten_it(URL, 5)
        else:
            key = record[0][0]
        return(render_template("short.html", long = URL, short = key))

@app.route("/")
@app.route("/index")
@app.route("/index/<msg>")
def index(msg = ""):
    start_db()
    form = URLForm()
    if(form.validate_on_submit()):
        print("Validate hua")
        return redirect(url_for('shorten'))
    if(msg == "tooshort"):
        msg = "The given URL is too short. Must be between 6 and 250 characters."
    elif(msg == "toolong"):
        msg = "The given URL is too long. Must be between 6 and 250 characters."
    elif(msg == ""):
        msg = "URL length must be between 6 and 250 characters."
    else:
    	return(render_template("404.html"))
    return(render_template("index.html", form = form, msg = msg))


@app.route("/stats/<sortby>")
@app.route("/stats")
def stats(sortby = ''):
    start_db()
    stats = view_all_entries(sortby = sortby)
    if(stats == ""):
        return(render_template("404.html"))
    print(stats)
    return render_template("stats.html", stats = stats)

@app.before_request
def before_request():
    start_db()

@app.errorhandler(404) 
def not_found(e):
    return(render_template("404.html"))

if __name__ == '__main__':
    app.run(debug = DEBUG, port = PORT)

