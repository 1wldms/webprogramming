from flask import Flask, render_template, request, redirect, url_for, session
import sqlite3

app = Flask(__name__)
app.secret_key = "wekfjl`klkAWldI109nAKnooionrg923jnn"

@app.route('/')
def index():
    ifLogin = False
    if 'username' in session:
        isLogin = True
    return render_template('mainpage.html', isLogin = isLogin) 


users = {}

@app.route('/signup', methods = ['GET','POST'])
def signup():
    if request.method == "POST":
        username = request.form['username']
        password = request.form['pwd']
        
        
        conn = sqlite3.connect('test.db')
        cursor = conn.cursor()
        q = "INSERT INTO users (username,password) VALUES ?;"
        cursor.execute(q,(username,))
        user_existing = cursor.fetchone()
        
        
        if user_existing:
            flash('existing ID')
            conn.close()
            return render_template('signup.html')
        else:
            q = "INSERT INTO users (username,password) VALUES (?, ?);"
            cursor.execute(q,(username,password))
            conn.commit()
            conn.close()
            flash('login~! good')
            return redirect(url_for('login'))
        
    return render_template('signup.html')

@app.route('/login', methods = ["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form['username']
        password = request.form['pwd']
        
        
        with sqlite3.connect('test.db') as conn:
            cursor = conn.cursor()
            q = "SELECT password FROM users WHERE username = ?;"
            cursor.execute(q, (username, password))
            user = cursor.fetchone()

            if user:
                return redirect(url_for('mainpage'))
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