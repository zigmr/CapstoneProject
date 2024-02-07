from flask import Flask, render_template, request
from os.path import exists
import sqlite3

# Startup functions

app = Flask(__name__)

@app.get("/")
def get_login_page():
    return render_template('login_page.html')

@app.post("/")
def login_user():
    print(request.form)
    return render_template('login_page.html')
