# 3rd-party packages
from flask import render_template, request, redirect, url_for, flash, Response
from flask_mongoengine import MongoEngine
from flask_login import LoginManager, current_user, login_user, logout_user, login_required
from flask_bcrypt import Bcrypt
from werkzeug.utils import secure_filename

# stdlib
from datetime import datetime

# local
from . import app, bcrypt, client
from .forms import (SearchForm, MovieReviewForm, RegistrationForm, LoginForm,
                             UpdateUsernameForm, UpdateProfilePicForm)
from .models import User, Review, load_user
from .utils import current_time

""" ************ View functions ************ """
@app.route('/', methods=['GET', 'POST'])
def index():
    form = SearchForm()

    if form.validate_on_submit():
        return redirect(url_for('query_results', query=form.search_query.data))

    return render_template('index.html', form=form)

@app.route('/search-results/<query>', methods=['GET'])
def query_results(query):
    results = client.search(query)

    return render_template('query.html', results=results)

@app.route('/movies/<game_id>', methods=['GET', 'POST'])
def game_detail(game_id):
    result = client.retrieve_game_by_id(game_id)

    return render_template('movie_detail.html', game=result )

@app.route('/user/<username>')
def user_detail(username):
    user = User.objects(username = username).first()
    if (user is not None):
        reviews = list(Review.objects(commenter = user))
        return render_template('user_detail.html', username = username, reviews = reviews)
    else:
        return render_template('user_detail.html', username = username, error = "No such user exists")

"""
EXTRA CREDIT: Refer to the README
"""
@app.route('/images/<username>')
def images(username):
    pass


""" ************ User Management views ************ """
@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        hashed = bcrypt.generate_password_hash(form.password.data).decode()
        user = User( email = form.email.data, username = form.username.data, password = hashed)
        user.save()
        return redirect(url_for('login'))
    
    return render_template("register.html", form = form)


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.objects(username = form.username.data).first()
        if (user is not None and bcrypt.check_password_hash(user.password, form.password.data)):
            login_user(user)
            return redirect(url_for('account'))
        else:
            flash('Log in Failed')
      
    return render_template('login.html', form = form)

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))

@app.route('/account', methods=['GET', 'POST'])
@login_required
def account():
    form = UpdateUsernameForm()
    if form.validate_on_submit():
        user = User.objects(username = current_user.username).first()
        user.modify(username = form.new_username.data)
        user.save()
        return redirect(url_for('login'))
    return render_template("account.html" , username = current_user.username , form = form)
