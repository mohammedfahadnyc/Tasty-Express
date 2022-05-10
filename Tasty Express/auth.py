from flask import Blueprint, render_template, flash, redirect, url_for, session, logging, request

bp = Blueprint('auth', __name__, url_prefix='/')

@bp.route("/login.html", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        uname = request.form["uname"]
        passw = request.form["passw"]

        login = user.query.filter_by(username=uname, password=passw).first()
        if login is not None:
            return render_template("home.html")
    return render_template("login.html")


@bp.route("/signup.html", methods=["GET", "POST"])
def signup():
    if request.method == "POST":
        uname = request.form['name']
        mobile = request.form['mbl']
        passw = request.form['passw']

        register = user(username=uname, email=mobile, password=passw)
        db.session.add(register)
        db.session.commit()
        return render_template("login.html")
    return render_template("signup.html")
