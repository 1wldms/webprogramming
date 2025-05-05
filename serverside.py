from flask import Flask, render_template, request, redirect, url_for, session

app = Flask(__name__)
app.secret_key = "wekfjl`klkAWldI109nAKnooionrg923jnn"

@app.route('/')
def index():
    return 'Index Page'
