#!/usr/env/bin python
#! -*- coding: utf-8 -*-
"""IS211 Final Project - Blog App"""

from flask import Flask, session, render_template, request, redirect, flash
import datetime
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
        (1, 'admin', 'First Post', '2017-12-01', 'This is the first blog post.'),
        (2, 'admin', 'Second Post', '2017-12-02', 'This is the second blog post.'),
        (3, 'admin', 'Third Post', '2017-12-03', 'This is the third blog post.')
    ]
    # populates tables with test data
    cursor.executemany('INSERT into blogposts VALUES (?,?,?,?,?)', testposts)
    connection.commit()

app = Flask(__name__)
app.secret_key = 'X!4TN[/2|J37b8z'

@app.route('/')
def index():
    if session['logged_in'] == True:
        user = session['user']
    else:
        user = 'Guest'
    cursor.execute('SELECT * FROM blogposts ORDER BY id DESC')
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
    session['logged_in'] = False
    return index()

@app.route('/dashboard')
def dashboard():
    if session['logged_in'] == True:
        cursor.execute('SELECT * FROM blogposts ORDER BY id DESC')
        blogposts = cursor.fetchall()
        return render_template('dashboard.html', blogposts=blogposts)
    else:
        return redirect('login')

@app.route('/delete/<id>')
def delete_post(id):
    # deletes the specified post and returns to dashboard
    # first verify logged-in status
    if session['logged_in'] == True:
        cursor.execute('DELETE from blogposts WHERE id = ?', id)
        return redirect('/dashboard')
    else:
        error = 'You must be logged in to perform this action.'
        return redirect('/login', error=error)

@app.route('/add', methods=['GET','POST'])
def add():
    # first verify logged-in status
    if session['logged_in'] == True:
        error = None
        if request.method == 'POST':
            # validate data, return error
            if request.form['title'] == '' or request.form['entry'] == '':
                error = 'Cannot have blank field(s). Please try again.'
            # update db, redirect to homepage
            else:
                title = request.form['title']
                entry = request.form['entry']
                postdate = datetime.date.today()
                author = session['user']
                cursor.execute(
                    'INSERT INTO blogposts(author, title, postdate, entry) '
                    'VALUES (?,?,?,?)', (author, title, postdate, entry))
                return redirect('/')
        return render_template('add.html', error=error)
    else:
        return redirect('/login')

@app.route('/edit/<id>', methods=['GET','POST'])
def edit(id):
    # first verify logged-in status
    if session['logged_in'] == True:
        error = None
        if request.method == 'POST':
            # validate data, return error
            if request.form['entry'] == '':
                error = 'Cannot have blank field(s). Please try again.'
            # update db, redirect to homepage
            else:
                entry = request.form['entry']
                id = request.form['blogid']
                cursor.execute('UPDATE blogposts SET entry=? WHERE id=?', (entry,id))
                connection.commit()
                return redirect('/')
        cursor.execute('SELECT * from blogposts WHERE id = ?', id)
        blogposts = cursor.fetchone()
        return render_template('edit.html', blogposts=blogposts)
    else:
        return redirect('/login')

if __name__ == '__main__':
    init_db()
    app.run()