from flask import Flask
from flask import render_template
from flask import request, url_for, redirect, session, flash
from datetime import date
from datetime import time
from datetime import datetime
import dbHandler
import re
from hashlib import md5

app = Flask(__name__)
app.config['SECRET_KEY'] = 'e5ac358c-f0bf-11e5-9e39-d3b532c10a28'

@app.after_request
def after_request(response):
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    return response

@app.route('/', methods=['POST', 'GET'])
@app.route('/home', methods=['POST', 'GET'])
def index():
    if 'username' in session:
        username = session['username']
        if re.match( "^.*@.*$", username):
            return render_template('recruiter_dashboard.html', username=username)
        else:
            return render_template('student_dashboard.html', username=username)
    return render_template('index.html')

@app.route('/register', methods=['POST', 'GET'])
def register():
    if 'username' in session:
        return redirect(url_for('index'))
    else:
        return render_template('register.html')

@app.route('/student_register', methods=['POST', 'GET'])
def student_register():
    if 'username' in session:
        return redirect(url_for('index'))
    if request.method == 'POST':
        username = request.form['username']
        if not dbHandler.uniqstudent(username):
            return render_template('register.html', notUniq="nonunique")
        password = request.form['password']
        email = request.form['email']
        name = request.form['name']
        age = request.form['age']
        college = request.form['college']
        year = request.form['year']
        dbHandler.insertStudent(username, password, email, year, college, age, name)
        session['username'] = username
        return redirect(url_for('index'))
    else:
        return render_template('register.html')

@app.route('/recruiter_register', methods=['POST', 'GET'])
def recruiter_register():
    if 'username' in session:
        return redirect(url_for('index'))
    if request.method == 'POST':
        email = request.form['email']
        if not dbHandler.uniqrecruiter(email):
            return render_template('register.html', notUniq="nonunique")
        password = request.form['password']
        company = request.form['company']
        dbHandler.insertRecruiter(company, password, email)
        session['username'] = email
        return redirect(url_for('index'))
    else:
        return render_template('register.html')

@app.route('/login', methods=['POST', 'GET'])
def login():
    if 'username' in session:
        return redirect(url_for('index'))
    else:
        return render_template('login.html')

@app.route('/student_login', methods=['POST', 'GET'])
def student_login():
    if 'username' in session:
        return redirect(url_for('index'))
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if dbHandler.allowLoginStudent(username, password):
            session['username'] = username
            return redirect(url_for('index'))
        else:
            return render_template('login.html', failedLogin="failed")
    else:
        return render_template('login.html')

@app.route('/recruiter_login', methods=['POST', 'GET'])
def recruiter_login():
    if 'username' in session:
        return redirect(url_for('index'))
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        if dbHandler.allowLoginRecruiter(email, password):
            session['username'] = email
            return redirect(url_for('index'))
        else:
            return render_template('login.html', failedLogin="failed")
    else:
        return render_template('login.html')

@app.route('/logout')
def logout():
    if 'username' in session:
        session.pop('username', None)
    return redirect(url_for('index'))


if __name__ == '__main__':
    app.run(debug=True)