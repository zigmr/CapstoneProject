from flask import Flask, flash, jsonify, redirect, render_template, request, session
from werkzeug.utils import secure_filename
import json, os.path, random, datetime

# Startup functions / --------------------

app = Flask(__name__)
app.secret_key = '156da9a0758ed359ef8a6015c1bead42744758c8b4d629d50dfa18737bd647ad'

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webm'}

from db_models import *     # Imports objects from the database *after* they have been added to the database

# documentation info ---------------

@app.route("/", methods=["GET"])

def get_login_page():
    food_image_paths = []
    vertical_positions = []
    horizontal_positions = []
    for item in sorted(get_menu_items(), key=lambda x: random.random()):
        food_image_paths.append(item.get_image_path())
        vertical_positions.append(random.random() * 100)
        horizontal_positions.append(random.random() * 100)
    return render_template('login_page.jinja',
                           food_image_paths=food_image_paths,
                           vertical_positions=vertical_positions,
                           horizontal_positions=horizontal_positions)


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
        session['employee_id'] = valid_credential.EmployeeID
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
        return redirect(url_for('get_login_page'))


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

# Returns JSON containing all objects currently in the menu
@app.route('/current-menu-items', methods=["GET"])
def current_menu_items():
    current_items = []

    for item in get_menu_items():
        item_to_add = {"id": item.mid,
                       "name": item.name,
                       "price": item.price,
                       "imageSource": item.get_image_path()}
        current_items.append(item_to_add)
    
    return jsonify(current_items)

# Returns JSON containing all objects currently removed from the menu
@app.route('/removed-menu-items', methods=['GET'])
def removed_menu_items():
    removed_items = []

    for item in get_removed_menu_items():
        item_to_add = {"id": item.mid,
                       "name": item.name,
                       "price": item.price,
                       "imageSource": item.get_image_path()}
        removed_items.append(item_to_add)
    
    return jsonify(removed_items)

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
    return render_template('Manager_UI.jinja',
                           first_name = session['first_name'],
                           last_name = session['last_name'])

# UI for changing the menu
@app.route('/manager/alter-menu', methods=["GET"])
def manager_menu_control():
    # Check that the user is a manager
    result = validate_user_type(['manager'])
    if result is not True:
        return result
    
    # If the user is a manager, show the page.
    return render_template('manager_menu_control.jinja',
                           first_name = session['first_name'],
                           last_name = session['last_name'],
                           current_menu_items = get_menu_items(),
                           removed_menu_items = get_removed_menu_items())

# Validates and saves changes to the menu
@app.route('/manager/alter-menu', methods=["POST"])
def manager_post_menu_changes():
    newItems = json.loads(request.form.get("newItems"))
    reinstatedItems = json.loads(request.form.get("reinstatedItems"))
    removedItems = json.loads(request.form.get("removedItems"))

    # If there are new items, store them in the database and their images in the appropriate folder.
    if 'newElemImage' in request.files:
        uploaded_files = request.files.getlist('newElemImage')

        assembledNewItems = zip(newItems, uploaded_files)
        for newItemData in assembledNewItems:
            name = newItemData[0]['name']
            price = newItemData[0]['price']
            new_image = newItemData[1]
            new_image_name = secure_filename(new_image.filename)
            new_image_loc = os.path.join('static', app.config['UPLOAD_FOLDER'], new_image_name)

            new_image.save(new_image_loc)
            new_menu_item = MenuItem(name=name, price=price, image_path=new_image_name)
            db.session.add(new_menu_item)

    # Update each item that's been returned to the menu
    for item in reinstatedItems:
        item_db_version = MenuItem.query.filter_by(mid=item['id']).first()

        item_db_version.name = item['name']
        item_db_version.price = item['price']
        if item['imageSource'] != item_db_version.get_image_path():
            newPath = item['imageSource'].replace('static/' + app.config['UPLOAD_FOLDER'] + "/", "")
            item_db_version.image_path = newPath

        item_db_version.visible = True
    
    # Update each item that's been removed from the menu
    for item in removedItems:
        item_db_version = MenuItem.query.filter_by(mid=item['id']).first()

        item_db_version.name = item['name']
        item_db_version.price = item['price']
        if item['imageSource'] != item_db_version.get_image_path():
            newPath = item['imageSource'].replace('static/' + app.config['UPLOAD_FOLDER'] + "/", "")
            item_db_version.image_path = newPath
        
        item_db_version.visible = False

    # Save the changes
    db.session.commit()

    return jsonify({"changes_complete": True})

# Display inventory control screen
@app.route('/manager/inventory')
def manager_inventory_screen():
    # Determine that the user is a manager
    result = validate_user_type(['manager'])
    if result is not True:
        return result
    
    # Convert the menu items into a JSON object
    db_menu_items = MenuItem.query.all()
    dict_menu_items = {}
    for item in db_menu_items:
        dict_menu_items[item.name] = item.get_image_path()
    
    # Show the page
    return render_template('manager_inventory.jinja',
                           first_name = session['first_name'],
                           last_name = session['last_name'],
                           all_menu_items = json.dumps(dict_menu_items),
                           inventory_stock = MenuItemInfo.query.where(MenuItemInfo.quantity > 0).order_by(MenuItemInfo.expiration_date).all(),
                           current_time = datetime.datetime.date(datetime.datetime.now()))

# Command to clear all items from inventory
@app.route("/manager/clear-expired", methods=["POST"])
def clear_expired_items():
    return jsonify({"changes_complete": False})

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
    return render_template('Cashier_UI.jinja',
                           first_name = session['first_name'],
                           last_name = session['last_name'],
                           menu_contents=get_menu_items())

# Processes orders placed by cashiers
@app.route("/cashier/send_order", methods=["POST"])
def recieve_order():
    # Validate that the person sending the order is a cashier
    result = validate_user_type(['cashier'])
    if result is not True:
        return result

    purchase_time = datetime.datetime.now()
    cashier_id = session['employee_id']
    sent_json = request.json
    card_number = sent_json['card_number'].replace(" ", "")
    promo_code = sent_json['promo_code']
    cart_items = sent_json['cart_items']

    # Make sure that necessary data is present
    if len(sent_json) == 0:
        return jsonify({"changes_complete": False, "order_status": "no JSON sent"})
    if len(card_number) == 0:
        return jsonify({"changes_complete": False, "order_status": "no card number sent"})
    if len(cart_items) == 0:
        return jsonify({"changes_complete": False, "order_status": "empty cart"})
    
    # Validate card number
    for card_char in card_number:
        if not card_char.isdigit():
            return jsonify({"changes_complete": False, "order_status": "invalid card number: contains letters"})
    if len(card_number) < 8:
        return jsonify({"changes_complete": False, "order_status": "invalid card number: too short"})
    if len(card_number) > 19:
        return jsonify({"changes_complete": False, "order_status": "invalid card number: too long"})
    
    # Attempt to store the order
    new_order = Order(card_number=card_number, cashier_id=cashier_id, purchase_time = purchase_time)
    if promo_code != "":
        new_order.promo_code_id=promo_code

    for item in cart_items:
        db_menu_item = MenuItem.query.filter_by(name=item['name']).first()
        new_order_item = OrderedItemType(item_type=db_menu_item, order=new_order, count=item['amount'])

        # Deduct the necessary items from stock
        quantity_to_remove = int(item['amount'])
        while quantity_to_remove > 0:
            # Find the soonest-to-expire inventory item that contains the item being sold
            db_oldest_inventory = MenuItemInfo.query.filter_by(mid=db_menu_item.mid).where(MenuItemInfo.quantity > 0).order_by(MenuItemInfo.expiration_date).first()
            if (db_oldest_inventory is None):
                # The order fails. No changes are made to the database and the customer is not charged.
                return jsonify({"changes_complete": False, "order_status": "not enough stock", "insufficient_stock": item['name']})
            
            if quantity_to_remove <= db_oldest_inventory.quantity:
                db_oldest_inventory.quantity -= quantity_to_remove
                quantity_to_remove = 0
            else:
                quantity_to_remove -= db_oldest_inventory.quantity
                db_oldest_inventory.quantity = 0

    db.session.add(new_order)
    db.session.commit()

    return jsonify({"changes_complete": True, "order_status": "fulfilled"})
