# 3rd-party packages
from flask import Flask, render_template, request, redirect, url_for
from flask_mongoengine import MongoEngine
from flask_login import LoginManager, current_user, login_user, logout_user, login_required
from flask_bcrypt import Bcrypt
from flask_talisman import Talisman
from werkzeug.utils import secure_filename

# stdlib
import os
from datetime import datetime

# local
from .client import GameClient

app = Flask(__name__)
app.config['MONGODB_HOST'] = 'mongodb://localhost:27017/goodplays'
app.config['SECRET_KEY'] = b'\x020;yr\x91\x11\xbe"\x9d\xc1\x14\x91\xadf\xec'

db = MongoEngine(app)
login_manager = LoginManager(app)
login_manager.login_view = 'users.login'
bcrypt = Bcrypt(app)
csp = {
    'default-src': [
        '\'self\'', 
        'https://stackpath.bootstrapcdn.com/bootstrap/4.4.1/css/bootstrap.min.css'
        ],
    'img-src': '*',
    'script-src' : [
        'https://code.jquery.com/jquery-3.4.1.slim.min.js', 
        'https://cdn.jsdelivr.net/npm/popper.js@1.16.0/dist/umd/popper.min.js',
        'https://stackpath.bootstrapcdn.com/bootstrap/4.4.1/js/bootstrap.min.js'
        ]
}

talisman = Talisman(app, content_security_policy=csp)
client = GameClient(os.environ.get('IGDB_API_KEY'))

from flask_app.main.routes import main
from flask_app.users.routes import users
from flask_app.games.routes import games

for bp in [main, users, games]:
    app.register_blueprint(bp)