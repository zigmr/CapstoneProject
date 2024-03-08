from flask import Flask, render_template, request

# Startup functions / --------------------

app = Flask(__name__)

from db_models import *     # Imports objects from the database *after* they have been added to the database

# documentation info ---------------

@app.route("/", methods=["GET"])

def get_login_page():
    return render_template('login_page.html')

# Route to handle form submission for login
@app.route("/", methods=["POST"])

def login_user():
    # Use forms to get username and pasword
    username = request.form.get('username')
    password = request.form.get('password')
    
    # Query the database to find matching username and password
    valid_credential = UserCredential.query.filter_by(Username=username, Password=password).first()
    
    if valid_credential:
        print(f"Logged in user {username}. Full name: {valid_credential.employee.FirstName} {valid_credential.employee.LastName}")
        return render_template('Manager_UI.html' if valid_credential.employee.FirstName == "Manager" else 'Cashier_UI.html', username=username, menu_contents=get_menu_items())
    else:
        return "<h1>Your username or password was incorrect.</h1>"


@app.route("/menu")
def display_menu_page():
    menu_contents = get_menu_items()
    return render_template('menu_listing.html', menu_contents=menu_contents)
