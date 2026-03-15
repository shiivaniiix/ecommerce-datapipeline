from flask import Flask, render_template, request, redirect, session
import pandas as pd
from datetime import datetime
from products import products

app = Flask(__name__)
app.secret_key = "secret_key"

CUSTOMERS_FILE = "data/customers.csv"
ORDERS_FILE = "data/orders.csv"

cart = []

@app.route("/")
def home():
    # Check if user is logged in
    if "user" not in session:
        return redirect("/login")
    return render_template("shop.html", products=products)
'''
@app.route("/signup", methods=["GET","POST"])
def signup():

    if request.method == "POST":

        name = request.form["name"]
        email = request.form["email"]
        password = request.form["password"]

        df = pd.read_csv(CUSTOMERS_FILE)

        customer_id = len(df) + 1

        new_customer = pd.DataFrame([{
            "customer_id": customer_id,
            "name": name,
            "email": email,
            "password": password,
            "signup_date": datetime.now()
        }])

        df = pd.concat([df,new_customer],ignore_index=True)
        df.to_csv(CUSTOMERS_FILE,index=False)

        return redirect("/")
'''
@app.route("/login", methods=["GET", "POST"])
def login():
    # If already logged in, redirect to shop
    if "user" in session:
        return redirect("/")
    
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]
        
        try:
            df = pd.read_csv(CUSTOMERS_FILE)
            
            # Check if email exists and password matches
            user = df[(df["EmailID"] == email) & (df["Password"] == password)]
            
            if not user.empty:
                # Set session variables
                session["user"] = email
                session["customer_id"] = int(user.iloc[0]["CustID"])
                return redirect("/")
            else:
                # Invalid credentials - you could add flash message here
                return render_template("login.html", error="Invalid email or password")
        except Exception as e:
            return render_template("login.html", error="An error occurred. Please try again.")
    
    return render_template("login.html")


@app.route("/signup", methods=["GET","POST"])
def signup():
    # If already logged in, redirect to shop
    if "user" in session:
        return redirect("/")
    
    if request.method == "POST":
        name = request.form["name"]
        email = request.form["email"]
        phone = request.form["phone"]
        address = request.form["address"]
        city = request.form["city"]
        state = request.form["state"]
        country = request.form["country"]
        postal = request.form["postal"]
        password = request.form["password"]

        try:
            df = pd.read_csv(CUSTOMERS_FILE)
            
            # Check if email already exists
            if not df[df["EmailID"] == email].empty:
                return render_template("signup.html", error="Email already registered. Please login.")
            
            cust_id = len(df) + 1

            new_customer = pd.DataFrame([{
                "CustID": cust_id,
                "CustomerName": name,
                "EmailID": email,
                "PhoneNumber": phone,
                "StreetAddress": address,
                "City": city,
                "State": state,
                "Country": country,
                "PostalCode": postal,
                "AccountCreatedAt": datetime.now(),
                "Password": password
            }])

            df = pd.concat([df, new_customer], ignore_index=True)
            df.to_csv(CUSTOMERS_FILE, index=False)
            
            # Automatically log in the user after signup
            session["user"] = email
            session["customer_id"] = cust_id
            
            return redirect("/")
        except Exception as e:
            return render_template("signup.html", error="An error occurred. Please try again.")

    return render_template("signup.html")


@app.route("/add_to_cart/<int:product_id>")
def add_to_cart(product_id):
    # Check if user is logged in
    if "user" not in session:
        return redirect("/login")
    
    for p in products:
        if p["id"] == product_id:
            cart.append(p)

    return redirect("/")


@app.route("/cart")
def view_cart():
    # Check if user is logged in
    if "user" not in session:
        return redirect("/login")
    return render_template("cart.html", cart=cart)

'''
@app.route("/checkout")
def checkout():

    orders = pd.read_csv(ORDERS_FILE)

    for item in cart:

        order_id = len(orders) + 1

        new_order = pd.DataFrame([{
            "order_id": order_id,
            "customer_id": 1,
            "product": item["name"],
            "price": item["price"],
            "order_date": datetime.now()
        }])

        orders = pd.concat([orders,new_order],ignore_index=True)

    orders.to_csv(ORDERS_FILE,index=False)

    cart.clear()

    return "Order Placed Successfully!"
'''
@app.route("/checkout")
def checkout():
    # Check if user is logged in
    if "user" not in session:
        return redirect("/login")
    
    if not cart:
        return redirect("/cart")
    
    orders = pd.read_csv(ORDERS_FILE)

    order_id = len(orders) + 1

    total_amount = sum([item["price"] for item in cart])

    new_order = pd.DataFrame([{
        "OrderID": order_id,
        "CustomerID": session["customer_id"],
        "PlacedAt": datetime.now(),
        "ExpectedDelieveryDate": datetime.now(),
        "TotalAmountPaid": total_amount,
        "Mode_of_Payment": "UPI",
        "Tracking_number": f"TRK{order_id}XYZ",
        "ShippingAmount": 50
    }])

    orders = pd.concat([orders, new_order], ignore_index=True)

    orders.to_csv(ORDERS_FILE, index=False)

    cart.clear()

    return "Order Placed Successfully!"


@app.route("/logout")
def logout():
    session.clear()
    return redirect("/login")


if __name__ == "__main__":
    app.run(debug=True)