
from flask import Flask, render_template, request, redirect, session
import pandas as pd
from datetime import datetime
from products import products
import boto3
import os
from dotenv import load_dotenv

timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

filename = f"orders/orders_{timestamp}.csv"

load_dotenv()

app = Flask(__name__)
app.secret_key = "secret_key"

CUSTOMERS_FILE = "data/customers.csv"
ORDERS_FILE = "data/orders.csv"

cart = []

# AWS CONFIG
BUCKET_NAME = os.getenv("AWS_BUCKET_NAME")
AWS_ACCESS_KEY = os.getenv("AWS_ACCESS_KEY")
AWS_SECRET_KEY = os.getenv("AWS_SECRET_KEY")

s3 = boto3.client(
    "s3",
    aws_access_key_id=AWS_ACCESS_KEY,
    aws_secret_access_key=AWS_SECRET_KEY
)


# ---------- S3 UPLOAD FUNCTION ----------

def upload_to_s3():
    try:
        s3.upload_file(
            CUSTOMERS_FILE,
            BUCKET_NAME,
            "customers/customers.csv"
        )

        s3.upload_file(
            ORDERS_FILE,
            BUCKET_NAME,
            filename
        )

        print("Files uploaded to S3 successfully")

    except Exception as e:
        print("S3 upload failed:", e)


# ---------- HOME ----------

@app.route("/")
def home():

    if "user" not in session:
        return redirect("/login")

    return render_template("shop.html", products=products)


# ---------- LOGIN ----------

@app.route("/login", methods=["GET", "POST"])
def login():

    if "user" in session:
        return redirect("/")

    if request.method == "POST":

        email = request.form["email"]
        password = request.form["password"]

        df = pd.read_csv(CUSTOMERS_FILE)

        user = df[(df["EmailID"] == email) & (df["Password"] == password)]

        if not user.empty:

            session["user"] = email
            session["customer_id"] = int(user.iloc[0]["CustID"])

            return redirect("/")

        return render_template("login.html", error="Invalid email or password")

    return render_template("login.html")


# ---------- SIGNUP ----------

@app.route("/signup", methods=["GET", "POST"])
def signup():

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

        df = pd.read_csv(CUSTOMERS_FILE)

        if not df[df["EmailID"] == email].empty:
            return render_template("signup.html", error="Email already registered")

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

        # upload updated customers.csv to S3
        upload_to_s3()

        session["user"] = email
        session["customer_id"] = cust_id

        return redirect("/")

    return render_template("signup.html")


# ---------- ADD TO CART ----------

@app.route("/add_to_cart/<int:product_id>")
def add_to_cart(product_id):

    if "user" not in session:
        return redirect("/login")

    for p in products:
        if p["id"] == product_id:
            cart.append(p)

    return redirect("/")


# ---------- CART ----------

@app.route("/cart")
def view_cart():

    if "user" not in session:
        return redirect("/login")

    total = sum([item["price"] for item in cart])

    return render_template("cart.html", cart=cart, total=total)


# ---------- CHECKOUT ----------

@app.route("/checkout")
def checkout():

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

    # upload updated CSVs to S3
    upload_to_s3()

    cart.clear()

    return "Order Placed Successfully!"


# ---------- LOGOUT ----------

@app.route("/logout")
def logout():

    session.clear()

    return redirect("/login")


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)