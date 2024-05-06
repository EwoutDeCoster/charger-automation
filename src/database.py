import sqlite3
import os
import json
import datetime
import hashlib
import random
import string
import requests

def connection():
    # Connect to the database
    conn = sqlite3.connect('data/database.db')
    c = conn.cursor()
    return c, conn

def set_session(username):
    # Generate a session for the user
    randomhash = hashlib.sha256()
    randomhash.update(os.urandom(128))
    session = randomhash.hexdigest()
    # update the session in the for the user and update the expire time to 2 hours
    c, conn = connection()
    c.execute("UPDATE credentials SET session = ?, expire = ? WHERE username = ?", (session, datetime.datetime.now() + datetime.timedelta(days=21), username))
    conn.commit()
    conn.close()
    return session

def check_session(session):
    # Check if the session is valid
    c, conn = connection()
    c.execute("SELECT * FROM credentials WHERE session = ?", (session,))
    result = c.fetchone()
    conn.close()
    try:
        if result:
            # cast result[4] to datetime.datetime
            sessionexpiry = datetime.datetime.strptime(result[4], '%Y-%m-%d %H:%M:%S.%f')
            if sessionexpiry > datetime.datetime.now():
                return True
            else:
                # remove the session from the database
                c, conn = connection()
                c.execute("UPDATE credentials SET session = ?, expire = ? WHERE session = ?", ("", "", session))
                conn.commit()
                conn.close()
                return False
        else:
            return False
    except Exception as e:
        print(e)
        return False

def get_user_info(session):
    # Get the user from the session
    c, conn = connection()
    c.execute("SELECT * FROM credentials WHERE session = ?", (session,))
    result = c.fetchone()
    conn.close()
    try:
        if result:
            return result[0], result[2], result[3]
        else:
            return False
    except Exception as e:
        print(e)
        return False

def checkCredentials(user, password):
    # Check if the credentials are correct
    c, conn = connection()
    c.execute("SELECT * FROM credentials WHERE username = ?", (user,))
    result = c.fetchone()
    conn.close()
    try:
        if result:
            if result[1] == encryptPassword(password):
                return True
            else:
                return False
        else:
            return False
    except Exception as e:
        print(e)
        return False


def encryptPassword(password):
    # Encrypt the password without salt
    hash = hashlib.sha256()
    # Encode the password to bytes
    encoded = password.encode()
    hash.update(encoded)
    return hash.hexdigest()

def createUser(user, password, company):
    # Create a new user
    c, conn = connection()
    c.execute("INSERT INTO credentials (username, password, email) VALUES (?, ?, ?)", (user, encryptPassword(password), company))
    conn.commit()
    conn.close()

def deleteUser(user):
    # Delete a user
    c, conn = connection()
    c.execute("DELETE FROM credentials WHERE username = ?", (user,))
    conn.commit()
    conn.close()
    
def getCompany(user):
    # Get the company name from the session
    c, conn = connection()
    c.execute("SELECT company FROM credentials WHERE username = ?", (user,))
    result = c.fetchone()
    conn.close()
    try:
        if result:
            return result[0]
        else:
            return False
    except Exception as e:
        print(e)
        return False

def sessiontocompany(session):
    # Get the company name from the session
    c, conn = connection()
    c.execute("SELECT company FROM credentials WHERE session = ?", (session,))
    result = c.fetchone()
    conn.close()
    try:
        if result:
            return result[0]
        else:
            return False
    except Exception as e:
        print(e)
        return False
    
def fillTokens(bedrijf):
    # generate 5 tokens and add them to the database
    c, conn = connection()
    for i in range(5):
        #generate a random hash256 string
        token = hashlib.sha256(os.urandom(32)).hexdigest()
        # the table has the fields token, company
        c.execute("INSERT INTO tokens (token, company) VALUES (?, ?)", (token, bedrijf))
    conn.commit()
    return True

def validateToken(token):
    # Check if the token is valid
    c, conn = connection()
    c.execute("SELECT * FROM tokens WHERE token = ?", (token,))
    result = c.fetchone()
    conn.close()
    try:
        if result:
            return True
        else:
            return False
    except Exception as e:
        print(e)
        return False
    
def getUserNameBySession(session):
    # Get the user name from the session
    c, conn = connection()
    c.execute("SELECT name FROM credentials WHERE session = ?", (session,))
    result = c.fetchone()
    conn.close()
    try:
        if result:
            return result[0]
        else:
            return False
    except Exception as e:
        print(e)
        return False

def getPId(email):
    # Get the person id from the email
    c, conn = connection()
    c.execute("SELECT pId FROM credentials WHERE username = ?", (email,))
    result = c.fetchone()
    conn.close()
    try:
        if result:
            return result[0]
        else:
            return False
    except Exception as e:
        print(e)
        return False

def setPId(email, pId):
    # Set the person id for the user
    c, conn = connection()
    c.execute("UPDATE credentials SET pId = ? WHERE username = ?", (pId, email))
    conn.commit()
    conn.close()
    return True
    
def setPassword(email, pId, password):
    # Set the password for the user
    c, conn = connection()
    c.execute("UPDATE credentials SET password = ? WHERE username = ? AND pId = ?", (encryptPassword(password), email, pId))
    conn.commit()
    # remove the pId from the user
    c.execute("UPDATE credentials SET pId = ? WHERE username = ? AND pId = ?", ("", email, pId))
    conn.commit()
    conn.close()
    return True

def userExists(email):
    # Check if the user exists
    c, conn = connection()
    c.execute("SELECT * FROM credentials WHERE username = ?", (email,))
    result = c.fetchone()
    conn.close()
    try:
        if result:
            return True
        else:
            return False
    except Exception as e:
        print(e)
        return False
    
def userToSession(username):
    # Get the session from the user
    c, conn = connection()
    c.execute("SELECT session, expire FROM credentials WHERE username = ?", (username,))
    result = c.fetchone()
    conn.close()
    try:
        if result:
            return result
        else:
            return False
    except Exception as e:
        print(e)
        return False
    
def getallcredentials():
    c, conn = connection()
    c.execute("SELECT * FROM credentials")
    result = c.fetchall()
    conn.close()
    return result

def renewSession(session):
    try:
        # Renew the session
        c, conn = connection()
        c.execute("UPDATE credentials SET expire = ? WHERE session = ?", (datetime.datetime.now() + datetime.timedelta(days=21), session))
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        print(e)
        return False
