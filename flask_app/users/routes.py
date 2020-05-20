## User management routes

# 3rd-party packages
from flask import render_template, request, redirect, url_for, flash, Response, send_file, Blueprint, session
from flask_mongoengine import MongoEngine
from flask_login import LoginManager, current_user, login_user, logout_user, login_required
from flask_bcrypt import Bcrypt
from werkzeug.utils import secure_filename
import pyotp, qrcode
from qrcode.image import svg

# stdlib
from datetime import datetime
from io import BytesIO

# local
from .. import app, bcrypt, client
from ..forms import (SearchForm, GameReviewForm, RegistrationForm, LoginForm,
                             UpdateUsernameForm, UpdateProfilePicForm, InviteFriendForm)
from ..models import User, Review, UserGameList, load_user, PlayedGame
from ..utils import current_time

bcrypt = Bcrypt()

users = Blueprint("users", __name__)

@users.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('users.login'))

    form = RegistrationForm()
    if form.validate_on_submit():
        hashed = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user = User(
            username=form.username.data,
            email=form.email.data,
            password=hashed
        )
        user.save()
        session['new_username'] = user.username
        flash("Thanks for registering! You can now log in below.")
        return redirect(url_for('users.tfa'))

    return render_template('register.html', form=form, user_exists=False)


@users.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('users.account'))
    
    form = LoginForm()
    if form.validate_on_submit():
        user = load_user(form.username.data)

        if user is not None and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user)
            return redirect(url_for('users.account'))
        else:
            flash("Please try again.")
    
    return render_template('login.html', form=form)

@users.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('main.index'))

@users.route('/account', methods=['GET', 'POST'])
@login_required
def account():
    user_form = UpdateUsernameForm()
    if 'name' in request.args and user_form.validate_on_submit():
        user = load_user(current_user.username)
        user.modify(username=user_form.new_username.data)
        user.save()
        
        flash("Username updated. Please login again.")
        return redirect(url_for('users.login'))
    
    photo_form = UpdateProfilePicForm()
    if 'photo' in request.args and photo_form.validate_on_submit():
        photo = photo_form.pic.data
        
        user = load_user(current_user.username)
        user.profile_pic.replace(photo.read(), content_type=photo.content_type)
        user.save()
        return redirect(url_for('users.account'))

    return render_template('account.html', user_form=user_form, photo_form=photo_form)

@users.route('/user/<username>')
def user_detail(username):
    user = load_user(username)

    if user is not None:
        reviews = Review.objects(commenter=user)

        games = []
        if UserGameList.objects(user=user):
            games = UserGameList.objects(user=user).get().games

        played = []
        if PlayedGame.objects(user=user):
            played = PlayedGame.objects(user=user)

        return render_template('user_detail.html', user=user, reviews=reviews, games=games, played=played)
    else:
        return render_template('user_detail.html', err_msg="That user was not found.")

@users.route('/images/<username>')
def images(username):
    user = load_user(username)
    photo = user.profile_pic
    return send_file(photo, mimetype=photo.content_type)

@users.route("/qr_code")
def qr_code():
    if 'new_username' not in session:
        return redirect(url_for('main.index'))
    
    user = User.objects(username=session['new_username']).first()
    session.pop('new_username')

    uri = pyotp.totp.TOTP(user.otp_secret).provisioning_uri(name="GoodPlays", issuer_name='GOODPLAYS-2FA')
    img = qrcode.make(uri, image_factory=svg.SvgPathImage)
    stream = BytesIO()
    img.save(stream)

    headers = {
        'Content-Type': 'image/svg+xml',
        'Cache-Control': 'no-cache, no-store, must-revalidate',
        'Pragma': 'no-cache',
        'Expires': '0' # Expire immediately, so browser has to reverify everytime
    }

    return stream.getvalue(), headers

@users.route("/tfa")
def tfa():
    if 'new_username' not in session:
        return redirect(url_for('main.index'))

    headers = {
        'Cache-Control': 'no-cache, no-store, must-revalidate',
        'Pragma': 'no-cache',
        'Expires': '0' # Expire immediately, so browser has to reverify everytime
    }

    return render_template('tfa.html'), headers