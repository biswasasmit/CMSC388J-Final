# 3rd-party packages
from flask import Flask, render_template, request, redirect, url_for
from flask_mongoengine import MongoEngine
from flask_login import LoginManager, current_user, login_user, logout_user, login_required
from flask_bcrypt import Bcrypt
from flask_talisman import Talisman
from werkzeug.utils import secure_filename
from flask_mail import Mail, Message

# stdlib
import os
from datetime import datetime

# local
from .client import GameClient

app = Flask(__name__)
app.config['MONGODB_HOST'] = 'mongodb://localhost:27017/goodplays'
app.config['SECRET_KEY'] = b'\x020;yr\x91\x11\xbe"\x9d\xc1\x14\x91\xadf\xec'

app.config['MAIL_SERVER']='smtp.gmail.com'
app.config['MAIL_PORT'] = 465
app.config['MAIL_USERNAME'] = os.environ.get('GOODPLAYS_MAIL_USERNAME')
app.config['MAIL_PASSWORD'] = os.environ.get('GOODPLAYS_MAIL_PASSWORD')
app.config['MAIL_USE_TLS'] = False
app.config['MAIL_USE_SSL'] = True

db = MongoEngine(app)
login_manager = LoginManager(app)
login_manager.login_view = 'users.login'
bcrypt = Bcrypt(app)
csp = {
    'default-src': [
        '\'self\'', 
        'https://stackpath.bootstrapcdn.com/bootstrap/4.4.1/css/bootstrap.min.css',
        'https://maxcdn.bootstrapcdn.com/bootstrap/3.4.1/css/bootstrap.min.css'
        ],
    'img-src': '*',
    'script-src' : [
        'https://code.jquery.com/jquery-3.4.1.slim.min.js', 
        'https://cdn.jsdelivr.net/npm/popper.js@1.16.0/dist/umd/popper.min.js',
        'https://stackpath.bootstrapcdn.com/bootstrap/4.4.1/js/bootstrap.min.js',
        'https://maxcdn.bootstrapcdn.com/bootstrap/3.4.1/js/bootstrap.min.js',
        'https://ajax.googleapis.com/ajax/libs/jquery/3.5.1/jquery.min.js'
        ]
}

talisman = Talisman(app, content_security_policy=csp)
client = GameClient(os.environ.get('IGDB_API_KEY'))

mail = Mail(app)

from flask_app.main.routes import main
from flask_app.users.routes import users
from flask_app.games.routes import games

for bp in [main, users, games]:
    app.register_blueprint(bp)