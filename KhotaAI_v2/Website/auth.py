from flask import Blueprint, render_template, request, flash, redirect, url_for
from .models import User
from werkzeug.security import generate_password_hash, check_password_hash
from . import db
from flask_login import login_user, login_required, logout_user, current_user
import requests
from requests.exceptions import Timeout
import random
from alembic import op
import sqlalchemy as sa

auth = Blueprint('auth', __name__)
key = generate_password_hash(password=str(random.randint(1, 10 ** 24)), method='sha256')


@auth.route('/login', methods=['GET', 'POST'])
def login():

    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        print(email, password)

        user = User.query.filter_by(email=email).first()
        if user:
            if user.role == 'Temp':
                flash('Not yet', category='error')
            else:
                if check_password_hash(user.password, password):
                    flash('Logged in successfully!', category='success')
                    login_user(user, remember=True)
                    return redirect(url_for('views.home'))
                else:
                    flash('Incorrect password, try again.', category='error')
        else:
            flash('Email does not exist.', category='error')

    return render_template("login.html", user=current_user, role=None)


@auth.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('auth.login'))


@auth.route('/accept' + key)
def accept():
    return '<h1> how ?</h1>'


@auth.route('/sign-up', methods=['GET', 'POST'])
def sign_up():
    global key
    if request.method == 'POST':
        email = request.form.get('email')
        first_name = request.form.get('firstName')
        password1 = request.form.get('password1')
        password2 = request.form.get('password2')
        print(email, first_name, password1, password2)

        user = User.query.filter_by(email=email).first()

        if user:
            flash('Email already exists.', category='error')
        elif len(email) < 4:
            flash('Email must be greater than 3 characters.', category='error')
        elif len(first_name) < 2:
            flash('First name must be greater than 1 character.', category='error')
        elif password1 != password2:
            flash('Passwords don\'t match.', category='error')
        elif len(password1) < 7:
            flash('Password must be at least 7 characters.', category='error')
        else:
            try:
                key = generate_password_hash(password=str(random.randint(1, 10 ** 24)), method='sha256')

                new_user = User(email=email, first_name=first_name, password=generate_password_hash(
                    password1, method='sha256'), role='Temp')
                db.session.add(new_user)
                db.session.commit()
                flash('Account requested', category='success')
                return redirect(url_for('views.home'))
            except Timeout as ex:
                flash('not accepted', 'error')

    return render_template("sign_up.html", user=current_user, role=None)
