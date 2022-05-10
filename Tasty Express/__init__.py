from flask import Flask, render_template, flash, redirect, url_for, session, logging, request
from flask_sqlalchemy import SQLAlchemy

def create_app(test_config=None):
    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
    db = SQLAlchemy(app)

    class user(db.Model):
        id = db.Column(db.Integer, primary_key=True)
        username = db.Column(db.String(80))
        email = db.Column(db.String(120))
        password = db.Column(db.String(80))

    from . import auth
    app.register_blueprint(auth.bp)

    from . import home
    app.register_blueprint(home.bp)
    app.add_url_rule('/', endpoint='home')

    return app
