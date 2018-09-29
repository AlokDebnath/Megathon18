import sqlite3 as sql
import datetime
from hashlib import md5


def insertStudent(username, password, email, name):
    con = sql.connect("database.db")
    cur = con.cursor()
    cur.execute("INSERT INTO students (name,username,password,email) VALUES (?,?,?,?)",
                (name, username, password, email))
    con.commit()
    con.close() 

def insertRecruiter(company, password, email):
    con = sql.connect("database.db")
    cur = con.cursor()
    cur.execute("INSERT INTO recruiters (company,password,email) VALUES (?,?,?)",
                (company, password, email))
    con.commit()
    con.close()

def uniqstudent(username):
    con = sql.connect("database.db")
    cur = con.cursor()
    obj = cur.execute("SELECT * FROM students WHERE username='" + username + "'")
    if obj.fetchone():
        return False
    else:
        return True

def uniqrecruiter(email):
    con = sql.connect("database.db")
    cur = con.cursor()
    obj = cur.execute("SELECT * FROM recruiters WHERE email='" + email + "'")
    if obj.fetchone():
        return False
    else:
        return True

def allowLoginStudent(username, password):
    con = sql.connect("database.db")
    cur = con.cursor()
    cur.execute(
        "SELECT username, password FROM students WHERE username=='{0}' AND password=='{1}'".format(username, password))
    if cur.fetchone():
        con.commit()
        con.close()
        return True
    else:
        con.commit()
        con.close()
        return False

def allowLoginRecruiter(email, password):
    con = sql.connect("database.db")
    cur = con.cursor()
    cur.execute(
        "SELECT email, password FROM recruiters WHERE email=='{0}' AND password=='{1}'".format(email, password))
    if cur.fetchone():
        con.commit()
        con.close()
        return True
    else:
        con.commit()
        con.close()
        return False

def getCompany(email):
    con = sql.connect("database.db")
    cur = con.cursor()
    obj = cur.execute(
        "SELECT company FROM recruiters WHERE email=='{0}'".format(email))
    obj = obj.fetchone()
    con.commit()
    con.close()
    return obj

def getCompanyID(email):
    con = sql.connect("database.db")
    cur = con.cursor()
    obj = cur.execute(
        "SELECT id FROM recruiters WHERE email=='{0}'".format(email))
    obj = obj.fetchone()
    con.commit()
    con.close()
    return obj[0]

def createJobOpening(company_id, title):
    con = sql.connect("database.db")
    cur = con.cursor()
    cur.execute("INSERT INTO job_openings (company_id,title) VALUES (?,?)",
                (company_id, title))
    con.commit()
    con.close()

def getJobOpenings(email):
    company_id = getCompanyID(email)
    con = sql.connect("database.db")
    cur = con.cursor()
    obj = cur.execute("SELECT title FROM job_openings WHERE company_id=='{0}'".format(company_id))
    obj = obj.fetchall()
    con.commit()
    con.close()
    return obj

def getJobs(title):
    con = sql.connect("database.db")
    cur = con.cursor()
    obj = cur.execute("SELECT company FROM recruiters where id==(SELECT company_id from job_openings WHERE title=='{0}')".format(title))
    obj = obj.fetchall()
    con.commit()
    con.close()
    return obj

def getCompanies(title):
    con = sql.connect("database.db")
    cur = con.cursor()
    obj = cur.execute("SELECT company FROM recruiters where company=='{0}'".format(title))
    obj = obj.fetchall()
    con.commit()
    con.close()
    return obj