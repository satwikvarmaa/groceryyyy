import sqlite3
from flask import  , render_template, request, jsonify
import threading

app = Flask(__name__)
DATABASE = 'grocery.db'
lock = threading.Lock()

# Function to get a thread-local SQLite connection
def get_db():
    db = getattr(threading.current_thread(), '_database', None)
    if db is None:
        db = sqlite3.connect(DATABASE)
        setattr(threading.current_thread(), '_database', db)
    return db

# Function to close the thread-local SQLite connection
@app.teardown_appcontext
def close_connection(exception):
    db = getattr(threading.current_thread(), '_database', None)
    if db is not None:
        db.close()

# Create the table if it doesn't exist
def create_table():
    with lock:
        db = get_db()
        c = db.cursor()
        c.execute("CREATE TABLE IF NOT EXISTS items (id INTEGER PRIMARY KEY AUTOINCREMENT, item TEXT, price REAL)")
        db.commit()

# Route to retrieve the grocery items
@app.route("/get_items")
def get_items():
    with lock:
        db = get_db()
        c = db.cursor()
        c.execute("SELECT * FROM items")
        items = c.fetchall()
        print(items)
        return jsonify(items)

# Route to add an item
@app.route("/add_item", methods=["POST"])
def add_item():
    item = request.form["item"]
    price = float(request.form["price"])
    quantity = int(request.form["quantity"])
    with lock:
        db = get_db()
        c = db.cursor()
        c.execute("INSERT INTO items (item, price, quantity) VALUES (?, ?, ?)", (item, price, quantity))
        db.commit()
    return "Item added successfully!"

# Main route to render the HTML template
@app.route("/")
def index():
    create_table()
    return render_template("index.html")

if __name__ == "__main__":
    app.run()
