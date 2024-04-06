# Capstone Project: Bytebloom Bakery

### The Application
Bytebloom is software which facilitates quick and efficient order processing for bakeries. Its user interface is provided by a Flask web server which interfaces with a local Flask-SQLAlchemy database.

# Running the Application
1. If you have not already installed the required modules, navigate to the project's root directory and install them using `pip install -r requirements.txt`
2. Enter a command line and change your working directory to the folder "bytebloom_flask".
3. Run `flask run`. A server will be hosted on a local address listed in the command line.

# Command Line Tools
Bytebloom contains a number of command line tools which provide useful functionality while the server is not running. **To execute these commands, your working directory must be "bytebloom_flask".**

### Database Commands
|To view the content of bytebloom.db download the "SQLite Viewer" extension.|
|Command|Effect|
|-|-|
|flask db_populate|Fills the database with example data, creating a local database if none is provided.|
|flask db_drop|Removes all tables and their contents from the database. Use with care!

### Utility Commands
|Command|Effect|
|-|-|
|flask menu|Displays the names of all menu items which will be visible in the cashier interface.|
|flask see_order_cost <order id>|Displays the total cost of all items in a specific purchase.|