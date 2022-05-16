from datetime import datetime

from flask import Flask, render_template, flash, redirect, url_for, session, logging, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import desc

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
db = SQLAlchemy(app)

app.secret_key = 'BAD_SECRET_KEY'
RESTURANT_ID = 0
USER_ID = 0
DELIVERY_STATUS = ""

class complaints(db.Model):
    cid = db.Column(db.Integer, primary_key=True)
    restaurant_name = db.Column(db.String(80))
    employee = db.Column(db.String(120))
<<<<<<< HEAD
    userWarnings = db.Column(db.Integer)
    emplnumWarnings = db.Column(db.Integer)
=======
    numWarnings = db.Column(db.Integer)
>>>>>>> adba21b69f4cf4e7f72ee7863036281c4211ff96
    text = db.Column(db.VARCHAR)
    username = db.Column(db.String(120))

class user(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    # username = db.Column(db.String(80))
    email = db.Column(db.String(120))
    name = db.Column(db.String(120))
    password = db.Column(db.String(80))
    address = db.Column(db.String(80))

class restaurant(db.Model):
    rid = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80))
    address = db.Column(db.String(120))
    rating = db.Column(db.Integer)
    category = db.Column(db.String(120))
    img_path = db.Column(db.String(120))

class menu(db.Model):
    rid = db.Column(db.Integer, db.ForeignKey('restaurant.rid'), primary_key=True)
    item_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120))
    price = db.Column(db.Integer)
    category = db.Column(db.String(80))
    db.CheckConstraint('category in ("food", "drink", "dessert")', name='category_check')


@app.before_first_request
def initialize():
    session['account_type'] = "visitor"
    session['cart'] = {}
    session['total'] = 0
    session['session_rid'] = None

def search(search_val):
    # currently just using a simple like filter
    # I added limit of 9 to keep the page short, but it works with no limit
    restaurants = restaurant.query.filter(restaurant.name.like(f"%{search_val}%")).limit(9).all()
    # splits restraunts into chunks of 3
    rest_in_row = 3
    restaurant_by_row = [restaurants[i:i+rest_in_row] for i in range(0, len(restaurants), rest_in_row)]
    return render_template("search.html", restaurants=restaurant_by_row)

@app.route("/")
def index():
    search_val = request.args.get("search_val")

    # searchs based on if the search_val occurs in any restraunt name
    if search_val:
        return search(search_val)
    else: # this leads to regular homepage
        # top 5 restraunts based on rating
        top_5 = restaurant.query.order_by(desc(restaurant.rating)).limit(5).all()
        return render_template("home.html", restaurants=top_5)

def get_cost_info(cart):
    total_cost = 0.0
    for itm in cart:
        price = cart[itm][0]
        quant = cart[itm][1]
        total_cost += price * quant

    restraunt_charges = total_cost * 0.10 # 10 %
    delivery_cost = total_cost * 0.05 # 5 %

    to_pay = "$" + str(sum((total_cost, delivery_cost, restraunt_charges)))
    total_cost = "$" + str(total_cost)
    restraunt_charges = "$" + str(restraunt_charges)
    delivery_cost = "$" + str(delivery_cost)

    return total_cost, restraunt_charges, delivery_cost, to_pay

@app.route("/_update_cart", methods=["GET", "POST"])
def update_cart():
    cart = session['cart']
    item_added_id_str = request.args.get("item_clicked_id")

    if item_added_id_str:
        clicked_by = request.args.get("clicked_by")
        item = menu.query.filter_by(item_id=int(item_added_id_str)).first()

        if clicked_by == "add":
            if item_added_id_str in cart.keys():
                cart.pop(item_added_id_str)
            else:
                cart[item_added_id_str] = [item.price, 1]
        elif clicked_by == "minus":
            if cart[item_added_id_str][1] == 1:
                cart.pop(item_added_id_str)
            else:
                cart[item_added_id_str][1] -= 1
        elif clicked_by == "plus":
            cart[item_added_id_str][1] += 1

    session['cart'] = cart
    total_cost, restraunt_charges, delivery_cost, to_pay = get_cost_info(cart)

    print(session['cart'])

    return jsonify(cart=session['cart'],
                   cart_len=len(session['cart']),
                   total_cost=total_cost,
                   restraunt_charges=restraunt_charges,
                   delivery_cost=delivery_cost,
                   to_pay=to_pay)


def row_to_dict(row):
    row_dict = row.__dict__
    row_dict.pop("_sa_instance_state")
    return row_dict

def table_to_lst(table):
    table_lst = []
    for row in table:
        table_lst.append(row_to_dict(row))
    return table_lst

@app.route("/manager.html")
def manager_page():
    return render_template("manager.html")
    # return render_template("manager.html", table = table)


@app.route("/complaints.html", methods=['POST','GET'])
def complaints_page():
    if request.method == "POST":
        uname = request.form['uname']
        rest = request.form['rest']
        employee = request.form['employee']
        complaint = request.form['complaint']
<<<<<<< HEAD
        query = complaints.query.order_by(complaints.cid.desc()).all()
        emplwarnings = 0
        if employee :
            for data in query :
                if data.employee  == employee :
                    emplwarnings = data.emplnumWarnings
            emplwarnings += 1

        register = complaints(username=uname, restaurant_name=rest,
                              employee=employee, text=complaint,
                              emplnumWarnings=emplwarnings)
=======

        register = complaints(username=uname, restaurant_name=rest, employee=employee, text=complaint)
>>>>>>> adba21b69f4cf4e7f72ee7863036281c4211ff96
        db.session.add(register)
        db.session.commit()
        return render_template("home.html")
    else:
        return render_template("complaints.html")


@app.route("/restaurant.html")
def restaurant_page():
    current_rid = request.args.get("rid")
    if current_rid:
        current_rid = int(current_rid)
    else:
        pass # error page

    # WIP: was trying to make the carts stay after refreshing restraunt page
    if True: #session['session_rid'] != current_rid:
        session['cart'] = {}
        session['total'] = 0
        session['session_rid'] = current_rid

    #Global rid, used for api calls to the delivery person
    global RESTURANT_ID, DELIVERY_STATUS
    RESTURANT_ID = current_rid
    DELIVERY_STATUS = f"{restaurant.query.get(RESTURANT_ID).name} Has Received The Order!"

    session['restaurant_info'] = row_to_dict(restaurant.query.filter_by(rid=current_rid).first())

    foods = menu.query.filter_by(rid=current_rid, category="food").all()
    drinks = menu.query.filter_by(rid=current_rid, category="drink").all()
    desserts = menu.query.filter_by(rid=current_rid, category="dessert").all()
    session['categories'] = [("Food", table_to_lst(foods)), ("Drinks", table_to_lst(drinks)), ("Desserts", table_to_lst(desserts))]

    return render_template("restaurant.html", restaurant_info=session['restaurant_info'],
                                              categories=session['categories'] )
@app.route("/checkout.html")
def checkout():
    update_cart()
    return render_template("checkout.html", restaurant_info=session['restaurant_info'],
                                            categories=session['categories'])

@app.route("/successful.html")
def successful():
    return render_template("successful.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        uname = request.form["uname"]
        passw = request.form["passw"]

        login = user.query.filter_by(email=uname, password=passw).first()
        if login is not None:
            global USER_ID
            USER_ID = login.id
            return redirect(url_for('index')) # goes to home page / and url also changes
    return render_template("login.html")


@app.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method == "POST":
        name = request.form['name']
        email = request.form['uname']
        passw = request.form['passw']
        address = request.form['address']

        register = user(name=name, email=email, password=passw,address=address)
        db.session.add(register)
        db.session.commit()
        return render_template("login.html")
    return render_template("signup.html")


@app.route("/order")
def order_status():
    global DELIVERY_STATUS
<<<<<<< HEAD
    return render_template('my_order.html',status=DELIVERY_STATUS,day=delivery_time)

@app.route("/dasher",methods=["GET","POST"])
def dasher():
    global RESTURANT_ID,USER_ID, DELIVERY_STATUS, delivery_time
=======
    return render_template('my_order.html',status=DELIVERY_STATUS)

@app.route("/dasher",methods=["GET","POST"])
def dasher():
    global RESTURANT_ID,USER_ID, DELIVERY_STATUS
>>>>>>> adba21b69f4cf4e7f72ee7863036281c4211ff96
    if request.method == "GET" :

        # USER_ID = 1
        # RESTURANT_ID = 1
        user_data = user.query.get(USER_ID)
        restaurant_data = restaurant.query.get(RESTURANT_ID)
        from_address = restaurant_data.address
        resturant_name = restaurant_data.name
        to_address = user_data.address
        to_name = user_data.name
        data = {
            "Order For"  : f"{to_name}",
            "Resturant Name" : f"{resturant_name}",
            "Resturant Address" : f"{from_address}",
            "Delivery Address" : f"{to_address}",
        }

        DELIVERY_STATUS = "Your Delivery Person Is On their Way with your order."
        return jsonify(data)

    elif request.method == "POST":
        DELIVERY_STATUS = "Delivered"
        return jsonify("Success")




if __name__ == "__main__":
    db.create_all()
<<<<<<< HEAD
    # app.run(debug=True, port=8081)
    app.run(host="0.0.0.0")
=======
    app.run(debug=True, port=8081)
    #app.run(host="0.0.0.0")
>>>>>>> adba21b69f4cf4e7f72ee7863036281c4211ff96
