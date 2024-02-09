from flask import Flask, render_template, request
from dotenv import dotenv_values

# Startup functions
app = Flask(__name__)
secrets = dotenv_values()

@app.get("/")
def get_login_page():
    return render_template('login_page.html')

@app.post("/")
def login_user():
    print(request.form)
    username = request.form['username']
    password = request.form['password']
    if username == secrets['ADMIN_USERNAME'] and password == secrets['ADMIN_PASSWORD']:
        return f"<h1>Welcome, {username}.<h1><p>Logged in as ADMIN</p>"
    elif username == secrets['CASHIER_USERNAME'] and password == secrets['CASHIER_PASSWORD']:
        return f"<h1>Welcome, {username}.<h1><p>Logged in as CASHIER</p>"
    else:
        return "<h1>Your username or password was incorrect.</h1>"
