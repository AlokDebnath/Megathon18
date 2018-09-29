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


def uniq(username):
    con = sql.connect("database.db")
    cur = con.cursor()
    obj = cur.execute("SELECT * FROM students WHERE username='" + username + "'")
    if obj.fetchone():
        return False
    else:
        return True


def allowLogin(username, password):
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
        con = sql.connect("database.db")
        cur = con.cursor()
        cur.execute(
        "SELECT username, password FROM recruiters WHERE username=='{0}' AND password=='{1}'".format(username, password))
        if cur.fetchone():
            con.commit()
            con.close()
            return True
        else:
            con.commit()
            con.close()
            return False