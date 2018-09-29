import sqlite3 as sql
import datetime
from hashlib import md5


def insertStudent(username, password, email, year, college, age, name):
    con = sql.connect("database.db")
    cur = con.cursor()
    cur.execute("INSERT INTO students (name,age,college,year,username,password,email) VALUES (?,?,?,?,?,?,?)",
                (name, age, college, year, username, password, email))
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