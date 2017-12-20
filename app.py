#!/usr/env/bin python
#! -*- coding: utf-8 -*-
"""IS211 Final Project - Blog App"""

from flask import Flask, session, render_template, request, redirect, flash, url_for
from functools import wraps
import datetime
import re
import sqlite3

# set connection and cursor as global variables so that all functions can use
connection = sqlite3.connect('blog.db')
# use row factory to access values by column name instead of index
connection.row_factory = sqlite3.Row
cursor = connection.cursor()

def init_db():
    with open('schema.sql') as db:
        cursor.executescript(db.read())

    # test data for populating table; separated from queries for security
    testposts = [
        (1, 'admin', 'First Post', '2017-12-01', 'This is the first blog post.', 'True'),
        (2, 'admin', 'Second Post', '2017-12-02', 'This is the second blog post.', 'True'),
        (3, 'admin', 'Third Post', '2017-12-03', 'This is the third blog post.', 'True')
    ]
    # populates tables with test data
    cursor.executemany('INSERT into blogposts VALUES (?,?,?,?,?,?)', testposts)
    connection.commit()

app = Flask(__name__)
app.secret_key = 'X!4TN[/2|J37b8z'

def login_required(f):
    # basic login check function found in Flask tutorial
   @wraps(f)
   def wrap(*args, **kwargs):
       if 'logged_in' in session and session['logged_in'] == True:
           return f(*args, **kwargs)
       else:
           return redirect('/login')
   return wrap

@app.route('/')
def index():
    published = "True"
    if 'user' in session:
        user = session['user']
    else:
        user = 'Guest'
    cursor.execute('SELECT * FROM blogposts WHERE publish=? ORDER BY id DESC', [published])
    blogposts = cursor.fetchall()
    return render_template('index.html', blogposts=blogposts, user=user)

@app.route('/login', methods=['GET','POST'])
def login():
    error = None
    if request.method == 'POST':
        if request.form['username'] != 'admin' or \
                request.form['password'] != 'password':
            session['logged_in'] = False
            session['user'] = 'Guest'
            error = 'Wrong username and/or password. Please try again.'
        else:
            session['user'] = request.form['username']
            session['logged_in'] = True
            return redirect('/dashboard')
    return render_template('login.html', error=error)

@app.route('/logout', methods=['GET'])
def logout():
    session['user'] = 'Guest'
    session['logged_in'] = False
    return redirect('/')

@app.route('/dashboard')
@login_required
def dashboard():
    # queries db, passes results to template
    cursor.execute('SELECT * FROM blogposts ORDER BY id DESC')
    blogposts = cursor.fetchall()
    return render_template('dashboard.html', blogposts=blogposts)

@app.route('/delete/<id>')
@login_required
def delete_post(id):
    # deletes the specified post and returns to dashboard
    cursor.execute('DELETE from blogposts WHERE id = ?', id)
    connection.commit()
    return redirect('/dashboard')

@app.route('/add', methods=['GET','POST'])
@login_required
def add():
    # allows user to add an entry
    error = None
    if request.method == 'POST':
        # validate data, return error if invalid
        if re.match(r'^\s*$', request.form['title']) \
                or re.match(r'^\s*$', request.form['entry']):
            error = 'Cannot have blank field(s). Please try again.'
        # if validation passes, update db, redirect to homepage
        else:
            title = request.form['title']
            entry = request.form['entry']
            postdate = datetime.date.today()
            author = session['user']
            published = "True"
            cursor.execute(
                'INSERT INTO blogposts(author, title, postdate, entry, publish) '
                'VALUES (?,?,?,?,?)', (author, title, postdate, entry, published))
            connection.commit()
            return redirect('/')
    return render_template('add.html', error=error)

@app.route('/edit/<id>', methods=['GET','POST'])
@login_required
def edit(id):
    error = None
    if request.method == 'GET':
        cursor.execute('SELECT * FROM blogposts WHERE id=?', id)
        blogpost = cursor.fetchone()
        return render_template('edit.html', blogpost=blogpost)
    elif request.method == 'POST':
        # validate data, return error if invalid
        if re.match(r'^\s*$', request.form['entry']):
            error = 'Cannot have blank field(s). Please try again.'
            cursor.execute('SELECT * FROM blogposts WHERE id=?', id)
            blogpost = cursor.fetchone()
            return render_template('edit.html', error=error, blogpost=blogpost)
        # if validation passes, update db, redirect to homepage
        else:
            entry = request.form['entry']
            id = request.form['blogid']
            cursor.execute('UPDATE blogposts SET entry=? WHERE id=?', (entry,id))
            connection.commit()
            return redirect('/')

@app.route('/permalink/<id>')
def permalink(id):
    # queries db, passes results to template
    cursor.execute('SELECT * FROM blogposts WHERE id=?', id)
    blogpost = cursor.fetchone()
    return render_template('permalink.html', blogpost=blogpost)

@app.route('/publish/<id>')
@login_required
def publish_post(id):
    # toggles the publish/unpublish quality of the specified post and returns to dashboard
    cursor.execute('SELECT * FROM blogposts WHERE id=?', id)
    blogpost = cursor.fetchone()
    if blogpost['publish'] == "True":
        published = "False"
    elif blogpost['publish'] == "False":
        published = "True"
    cursor.execute('UPDATE blogposts SET publish=? WHERE id=?', (published, id))
    connection.commit()
    return redirect('/dashboard')

if __name__ == '__main__':
    init_db()
    app.run()