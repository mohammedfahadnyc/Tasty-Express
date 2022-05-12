from flask import Flask, render_template, flash, redirect, url_for, session, logging, request
from flask_sqlalchemy import SQLAlchemy


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
db = SQLAlchemy(app)


class user(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80))
    email = db.Column(db.String(120))
    name = db.Column(db.String(120))
    password = db.Column(db.String(80))


@app.route("/")
def index():
    # top 10 restraunts based on rating
    search_val = request.args.get("search_val")
    restaurants = ({"name": f"Restaurant {str(num)}", "rating": f"{str(num % 5)}.5"} for num in range(1, 11))

    if search_val:
        return render_template("search.html")

    return render_template("home.html", restaurants=restaurants)


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        uname = request.form["uname"]
        passw = request.form["passw"]

        login = user.query.filter_by(username=uname, password=passw).first()
        if login is not None:
            return render_template("home.html")
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
