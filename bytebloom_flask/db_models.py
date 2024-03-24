from flask import url_for
from flask_sqlalchemy import SQLAlchemy
import datetime

from app import app

# Database Information/classes --------

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///bytebloom.db'
db = SQLAlchemy(app)

app.config['UPLOAD_FOLDER'] = './images/menu_foods'

    # create database tables if they do not exist
def initialize_database():
    """Creates database tables if they do not exist."""
    with app.app_context():
        db.create_all()

# Global Constants ----------
EMPLOYEE_ROLES = ["cashier", "manager"]

# Employee information classes --------

class Employee(db.Model):
    """Data representing one employee.
    
    Keyword arguments:
    - EmployeeID (int): autogenerated numeric ID representing one user.
    - FirstName (str)
    - LastName (str)
    - Email (str)

    Related tables:
    - UserCredential: login information
    """

    __tablename__ = 'Employees'

    EmployeeID = db.Column(db.Integer, primary_key=True)
    FirstName = db.Column(db.String(50))
    LastName = db.Column(db.String(50))
    Email = db.Column(db.String(100))
    credential = db.relationship("UserCredential", back_populates="employee")

    def __repr__(self):
        return f"{self.FirstName} {self.LastName}"

    def __str__(self):
        return f"{self.FirstName} {self.LastName}"    

class UserCredential(db.Model):
    """Data representing one user's login information.
    
    Keyword arguments:
    - CredentialID (int): optional numeric ID. Autogenerated
    - Username (str)
    - Password (str)
    - Role (str): the job the employee holds. Defines access permissions
    - employee (Employee): the Employee that this credential is associated with.

    Related tables:
    - Employee: user which uses this credential
    """

    __tablename__ = 'UserCredentials'
    CredentialID = db.Column(db.Integer, primary_key=True)
    Username = db.Column(db.String(50), unique=True, nullable=False)
    Password = db.Column(db.String(50), nullable=False)
    EmployeeID = db.Column(db.Integer, db.ForeignKey('Employees.EmployeeID'))
    EmployeeRole = db.Column(db.String(50), nullable=False)
    employee = db.relationship("Employee", back_populates="credential")

    @db.validates('EmployeeRole')
    def validate_role(self, key, value):
        if value not in EMPLOYEE_ROLES:
            raise ValueError("Employee role is not a valid category")
        return value

# Menu Classes

class MenuItem(db.Model):
    """Data representing a type of product as it is displayed on the menu.
    
    Keyword arguments:
    - mid (int): optional numeric ID. Autogenerated.
    - name (str): the name of the product, as displayed to the user.
    - price (float): the price of one unit of product.
    - image_path(str): the name of the image associated with the menu item. Does not include folder names.
        - When constructing a MenuItem, save the image used in image_path in the folder /bytebloom/static/images/menu_foods
    - visible (bool): whether or not the item is currently available on the menu. Defaults to True.
    
    Methods:
    - get_image_path(): Returns a string containing the location of the image for use in HTML files.
    """

    __tablename__ = "MenuItems"

    mid = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    price = db.Column(db.Float)
    image_path = db.Column(db.String)
    visible = db.Column(db.Boolean, default=True)

    current_stock = db.relationship("MenuItemInfo", back_populates="menu_item")

    def __repr__(self):

        return f"({self.mid}) {self.name}"
    
    def get_image_path(self):
        """Returns a string containing the location of the image for use in HTML files."""
        return url_for('static', filename=app.config['UPLOAD_FOLDER'] + "/" + self.image_path)
    
def get_menu_items():
    """Returns a list of MenuItems which are currently on the menu."""
    return MenuItem.query.filter_by(visible=True)

def get_removed_menu_items():
    """Returns a list of MenuItems which are currently not on the menu."""
    return MenuItem.query.filter_by(visible=False)
    
class MenuItemInfo(db.Model):
    """Data representing a shipment of a single type of product.
    
    - id (int): numeric shipment ID. Autogenerated
    - mid (int): ID of the MenuItem describing a food listed in the menu
    - quantity (int): the number of items from the shipment which have not been sold.
    - expiration_date (datetime.DateTime): the date on which the shipment's remaining items expire. 
    """

    __tablename__ = "MenuIteminfo"
    id = db.Column(db.Integer, primary_key=True)
    mid = db.Column(db.Integer, db.ForeignKey('MenuItems.mid'))
    quantity = db.Column(db.Integer, nullable=False)
    expiration_date = db.Column(db.Date, nullable=False)

    menu_item = db.relationship("MenuItem", back_populates="current_stock")

# Command line Tools --------

# Drop all tables from the database.
@app.cli.command('db_drop')
def drop_all():
    """CLI tool to drop all tables for testing. Run with \"flask db_drop\""""
    db.drop_all()

# Add test users to the database
# TODO: replace with proper test suite 
@app.cli.command("db_populate")
def populate_users():
    """CLI tool to populate table with test data. Run with \"flask db_populate\""""
    test_manager = Employee(FirstName="Zineb", LastName="Gamra", Email="test@test.org")
    test_manager_credentials = UserCredential(Username="ZinebGamra", Password="foo", EmployeeRole="manager", employee=test_manager)
    test_cashier = Employee(FirstName="Nya", LastName="James", Email="test@test.org")
    test_cashier_credentials = UserCredential(Username="NyaJames", Password="bar", EmployeeRole="cashier", employee=test_cashier)
    test_cashier_2 = Employee(FirstName="Robert", LastName="Angodung", Email="test@test.org")
    test_cashier_2_credentials = UserCredential(Username="RobertAng", Password="baz", EmployeeRole="cashier", employee=test_cashier_2)

    bread = MenuItem(name='Bread (1 loaf)', price=2.99, image_path='bread.jpg')
    baguette = MenuItem(name='baguette', price=2.99, image_path='baguette.jpg')
    cupcake = MenuItem(name='cupcake', price=2.99, image_path='cupcake.jpg')
    cookie = MenuItem(name='cookie', price=2.99, image_path='cookie.jpg')
    croissant = MenuItem(name='croissant', price=2.99, image_path='croissant.jpg')
    bagel = MenuItem(name='bagel', price=2.99, image_path='bagel.jpg')
    doughnut = MenuItem(name='doughnut', price=2.99, image_path='doughnut.jpg')
    pretzel = MenuItem(name='pretzel', price=2.99, image_path='pretzel.jpg')
    pound_cake = MenuItem(name='pound cake', price=2.99, image_path='poundcake.jpg')
    brioche = MenuItem(name='brioche', price=2.99, image_path='brioche.jpg', visible=False)
    banana_bread = MenuItem(name='banana bread', price=2.99, image_path='bananabread.jpg', visible=False)
    macaroon = MenuItem(name='macaroon', price=2.99, image_path='macaroon.jpg')
    white_bread = MenuItem(name='white bread', price=2.99, image_path='whitebread.jpg')

    bread.current_stock.append(MenuItemInfo(quantity=500, expiration_date=datetime.date(2024, 12, 31)))
    baguette.current_stock.append(MenuItemInfo(quantity=500, expiration_date=datetime.date(2024, 12, 31)))
    cupcake.current_stock.append(MenuItemInfo(quantity=500, expiration_date=datetime.date(2024, 12, 31)))
    cookie.current_stock.append(MenuItemInfo(quantity=500, expiration_date=datetime.date(2024, 12, 31)))
    croissant.current_stock.append(MenuItemInfo(quantity=500, expiration_date=datetime.date(2024, 12, 31)))
    bagel.current_stock.append(MenuItemInfo(quantity=500, expiration_date=datetime.date(2024, 12, 31)))
    doughnut.current_stock.append(MenuItemInfo(quantity=500, expiration_date=datetime.date(2024, 12, 31)))
    pretzel.current_stock.append(MenuItemInfo(quantity=500, expiration_date=datetime.date(2024, 12, 31)))
    pound_cake.current_stock.append(MenuItemInfo( quantity=500, expiration_date=datetime.date(2024, 12, 31)))
    brioche.current_stock.append(MenuItemInfo(quantity=500, expiration_date=datetime.date(2024, 12, 31)))
    banana_bread.current_stock.append(MenuItemInfo(quantity=500, expiration_date=datetime.date(2024, 12, 31)))
    macaroon.current_stock.append(MenuItemInfo(quantity=500, expiration_date=datetime.date(2024, 12, 31)))
    white_bread.current_stock.append(MenuItemInfo(quantity=500, expiration_date=datetime.date(2024, 12, 31)))
    bread.current_stock.append(MenuItemInfo(quantity=250, expiration_date=datetime.date(2025, 1, 31)))

    db.session.add(test_manager)
    db.session.add(test_manager_credentials)
    db.session.add(test_cashier)
    db.session.add(test_cashier_credentials)
    db.session.add(test_cashier_2)
    db.session.add(test_cashier_2_credentials)
    db.session.add(bread)
    db.session.add(baguette)
    db.session.add(cookie)
    db.session.add(croissant)
    db.session.add(bagel)
    db.session.add(doughnut)
    db.session.add(pretzel)
    db.session.add(pound_cake)
    db.session.add(brioche)
    db.session.add(banana_bread)
    db.session.add(macaroon)
    db.session.add(white_bread)

    db.session.commit()

@app.cli.command("menu")
def print_menu():
    for item in get_menu_items():
        print(item.name)

# Startup --------
initialize_database()   # call the initialize_database function and pull up login
