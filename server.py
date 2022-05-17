from datetime import datetime

from flask import Flask, render_template, flash, redirect, url_for, session, logging, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import desc

from werkzeug.security import check_password_hash,generate_password_hash
from flask_login import UserMixin, login_user, LoginManager, login_required, current_user, logout_user

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
db = SQLAlchemy(app)

app.secret_key = 'BAD_SECRET_KEY'
RESTURANT_ID = 0
USER_ID = 0
DELIVERY_STATUS = ""
VIP_DISCOUNT = 0.05
login_manager = LoginManager()
login_manager.init_app(app)

class order_details (db.Model):
    order_id = db.Column(db.Integer, primary_key=True)
    rid = db.Column(db.Integer,db.ForeignKey('restaurant.rid'))
    user_id = db.Column(db.Integer,db.ForeignKey('user.id'))
    delivery_id = db.Column(db.Integer,db.ForeignKey('user.id'))
    total_cost = db.Column(db.String(120))


class employee (db.Model):
    id = db.Column(db.Integer,db.ForeignKey('user.id'), primary_key=True)
    rid= db.Column(db.Integer,db.ForeignKey('restaurant.rid'), primary_key=True)
    salary = db.Column(db.String(120))
    warnings = db.Column(db.String(120))
    category = db.Column(db.String(80))


class complaints(db.Model):
    cid = db.Column(db.Integer, primary_key=True)
    restaurant_name = db.Column(db.String(80))
    employee = db.Column(db.String(120))

    userWarnings = db.Column(db.Integer)
    emplnumWarnings = db.Column(db.Integer)

    numWarnings = db.Column(db.Integer)
    text = db.Column(db.VARCHAR)
    username = db.Column(db.String(120))

class user(UserMixin,db.Model):
    id = db.Column(db.Integer, primary_key=True)
    # username = db.Column(db.String(80))
    email = db.Column(db.String(120))
    name = db.Column(db.String(120))
    # we should have first and last name
    # first_name = db.Column(db.String(120))
    # last_name = db.Column(db.String(120))
    password = db.Column(db.String(80))
    address = db.Column(db.String(80))
    phone_number = db.Column(db.String(80))
    numWarnings = db.Column(db.Integer)
    category = db.Column(db.String(80))



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



@login_manager.user_loader
def load_user(user_id):
    return user.query.get(int(user_id))


@app.before_first_request
def initialize():
    # session['account_type'] = "visitor"
    # keeping it to register_customer so we can work on everything
    session['account_type'] = "visitor"
    session['user_first_name'] = None
    session['cart'] = {}
    session['total'] = 0
    session['session_rid'] = None
    session['is_vip'] = False

@app.context_processor
def base():
    return dict(account_type=session['account_type'],
                user_first_name=session['user_first_name'])

@app.route("/manager.html")
def manager_page():
    table = complaints.query.all()
    return render_template("manager.html", complaints = table)
#approve complaints,  update the warnings, blacklist the user

@app.route("/manager_employees.html")
def manager_employees_page():
    table = complaints.query.all()
    return render_template("manager_employees.html", complaints = table)

@app.route("/manager_users.html")
def manager_users_page():
    table = user.query.all()
    return render_template("manager_users.html", users = table)

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

def format_dollar(dol_int):
    return '${0:.2f}'.format(dol_int)

def get_cost_info(cart):
    global VIP_DISCOUNT
    total_cost = 0.0
    for itm in cart:
        price = cart[itm][0]
        quant = cart[itm][1]
        total_cost += price * quant

    restraunt_charges = total_cost * 0.10 # 10 %
    delivery_cost = total_cost * 0.05 # 5 %


    #add vip discount
    vip_discount = (1-VIP_DISCOUNT) if session['is_vip'] else 1
    to_pay = sum((total_cost, delivery_cost, restraunt_charges)) * vip_discount

    session['total'] = to_pay
    to_pay = format_dollar(to_pay)
    total_cost = format_dollar(total_cost)
    restraunt_charges = format_dollar(restraunt_charges)
    delivery_cost = format_dollar(delivery_cost)

    return total_cost, restraunt_charges, delivery_cost, to_pay


@app.route("/_update_cart", methods=["GET", "POST"])
@login_required
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



@app.route("/complaints.html", methods=['POST','GET'])
def complaints_page():
    if request.method == "POST":
        uname = request.form['uname']
        rest = request.form['rest']
        employee = request.form['employee']
        complaint = request.form['complaint']
# <<<<<<< HEAD
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
# =======
#
#         register = complaints(username=uname, restaurant_name=rest, employee=employee, text=complaint)
# >>>>>>> adba21b69f4cf4e7f72ee7863036281c4211ff96
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

    user_info = user.query.filter_by(id=USER_ID).first()
    if user_info:
        session['is_vip'] = user_info.category == "VIP"

    return render_template("restaurant.html", restaurant_info=session['restaurant_info'],
                                              categories=session['categories'],
                                              VIP_DISCOUNT=VIP_DISCOUNT*100,
                                              is_vip=session['is_vip'])

@app.route("/checkout.html", methods=["GET", "POST"])
@login_required
def checkout():
    if request.method == "POST":
        if "user_address" in request.form:
            user_address = request.form["user_address"]
        elif "pm_card_num" in request.form:
            payment_info = {"pm_card_num" : request.form["pm_card_num"],
                            "pm_date_month" : request.form["pm_date_month"],
                            "pm_cvv" : request.form["pm_cvv"],
                            "pm_name" : request.form["pm_name"]}


    update_cart()
    user_info = user.query.filter_by(id=USER_ID).first()

    return render_template("checkout.html", restaurant_info=session['restaurant_info'],
                                            categories=session['categories'],
                                            user_info=user_info,
                                            VIP_DISCOUNT=VIP_DISCOUNT*100,
                                            is_vip=session['is_vip'])


@app.route("/successful.html")
@login_required
def successful():
    new_order = order_details(rid=int(session['restaurant_info']['rid']),
                             user_id=USER_ID,
                             total_cost=session['total'])

    db.session.add(new_order)
    db.session.commit()
    return render_template("successful.html")


@app.route("/profile.html", methods=["GET", "POST"])
@login_required
def profile():
    user_info = {}
    if request.method == "POST":
        # get from form
        user_info = {"first_name": request.form['user_firstname1'],
                     "last_name": request.form['user_lastname1'],
                     "phone": request.form['user_phoneNumber1'],
                     "email": request.form['user_email1'],
                     "address": request.form['user_address1']}
    else:
        # get from user db
        # dummy values for now
        user_info = {"first_name": "Firstname",
                     "last_name": "Lastname",
                     "phone": "1234567890",
                     "email": "firstlast@email.com",
                     "address": "1111 Queens blvd, NY, 11111"}

    return render_template("profile.html", user_info=user_info)

@app.route("/aboutus.html")
def aboutus():
    return render_template("aboutus.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        uname = request.form["uname"]
        passw = request.form["passw"]
        logged_in_user = user.query.filter_by(email=uname).first()
        if not logged_in_user:
            flash("No Accounts Associated with this email!")
            return redirect(url_for('login'))
        if not check_password_hash(logged_in_user.password,passw):
            flash("Incorrect Password")
            return redirect(url_for('login'))
        login_user(logged_in_user)
        global USER_ID
        USER_ID = logged_in_user.id
        session["account_type"] = "register_customer"
        session["user_first_name"] = logged_in_user.name
        return redirect(url_for('index')) # goes to home page / and url also changes

    return render_template("login.html")


@app.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method == "POST":
        name = request.form['name']
        email = request.form['uname']
        passw = request.form['passw']
        address = request.form['address']
        phone = request.form['num']
        if user.query.filter_by(email=email).first():
            flash("User Already Exists, Log in Now")
            return redirect (url_for('login'))

        hashed_password = generate_password_hash(passw,method='pbkdf2:sha256', salt_length=16)
        new_user = user(name=name, email=email, password=hashed_password,address=address,phone_number=phone)
        db.session.add(new_user)
        db.session.commit()
        login_user(new_user)
        return redirect (url_for('login'))

    return render_template("signup.html")

@app.route("/logout")
def logout():
    # logout_user()
    session['account_type'] = 'visitor'
    session['user_first_name'] = None
    return redirect(url_for('index'))


@app.route("/order")
@login_required
def order_status():
    global DELIVERY_STATUS
# <<<<<<< HEAD
    return render_template('my_order.html',status=DELIVERY_STATUS)


@app.route("/dasher",methods=["GET","POST"])
def dasher():
    global RESTURANT_ID,USER_ID, DELIVERY_STATUS, delivery_time
# =======
#     return render_template('my_order.html',status=DELIVERY_STATUS)
#
# @app.route("/dasher",methods=["GET","POST"])
# def dasher():
#     global RESTURANT_ID,USER_ID, DELIVERY_STATUS
# >>>>>>> adba21b69f4cf4e7f72ee7863036281c4211ff96
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
    # app.run(debug=True, port=8081)
    app.run(host="0.0.0.0",debug=True)
