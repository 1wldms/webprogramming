from flask import Flask, render_template, request, redirect, url_for, session

app = Flask(__name__)
app.secret_key = "wekfjl`klkAWldI109nAKnooionrg923jnn"

@app.route('/')
def index():
    ifLogin = False
    if 'username' in session:
        isLogin = True
    return render_template('mainpage.html', isLogin = isLogin) 


users = {}

@app.route('/signup', methods = ["GET", "POST"])
def signup():
    if request.method == "POST": 
        username = request.form['username'] 
        
        if username in users:
            return "이미 존재하는 사용자입니다."
        
        users[username] = password
        return redirect(url_for('login'))
    else:
        return render_template('signup.html')


@app.route('/login', methods = ["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form['username']
        password = request.form['pwd']
        
        if username in users and users[username] == password:
            session['username'] = username 
            return redirect(url_for('index'))
        
        return render_template('login.html', error ="아이디 또는 비밀번호가 잘못되었습니다.")
    else:
        return render_template('login.html')


@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

if __name__ == "__main__":
    app.run(debug=True, port = 8080)