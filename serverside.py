from flask import Flask, render_template, request, redirect, url_for, session, flash
import sqlite3
import os
import requests
import json
from openai import OpenAI
import traceback

app = Flask(__name__)
app.secret_key = "wekfjl`klkAWldI109nAKnooionrg923jnn"

client = OpenAI(api_key="")

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

@app.route('/result', methods=["GET","POST"])
def result():
    city = request.form["city"]
    style = request.form["style"]
    
    username = session.get('username')
    with sqlite3.connect(DB_user) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT gender FROM users WHERE username = ?;", (username,))
        result = cursor.fetchone()
        gender = result[0] if result else "unspecified"
    
    
    # 날씨 API 설정
    apiKey = "43b898019498441e6f6dfae065f1af73"
    lang = 'eng'
    units = 'metric'
    api = f"https://api.openweathermap.org/data/2.5/weather?q={city}&APPID={apiKey}&lang={lang}&units={units}"

    try:
        response = requests.get(api)
        weather_data = response.json()
        

        if response.status_code == 200:
            temp = weather_data['main']['temp']
            feels_like = weather_data['main']['feels_like']
            temp_max = weather_data['main']['temp_min']
            temp_min = weather_data['main']['temp_max']
            clouds  = weather_data['clouds']['all']
            humidity = weather_data['main']['humidity']
            wind_speed = weather_data['wind']['speed']
            description = weather_data['weather'][0]['description']
            
            if clouds == 0:
                cloud_status = "Clear sky - Blue sky with no clouds at all"
            elif clouds <= 25:
                cloud_status = "Mostly clear - Mostly sunny with a few clouds"
            elif clouds <= 50:
                cloud_status = "Partly cloudy - About half sky covered with clouds"
            elif clouds <= 84:
                cloud_status = "Mostly cloudy - Sky is mostly covered by clouds"
            else:
                cloud_status = "Overcast - Completely covered with thick clouds"
            
            if wind_speed < 0.3:
                wind_status = "Calm - Very light air, hardly noticeable"
            elif wind_speed < 1.6:
                wind_status = "Light air - Feels like still air, leaves unmoving"
            elif wind_speed < 3.4:
                wind_status = "Light breeze - Leaves rustle, wind can be felt on face"
            elif wind_speed < 5.5:
                wind_status = "Gentle breeze - Leaves and small twigs in constant motion"
            elif wind_speed < 8.0:
                wind_status = "Moderate breeze - Moves small branches, raises loose paper"
            elif wind_speed < 10.8:
                wind_status = "Fresh breeze - Small trees sway, wind felt strongly"
            else:
                wind_status = "Strong wind - Trees move noticeably, walking against wind is difficult"


        else:
            temp = feels_like = temp_max = temp_min = cloud_status = humidity = wind_status = description = "NO DATA"

    except Exception as e:
        print(f"Error fetching weather data: {e}")
        temp = feels_like = temp_max = temp_min = cloud_status = humidity = wind_status = description = "ERROR"
    
    
    try:
        prompt = f"I am {gender}. I live in {city} and would like to wear clothes in a {style} style. Could you please suggest an outfit and recommendations that would suit me?"

        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "user", "content": prompt}
            ],
            max_tokens=300,
            temperature=0.7,
        )

        gpt_reply = response.choices[0].message.content
        
    except Exception as e:
        traceback.print_exc()  # 전체 에러 로그 보기
        print(f"Error fetching GPT response: {e}")
        gpt_reply = f"GPT ERROR: {str(e)}"
        

    return render_template("result.html",
                            city=city,
                            style=style,
                            temp=temp,
                            feels_like=feels_like,
                            temp_max=temp_max,
                            temp_min=temp_min,
                            cloud_status=cloud_status,
                            humidity=humidity,
                            wind_status=wind_status,
                            description=description,
                            gpt_reply=gpt_reply)


@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))

if __name__ == "__main__":
    app.run(debug=True, port = 8080)