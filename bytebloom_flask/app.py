from flask import Flask, render_template, request

# database ------------------------------

from flask_sqlalchemy import SQLAlchemy

# Startup functions / --------------------

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///bytebloom.db'

# Database Information/classes --------

db = SQLAlchemy(app)

class Employee(db.Model):

    __tablename__ = 'Employees'

    EmployeeID = db.Column(db.Integer, primary_key=True)
    FirstName = db.Column(db.String(50))
    LastName = db.Column(db.String(50))
    Email = db.Column(db.String(100))
    credential = db.relationship("UserCredential", back_populates="employee")

# ------------------------------------------------------------
# Model temporarily disabled until employee login is debugged
# ------------------------------------------------------------
# class MenuItem(db.Model):
#     __tablename__ = 'MenuItems'

#     MenuItemID = db.Column(db.Integer, primary_key=True)
#     Name = db.Column(db.String(255), nullable=False)
#     ExpirationDate = db.Column(db.Date)
#     Pricing = db.Column(db.Numeric(10, 2))
#     Quantity = db.Column(db.Integer)
#     EmployeeID = db.Column(db.Integer, db.ForeignKey('Employees.EmployeeID'))  

#     employee = db.relationship("Employee")

class UserCredential(db.Model):

    __tablename__ = 'UserCredentials'
    CredentialID = db.Column(db.Integer, primary_key=True)
    Username = db.Column(db.String(50), unique=True, nullable=False)
    Password = db.Column(db.String(50), nullable=False)
    EmployeeID = db.Column(db.Integer, db.ForeignKey('Employees.EmployeeID'))
    employee = db.relationship("Employee", back_populates="credential")

# documentation info ---------------
    # create database tables if they do not exist
def initialize_database():  
    with app.app_context():
        db.create_all()

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
        return render_template('Manager_UI.html' if valid_credential.employee.FirstName == "Manager" else 'Cashier_UI.html', username=username)
    else:
        return "<h1>Your username or password was incorrect.</h1>"


# CLI tool to drop all tables for testing. Run with "flask db_drop"
# TODO: Delete this
@app.cli.command('db_drop')
def drop_all():
    db.drop_all()

# CLI tool to populate table with test data. Run with "flask db_populate"
@app.cli.command("db_populate")
def populate_users():
    test_manager = Employee(EmployeeID=1, FirstName="Manager", LastName="Gamra", Email="test@test.org")
    test_manager_credentials = UserCredential(Username="Manager", Password="foo", EmployeeID=1)
    test_cashier = Employee(EmployeeID=2, FirstName="Nya", LastName="James", Email="test@test.org")
    test_cashier_credentials = UserCredential(Username="Cashier", Password="bar", EmployeeID=2)

    db.session.add(test_manager)
    db.session.add(test_manager_credentials)
    db.session.add(test_cashier)
    db.session.add(test_cashier_credentials)
    db.session.commit()

# call the initialize_database function and pull up login
initialize_database()