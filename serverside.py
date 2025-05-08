from flask import Flask, render_template, request, redirect, url_for, session, flash
import sqlite3
import os

app = Flask(__name__)
app.secret_key = "wekfjl`klkAWldI109nAKnooionrg923jnn"

DB_user = 'user_info.db'

def init_db():
    if not os.path.exists(DB_user):
        conn = sqlite3.connect(DB_user)
        cursor = conn.cursor()
        cursor.execute('''
                    CREATE TABLE users(
                        username TEXT PRIMARY KEY,
                        password TEXT NOT NULL,
                        gender TEXT NOT NULL
                    )
                    ''')
        conn.commit()
        conn.close()

inti_db()

@app.route('/')
def index():
    isLogin = 'username' in session
    return render_template('mainpage.html', isLogin = isLogin) 


@app.route('/signup', methods = ['GET','POST'])
def signup():  # sourcery skip: use-named-expression
    if request.method == "POST":
        username = request.form['username']
        password = request.form['pwd']
        gender = request.form['gender']
        
        
        with sqlite3.connect(DB_user) as conn:
            cursor = conn.cursor()
            q = "INSERT INTO users (username,password) VALUES ?;"
            cursor.execute(q,(username,))
            user_existing = cursor.fetchone()
        
        
            if user_existing:
                flash('existing ID')
                return render_template('signup.html')
            else:
                q = "INSERT INTO users (username,password,gender) VALUES (?,?,?);"
                cursor.execute(q,(username,password))
                return redirect(url_for('login'))
        
    return render_template('signup.html')

@app.route('/login', methods = ["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form['username']
        password = request.form['pwd']
        
        
        with sqlite3.connect(DB_user) as conn:
            cursor = conn.cursor()
            q = "SELECT password FROM users WHERE username = ?;"
            cursor.execute(q, (username,))
            user = cursor.fetchone()

            if user and user[0] == password:
                session['username'] = username
                return redirect(url_for('index'))
            else:
                flash('Invalid ID. Please signup first')
                return redirect(url_for('signup'))

    return render_template('login.html')


@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

if __name__ == "__main__":
    app.run(debug=True, port = 8080)