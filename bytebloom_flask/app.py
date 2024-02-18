from flask import Flask, render_template, request
from dotenv import dotenv_values

# database ------------------------------

from flask_sqlalchemy import SQLAlchemy

# Startup functions / --------------------

app = Flask(__name__)
secrets = dotenv_values()
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///bytebloom.db'

# Database Information/classes --------

db = SQLAlchemy(app)

class Employee(db.Model):

    __tablename__ = 'Employees'

    EmployeeID = db.Column(db.Integer, primary_key=True)
    FirstName = db.Column(db.String(50))
    LastName = db.Column(db.String(50))
    Email = db.Column(db.String(100))



class MenuItem(db.Model):
    __tablename__ = 'MenuItems'

    MenuItemID = db.Column(db.Integer, primary_key=True)
    Name = db.Column(db.String(255), nullable=False)
    ExpirationDate = db.Column(db.Date)
    Pricing = db.Column(db.Numeric(10, 2))
    Quantity = db.Column(db.Integer)
    EmployeeID = db.Column(db.Integer, db.ForeignKey('Employees.EmployeeID'))  

    employee = db.relationship("Employee")

class UserCredential(db.Model):

    __tablename__ = 'UserCredentials'
    CredentialID = db.Column(db.Integer, primary_key=True)
    Username = db.Column(db.String(50), unique=True, nullable=False)
    Password = db.Column(db.String(50), nullable=False)
    EmployeeID = db.Column(db.Integer, db.ForeignKey('Employees.EmployeeID'))
    employee = db.relationship("Employee", back_populates="credentials")

# documentation info ---------------
    # create database tables if they do not exist
def initialize_database():  
    with app.app_context():
        db.create_all()

# call the initialize_database function and pull up login
        
initialize_database()

@app.route("/", methods=["GET"])

def get_login_page():
    return render_template('login_page.html')

# use forms to get username and pasword

@app.route("/", methods=["POST"])
def login_user():
    username = request.form.get('username')
    password = request.form.het('password')

# query to find matching user/pw in database
    
    user = UserCredential.query.filter_by(username=username, Password=password).first()

    if user:
        return render_template('Manager_UI.html' if user.employee.FirstName == "Zineb" else 'Cashier_UI.html', username=username)

# App Functions --------------------  

# @app.get("/")
# def get_login_page():
    # return render_template('login_page.html')

# @app.post("/")
#def login_user():
##    username = request.form['username']
#    password = request.form['password']
#    if username == secrets['ADMIN_USERNAME'] and password == secrets['ADMIN_PASSWORD']:
#        return render_template('Manager_UI.html', username = username)
#    elif username == secrets['CASHIER_USERNAME'] and password == secrets['CASHIER_PASSWORD']:
#        return render_template('Cashier_UI.html', username = username)
#    else:
#        return "<h1>Your username or password was incorrect.</h1>"

#----------------------------------

# Route to handle form submission for login
@app.route("/", methods=["POST"])

def login_user():
    username = request.form.get('username')
    password = request.form.get('password')
    
    # Query the database to find matching username and password
    user = UserCredential.query.filter_by(Username=username, Password=password).first()
    
    if user:
        return render_template('Manager_UI.html' if user.employee.FirstName == "Manager" else 'Cashier_UI.html', username=username)
    else:
        return "<h1>Your username or password was incorrect.</h1>"