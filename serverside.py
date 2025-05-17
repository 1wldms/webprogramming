from flask import Flask, render_template, request, redirect, url_for, session, flash
import sqlite3
import os
import requests
import json

app = Flask(__name__)
app.secret_key = "wekfjl`klkAWldI109nAKnooionrg923jnn"


DB_user = 'user_info.db'

def init_db():
    if os.path.exists(DB_user):
        os.remove(DB_user)
    
    conn = sqlite3.connect(DB_user)
    cursor = conn.cursor()
    cursor.execute('''
                CREATE TABLE users(
                    username TEXT PRIMARY KEY,
                    password TEXT NOT NULL,
                    gender TEXT NOT NULL
                );
                ''')
    
    cursor.execute('''
                CREATE TABLE likes(
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT NOT NULL,
                    img TEXT NOT NULL,
                    FOREIGN KEY(username) REFERENCES users(username)
                );
                ''')
    conn.commit()
    conn.close()

init_db()

@app.route('/')
def index():
    isLogin = 'username' in session
    return render_template('mainpage.html', isLogin = isLogin) 


@app.route('/signup', methods = ['GET','POST'])
def signup():  
    if request.method == "POST":
        username = request.form['username']
        password = request.form['pwd']
        gender = request.form['gender']
        
        with sqlite3.connect(DB_user) as conn:
            cursor = conn.cursor()
            q = "SELECT * FROM users WHERE username = ?"
            cursor.execute(q,(username,))
            user_existing = cursor.fetchone()
        
            if user_existing:
                flash('Existing ID')
                return render_template('signup.html')
            else:
                q = "INSERT INTO users (username,password,gender) VALUES (?,?,?);"
                cursor.execute(q,(username,password,gender))
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
                return redirect(url_for('weather_style'))
            else:
                flash("Please check your username of password again.")
                return redirect(url_for('login'))

    return render_template('login.html')

@app.route('/mypage')
def mypage():
    if 'username' not in session:
        flash('Please login.')
        return redirect(url_for('login'))
    
    username = session['username']
    
    with sqlite3.connect(DB_user) as conn:
        cursor = conn.cursor()
        
        q = "SELECT password, gender FROM users WHERE username = ?;"
        cursor.execute(q, (username,))
        user = cursor.fetchone()
        
        if not user:
            flash('Cannot find user info.')
            return redirect(url_for('signup'))
        
        password, gender = user
        
        p = "SELECT img FROM likes WHERE username = ? ORDER BY id DESC;"
        cursor.execute(p, (username,))
        likes = [row[0] for row in cursor.fetchall()]
        
    return render_template(
        "mypage.html",
        username = username,
        password = password,
        gender = gender,
        likes = likes,
    )

@app.route('/Style-It', methods=["GET"])
def weather_style():
    return render_template("weather_style.html")

@app.route('/result', methods=["POST"])
def result():
    city = request.form["city"]
    style = request.form["style"]
    
    # 날씨 API 설정
    apiKey = "발급받은Key" # 웹 사이트에 weather api, free for student 요청한 상태 
    lang = 'eng'
    units = 'metric'
    api = f"https://api.openweathermap.org/data/2.5/weather?q={city}&APPID={apiKey}&lang={lang}&units={units}"

    try:
        response = requests.get(api)
        weather_data = response.json()

        if response.status_code == 200:
            temp = weather_data['main']['temp']
            humidity = weather_data['main']['humidity']
            wind_speed = weather_data['wind']['speed']
            description = weather_data['weather'][0]['description']
        else:
            temp = humidity = wind_speed = description = "NO DATA"

    except Exception as e:
        print(f"Error fetching weather data: {e}")
        temp = humidity = wind_speed = description = "ERROR"

    return render_template("result.html",
                            city=city,
                            style=style,
                            temp=temp,
                            humidity=humidity,
                            wind_speed=wind_speed,
                            description=description)
    
    # 여기에 날씨 API + 추천 로직 넣기
    return render_template("result.html", city=city, style=style)


@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))

if __name__ == "__main__":
    app.run(debug=True, port = 8080)