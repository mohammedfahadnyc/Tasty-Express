from flask import Blueprint, render_template, flash, redirect, url_for, session, logging, request

bp = Blueprint('home', __name__)

@bp.route('/')
def home():
    return render_template("home.html")
