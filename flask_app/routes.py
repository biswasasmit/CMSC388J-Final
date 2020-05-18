# 3rd-party packages
from flask import render_template, request, redirect, url_for, flash, Response, send_file
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

bcrypt = Bcrypt()

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

    if type(results) == dict:
        return render_template('query.html', error_msg=results['Error'])
    
    return render_template('query.html', results=results)

@app.route('/movies/<movie_id>', methods=['GET', 'POST'])
def movie_detail(movie_id):
    result = client.retrieve_movie_by_id(movie_id)

    if type(result) == dict:
        return render_template('movie_detail.html', error_msg=result['Error'])

    form = MovieReviewForm()
    if form.validate_on_submit():
        review = Review(
            commenter=load_user(current_user.username), 
            content=form.text.data, 
            date=current_time(),
            imdb_id=movie_id,
            movie_title=result.title
        )

        review.save()

        return redirect(request.path)

    reviews = Review.objects(imdb_id=movie_id)

    print(current_user.is_authenticated)

    return render_template('movie_detail.html', form=form, movie=result, reviews=reviews)

@app.route('/user/<username>')
def user_detail(username):
    user = load_user(username)

    if user is not None:
        reviews = Review.objects(commenter=user)
        return render_template('user_detail.html', user=user, reviews=reviews)
    else:
        return render_template('user_detail.html', err_msg="That user was not found.")

"""
EXTRA CREDIT: Refer to the README
"""
@app.route('/images/<username>')
def images(username):
    user = load_user(username)
    photo = user.profile_pic
    return send_file(photo, mimetype=photo.content_type)


""" ************ User Management views ************ """
@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('login'))

    form = RegistrationForm()
    if form.validate_on_submit():
        hashed = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user = User(
            username=form.username.data,
            email=form.email.data,
            password=hashed
        )
        user.save()
        flash("Thanks for registering! You can now log in below.")
        return redirect(url_for('login'))

    return render_template('register.html', form=form, user_exists=False)


@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('account'))
    
    form = LoginForm()
    if form.validate_on_submit():
        user = load_user(form.username.data)

        if user is not None and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user)
            return redirect(url_for('account'))
        else:
            flash("Please try again.")
    
    return render_template('login.html', form=form)

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))

@app.route('/account', methods=['GET', 'POST'])
@login_required
def account():
    user_form = UpdateUsernameForm()
    if 'name' in request.args and user_form.validate_on_submit():
        user = load_user(current_user.username)
        user.modify(username=user_form.new_username.data)
        user.save()
        
        flash("Username updated. Please login again.")
        return redirect(url_for('login'))
    
    photo_form = UpdateProfilePicForm()
    if 'photo' in request.args and photo_form.validate_on_submit():
        photo = photo_form.pic.data
        
        user = load_user(current_user.username)
        user.profile_pic.replace(photo.read(), content_type=photo.content_type)
        user.save()
        return redirect(url_for('account'))
    
    return render_template('account.html', user_form=user_form, photo_form=photo_form)