from flask import Flask, render_template, redirect, request

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
        if valid_credential.EmployeeRole == "manager":
            return redirect(url_for('manager_home', full_name=str(valid_credential.employee)))
        else:
            return redirect(url_for('cashier_menu', full_name=str(valid_credential.employee)))
    else:
        return "<h1>Your username or password was incorrect.</h1>"
    

# Landing page for managers
@app.route('/manager/home/<full_name>', methods=["GET"])
def manager_home(full_name):
    return render_template('Manager_UI.html',
                           full_name=full_name)

# Landing page for cashiers
@app.route("/cashier/home/<full_name>", methods=["GET"])
def cashier_menu(full_name):
    return render_template('Cashier_UI.html',
                           fullname=full_name,
                           menu_contents=get_menu_items())
