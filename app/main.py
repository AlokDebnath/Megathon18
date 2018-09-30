from flask import Flask
from flask import render_template, send_from_directory
from flask import request, url_for, redirect, session, flash
from datetime import date
from datetime import time
from datetime import datetime
from werkzeug import secure_filename
import dbHandler
import re, os
import json
import requests
from hashlib import md5
import textract
import nltk
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, Text
from sqlalchemy.orm import sessionmaker
import sqlite3 as sql

app = Flask(__name__)
app.config['SECRET_KEY'] = 'e5ac358c-f0bf-11e5-9e39-d3b532c10a28'

#### From processing.py ####



def noun_finder(tokenized_words):
    # NN is more generic, NNP is more specific. Check which one yields better performance
    l1 = ['>', '<', 'nbsp']
    tokenized_words = [x for x in tokenized_words if x not in l1 and len(x) > 2 and x[0] != '/']
    is_noun = lambda pos: pos[:3] == 'NNP'
    #is_noun = lambda pos: pos[:2] == 'NN'
    nouns = [word for (word, pos) in nltk.pos_tag(tokenized_words) if is_noun(pos)]
    return nouns

# For Data input, need to tokenize it then run noun finder


def score_2_list(nounlist1, nounlist2):
    score = 0
    nounhash = {}
    for noun in nounlist1:
        if noun not in nounhash.keys():
            nounhash[noun] = 1
        else:
            nounhash[noun] += 1
    for noun in nounlist2:
        if noun not in nounhash.keys():
            nounhash[noun] = 1
        else:
            nounhash[noun] += 1
    for i in nounhash.keys():
        if nounhash[i] > 1:
            score += 1
    return score

def score_3_list(nounlist1, nounlist2, nounlist3):
    for noun in nounlist1:
        if noun not in nounhash.keys():
            nounhash[noun] = 1
        else:
            nounhash[noun] += 1
    for noun in nounlist2:
        if noun not in nounhash.keys():
            nounhash[noun] = 1
        else:
            nounhash[noun] += 1
    for noun in nounlist3:
        if noun not in nounhash.keys():
            nounhash[noun] = 1
        else:
            nounhash[noun] += 1
    for i in nounhash.keys():
        if nounhash[i] == 2:
            score += 1
        if nounhash[i] == 3:
            score += 10
    return score

def getJobDesc():
    job_desclist = []
    lst = getJobDescdb()
    for i in lst:
        job_desclist.append([i[1], i[0]])
    return job_desclist


def getJobDescdb():
    con = sql.connect("database.db")
    cur = con.cursor()
    obj = cur.execute("SELECT id, job_description FROM job_openings")
    obj = obj.fetchall()
    con.commit()
    con.close()
    return obj



def read_job_desc():
    joblist = getJobDesc()
    titlemap = []
    # joblist is a list of lists where the nested list is [job_description, job_title]
    counter = 0
    for job in joblist:
        counter += 1
        titlemap.append([job[1], noun_finder(nltk.word_tokenize(job[0]))]) # job[0] is always the description
        if counter == 100:
            break
    print(titlemap)
    return titlemap


def get_resumes(n, path):
        all_cvs = list()
        for index, folder in enumerate(os.listdir(path)):
            for index2, file in enumerate(os.listdir(path + folder)):
                if (file[-3:]) in ['pdf', 'docx']:
                        text = textract.process("./resumes/" + folder + "/" + file)
                        cleaned_cv = (str(text)).replace('\\n', '\n')
                        regex = re.compile('^x..$')
                        cleaned_cv = list(filter(lambda x: not regex.search(x), re.findall("[A-Z]{2,}(?![a-z])|[\w]+", cleaned_cv)))
                        all_cvs.append((folder, cleaned_cv))
                else:
                    continue
                if index >= 1000:
                    break
        # print(all_cvs[n])
        return all_cvs

# Given one job description, clean and create nounlist
def input_job_desc(description):
    scorelist = {}
    nounlist1 = noun_finder(nltk.word_tokenize(description))
    all_resumes = get_resumes(1000, './resumes/')
    count = 0
    for resume in all_resumes:
        nounlist2 = noun_finder(resume[1])
        score = score_2_list(nounlist1, nounlist2)
        scorelist[resume[0]] = score
        count += 1
        print(count)

    return scorelist

def input_stud_desc(resumefile):
    text = textract.process(resumefile)
    cleaned_cv = (str(text)).replace('\\n', '\n')
    regex = re.compile('^x..$')
    cleaned_cv = list(filter(lambda x: not regex.search(x), re.findall("[A-Z]{2,}(?![a-z])|[\w]+", cleaned_cv)))
    nounlist1 = noun_finder(cleaned_cv)
    print(nounlist1)
    scorelist = {}
    count = 0
    # All job descriptions
    jobs_descs = read_job_desc()
    for desc in jobs_descs:
        nounlist2 = desc[1]
        print(nounlist2)
        score = score_2_list(nounlist1, nounlist2)
        scorelist[desc[0]] = score
        count += 1
        print(count)
    return scorelist




#### End processing.py ####









def make_dir(upload_dir):
    if not os.path.exists(upload_dir):
        os.makedirs(upload_dir)


# @app.after_request
# def after_request(response):
#     response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
#     return response

@app.route('/', methods=['POST', 'GET'])
@app.route('/home', methods=['POST', 'GET'])
def index():
    if 'username' in session:
        username = session['username']
        # If company
        if re.match( "^.*@.*$", username):
            company = dbHandler.getCompany(username)
            jobopenings = dbHandler.getJobOpenings(username)
            students = dbHandler.getAllStudents()
            return render_template('recruiter_dashboard.html', students=students, company=company[0], jobopenings=jobopenings, recruiter=True)
        else:
            resume = list_resume(username)
            studentdata = dbHandler.getStudentData(username)
            companies = dbHandler.getAllCompanies()
            return render_template('student_dashboard.html', companies=companies, username=username, resume=resume, student=True, studentdata=studentdata)
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
        dbHandler.insertStudent(username, password, email, name)
        upload_dir = './resumes/'
        upload_dir = upload_dir + username
        make_dir(upload_dir)
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

def list_resume(username):
    path = './resumes/' + username
    onlyfiles = [f for f in os.listdir(path) if os.path.isfile(os.path.join(path, f))]
    if len(onlyfiles) == 0:
        return False
    else:
        return onlyfiles[0]

@app.route('/uploader', methods = ['GET', 'POST'])
def upload_resume():
    if 'username' in session:
        username = session['username']
        if request.method == 'POST':
            file = request.files['file']
            upload_dir = './resumes/'
            upload_dir = upload_dir + username
            filename = secure_filename(file.filename)
            file.save(os.path.join(upload_dir, filename))
    return redirect(url_for('index'))

@app.route('/downloader/<username>', methods = ['GET', 'POST'])
def download_resume(username):
    resume = list_resume(username)
    return send_from_directory('./resumes/' + username, resume, as_attachment=True)

@app.route('/deleter', methods = ['GET', 'POST'])
def delete_resume():
    username = session['username']
    resume = list_resume(username)
    os.remove('./resumes/' + username + '/' + str(resume))
    return redirect(url_for('index'))

@app.route('/create_opening', methods = ['GET', 'POST'])
def create_job_opening():
    if 'username' in session:
        if request.method == 'POST':
            email = session['username']
            title = request.form['title']
            job_description = request.form['job_description']
            company_id = dbHandler.getCompanyID(email)
            dbHandler.createJobOpening(company_id, title, job_description)
    return redirect(url_for('index'))

@app.route('/delete_opening', methods = ['GET', 'POST'])
def delete_job_opening():
    if 'username' in session:
        if request.method == 'POST':
            id = request.args.get('id')
            dbHandler.deleteJobOpening(id)
    return redirect(url_for('index'))

@app.route('/search', methods=['GET', 'POST'])
def search_jobs():
    if 'username' in session:
        if request.method == 'POST':
            title = request.form['search']
            jobs = dbHandler.getJobs(title)
            companies = dbHandler.getCompanies(title)
            return render_template('job_openings.html', jobs=jobs, companies=companies)
    return redirect(url_for('index'))


@app.route('/processed_search', methods = ['GET', 'POST'])
def processed_search():
    if 'username' in session:
        username = session['username']
        if not list_resume(username):
            return "Please Input a Resume"
        resumename = list_resume(username)
        filepath = "./resumes/" + username + "/" + resumename
        scorelist = input_stud_desc(filepath)
        return str(scorelist)

@app.route('/processed_search_candidate', methods = ['GET', 'POST'])
def processed_search_candidate():
    if 'username' in session:
        company_email = session['username']
        id = request.args.get('id')
        description = dbHandler.getJobDescription(id)
        scorelist = input_job_desc(description[0])
        return str(scorelist)


@app.route('/user_search', methods=['GET', 'POST'])
def search_candidate():
    if 'username' in session:
        if request.method == 'POST':
            username = request.form['search']
            name = dbHandler.getUser(username)
            studentdata = dbHandler.getStudentData(username)
            if not studentdata:
                return redirect(url_for('index'))
            resume = list_resume(username)
            studentdata = dbHandler.getStudentData(username)
            return render_template('student_dashboard.html', studentdata=studentdata, student=False, username=username, name=name[0], resume=resume)
        username = request.args.get('student')
        name = dbHandler.getUser(username)
        resume = list_resume(username)
        studentdata = dbHandler.getStudentData(username)
        return render_template('student_dashboard.html', studentdata=studentdata, student=False, username=username, name=name[0], resume=resume)
    return redirect(url_for('index'))

@app.route('/company', methods=['GET', 'POST'])
def viewCompany():
    company_id = request.args.get('company_id')
    if 'username' in session:
        email = dbHandler.getCompanyEmail(company_id)
        company = dbHandler.getCompany(email)
        jobopenings = dbHandler.getJobOpenings(email)
        return render_template('recruiter_dashboard.html', company=company[0], jobopenings=jobopenings, recruiter=False)
    return redirect(url_for('index'))

@app.route('/job', methods=['GET', 'POST'])
def viewJob():
    job_id = request.args.get('job_id')
    print(job_id)
    if 'username' in session:
        jobopening = dbHandler.getJob(job_id)
        return render_template('view_job.html', jobopening=jobopening)
    return redirect(url_for('index'))

@app.route('/github', methods=['GET', 'POST'])
def add_github_link():
    if 'username' in session:
        if request.method == 'POST':
            username = session['username']
            link = request.form['github']
            dbHandler.addGithubLink(link, username)
    return redirect(url_for('index'))

@app.route('/codeforces', methods=['GET', 'POST'])
def add_codeforces_link():
    if 'username' in session:
        if request.method == 'POST':
            username = session['username']
            link = request.form['codeforces']
            dbHandler.addCodeforcesLink(link, username)
    return redirect(url_for('index'))

def getGithubDetails(github_handle):
    stars = 0
    languages = []
    response = requests.get("https://api.github.com/users/" + github_handle + "/repos")
    data = response.json()
    for repo in data:
        stars = stars + repo['stargazers_count']
        if repo['language']:
            if repo['language'] not in languages:
                languages.append(repo['language'])
    print(stars)
    print(languages)

def getCodeforcesDetails(codeforces_handle):
    rating = 0
    rank = "unavailable"
    response = requests.get("https://codeforces.com/api/user.info?handles=" + codeforces_handle)
    data = response.json()
    for user in data['result']:
        rating = user['rating']
        rank = user['rank']
    print(rating)
    print(rank)


if __name__ == '__main__':
    app.run(debug=True)
