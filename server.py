from flask import Flask, render_template, flash, redirect, url_for, session, logging, request
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import desc

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
db = SQLAlchemy(app)

app.secret_key = 'BAD_SECRET_KEY'

class user(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80))
    email = db.Column(db.String(120))
    name = db.Column(db.String(120))
    password = db.Column(db.String(80))

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

@app.route("/restaurant.html")
def restaurant_page():
    current_rid = int(request.args.get("rid"))
    restaurant_info = restaurant.query.filter_by(rid=current_rid).first()
    foods = menu.query.filter_by(rid=current_rid, category="food").all()
    drinks = menu.query.filter_by(rid=current_rid, category="drink").all()
    desserts = menu.query.filter_by(rid=current_rid, category="dessert").all()

    return render_template("restaurant.html", restaurant_info=restaurant_info,
                                              foods=foods,
                                              drinks=drinks,
                                              desserts=desserts)

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        uname = request.form["uname"]
        passw = request.form["passw"]

        login = user.query.filter_by(username=uname, password=passw).first()
        if login is not None:
            return redirect(url_for('index')) # goes to home page / and url also changes
    return render_template("login.html")


@app.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method == "POST":
        name = request.form['name']
        uname = request.form['uname']
        passw = request.form['passw']

        register = user(name=name, username=uname, password=passw)
        db.session.add(register)
        db.session.commit()
        return render_template("login.html")
    return render_template("signup.html")


if __name__ == "__main__":
    db.create_all()
    app.run(debug=True, port=8081)
