from flask import Flask, flash, redirect, render_template, request, session

# Startup functions / --------------------

app = Flask(__name__)
app.secret_key = '156da9a0758ed359ef8a6015c1bead42744758c8b4d629d50dfa18737bd647ad'

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
        print(f"Logged in user {username}. Full name: {str(valid_credential.employee)}")
        session['username'] = username
        session['user_type'] = valid_credential.EmployeeRole
        session['first_name'] = valid_credential.employee.FirstName
        session['last_name'] = valid_credential.employee.LastName
        print(session)

        if valid_credential.EmployeeRole == "manager":
            return redirect(url_for('manager_home'))
        else:
            return redirect(url_for('cashier_menu'))
    else:
        flash('Invalid username or password.\nCheck your credentials and try again.')
        return render_template('login_page.html')


# ---------------------------------
# Helper Functions
# ---------------------------------

# Logs out the active user and removes their session information.
@app.route("/logout")
def logout():
    session.clear()
    flash("You were successfully logged out.")
    return redirect(url_for('get_login_page'))


# Validates that a user's credentials are sufficient to view a page
def validate_user_type(required_user_types):
    """Determines whether the user's session is of an authorized credential category.
    
    Parameters:
    - required_user_types (list): list containing strings describing permitted user types.
        - The list of user types used by this system are found in db_models.EMPLOYEE_ROLES
    
    Postconditions:
    - If the session does not have a user type associated with it, a flashed message is added to the session. Returns a redirect to the login screen.
    - If the session's user type is not one of the types found in required_user_types, a flashed message is added to the session. Returns a redirect to the login screen.
    - If the session's user type is valid, return True. No redirection occurs.
    """

    if 'user_type' not in session:
        session.clear()
        flash("User credentials were not stored properly. Please contact a system administrator for assistance. You have been logged out.")
        return redirect(url_for('get_login_page'))
    if session['user_type'] not in required_user_types:
        session.clear()
        flash("User is not a valid user type for this page. You have been logged out.")
        return redirect(url_for('get_login_page'))
    return True


# ---------------------------------
# Manager pages
# ---------------------------------

# Landing page for managers
@app.route("/manager/home", methods=["GET"])
def manager_home():
    # Check that the user is a manager
    result = validate_user_type(['manager'])
    if result is not True:
        return result
    
    # If the user is a manager, show the page.
    return render_template('Manager_UI.html',
                           first_name = session['first_name'],
                           last_name = session['last_name'])


# ---------------------------------
# Cashier pages
# ---------------------------------

# Landing page for cashiers
@app.route("/cashier/home", methods=["GET"])
def cashier_menu():
    # Check that the user is a cashier
    result = validate_user_type(['cashier'])
    if result is not True:
        return result

    #If the user is a cashier, show the page.
    return render_template('Cashier_UI.html',
                           first_name = session['first_name'],
                           last_name = session['last_name'],
                           menu_contents=get_menu_items())
