import os
import pandas as pd
from flask import Flask, render_template, request, redirect, url_for, session

app = Flask(__name__)
app.secret_key = "freaklife_secret"

# File paths
USER_FILE = "users.xlsx"
ORDER_FILE = "orders.xlsx"

# Ensure Excel files exist
def ensure_excel_file(file_path, columns):
    try:
        if not os.path.exists(file_path) or os.stat(file_path).st_size == 0:
            pd.DataFrame(columns=columns).to_excel(file_path, index=False, engine="openpyxl")
        else:
            pd.read_excel(file_path, engine="openpyxl")  # Check if it's readable
    except Exception:
        pd.DataFrame(columns=columns).to_excel(file_path, index=False, engine="openpyxl")

# Ensure users.xlsx and orders.xlsx exist
ensure_excel_file(USER_FILE, ["First Name", "Last Name", "Email", "Password"])
ensure_excel_file(ORDER_FILE, ["User", "Product", "Price", "Quantity", "Mobile", "Email", "First Name", "Surname", "Pincode", "Address"])

# Product List
PRODUCTS = [
    {"id": 1, "name": "Whey Protein", "price": 4500, "image": "whey.png", "desc": "Premium whey protein for muscle growth."},
    {"id": 2, "name": "Creatine", "price": 1500, "image": "creatine.png", "desc": "Boost strength and endurance."},
    {"id": 3, "name": "CreaPro", "price": 2000, "image": "creapro.png", "desc": "Advanced creatine formula for max power."},
    {"id": 4, "name": "Raw Pre-Workout", "price": 2200, "image": "preworkout.png", "desc": "Explosive energy and focus."},
    {"id": 5, "name": "Smelling Salt", "price": 800, "image": "smelling_salt.png", "desc": "Instant strength boost for heavy lifts."},
    {"id": 6, "name": "Gym Belt", "price": 1800, "image": "gym_belt.png", "desc": "Support your back during heavy lifts."},
    {"id": 7, "name": "Gym Duffle Bag", "price": 1200, "image": "duffle_bag.png", "desc": "Spacious gym bag for all essentials."},
    {"id": 8, "name": "Gym Gloves", "price": 900, "image": "gym_gloves.png", "desc": "Protect your hands while lifting."},
    {"id": 9, "name": "Lifting Straps", "price": 700, "image": "lifting_straps.png", "desc": "Enhance grip strength for heavy lifts."},
    {"id": 10, "name": "Wrist Bands", "price": 600, "image": "wrist_bands.png", "desc": "Provides wrist support during workouts."},
    {"id": 11, "name": "Lifting Shoes", "price": 3500, "image": "lifting_shoes.png", "desc": "Increase stability and performance."}
]

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/products')
def products():
    return render_template('products.html', products=PRODUCTS)

@app.route('/add_to_cart', methods=['POST'])
def add_to_cart():
    if "user" not in session:
        return redirect(url_for('login_page'))

    product_id = int(request.form['product_id'])
    quantity = int(request.form['quantity'])

    product = next((p for p in PRODUCTS if p["id"] == product_id), None)
    
    if product:
        cart = session.get("cart", [])
        
        for item in cart:
            if item["id"] == product_id:
                item["quantity"] += quantity
                break
        else:
            cart.append({"id": product_id, "name": product["name"], "price": product["price"], "quantity": quantity})

        session["cart"] = cart
        session.modified = True

    return redirect(url_for('cart'))

@app.route('/cart')
def cart():
    cart_items = session.get("cart", [])
    total_price = sum(item["price"] * item["quantity"] for item in cart_items)
    return render_template('cart.html', cart_items=cart_items, total_price=total_price)

@app.route('/remove_from_cart/<int:product_id>')
def remove_from_cart(product_id):
    if "cart" in session:
        session["cart"] = [item for item in session["cart"] if item["id"] != product_id]
        session.modified = True
    return redirect(url_for('cart'))

@app.route('/checkout', methods=['GET', 'POST'])
def checkout():
    if request.method == 'POST':
        mobile = request.form['mobile']
        email = request.form['email']
        firstname = request.form['firstname']
        surname = request.form['surname']
        pincode = request.form['pincode']
        address = request.form['address']

        user_email = session.get("user")
        if not user_email:
            return "Error: You must be logged in to place an order."

        cart_items = session.get("cart", [])
        if not cart_items:
            return "Error: Your cart is empty."

        ensure_excel_file(ORDER_FILE, ["User", "Product", "Price", "Quantity", "Mobile", "Email", "First Name", "Surname", "Pincode", "Address"])

        df = pd.read_excel(ORDER_FILE, engine="openpyxl")

        new_orders = pd.DataFrame([
            [user_email, item["name"], item["price"], item["quantity"], mobile, email, firstname, surname, pincode, address]
            for item in cart_items
        ], columns=["User", "Product", "Price", "Quantity", "Mobile", "Email", "First Name", "Surname", "Pincode", "Address"])

        df = pd.concat([df, new_orders], ignore_index=True)
        df.to_excel(ORDER_FILE, index=False, engine="openpyxl")

        session["cart"] = []
        return redirect(url_for('exit_page'))  # ✅ Now redirects correctly

    return render_template('checkout.html')

@app.route('/exit')
def exit_page():
    return render_template('exit.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        firstname = request.form['firstname']
        lastname = request.form['lastname']
        email = request.form['email']
        password = request.form['password']

        df = pd.read_excel(USER_FILE, engine="openpyxl")

        if email in df["Email"].values:
            return "Error: Email already exists."

        new_user = pd.DataFrame([[firstname, lastname, email, password]],
                                columns=["First Name", "Last Name", "Email", "Password"])
        df = pd.concat([df, new_user], ignore_index=True)
        df.to_excel(USER_FILE, index=False, engine="openpyxl")

        return redirect(url_for('login_page'))

    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login_page():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        df = pd.read_excel(USER_FILE, engine="openpyxl")

        user = df[(df['Email'] == email) & (df['Password'] == password)]

        if not user.empty:
            session["user"] = email
            if "cart" not in session:
                session["cart"] = []
            return redirect(url_for('products'))
        else:
            return "Error: Invalid email or password."

    return render_template('login.html')

if __name__ == '__main__':
    app.run(debug=True)
