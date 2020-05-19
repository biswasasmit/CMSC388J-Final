from flask_login import UserMixin
import pyotp
from datetime import datetime
from . import db, login_manager

@login_manager.user_loader
def load_user(user_id):
    return User.objects(username=user_id).first()

class User(db.Document, UserMixin):
    email = db.EmailField(unique=True, required=True)
    username = db.StringField(unique=True, required=True, min_length=1, max_length=40)
    password = db.StringField(required=True)
    profile_pic = db.FileField()
    otp_secret = db.StringField(required=True, min_length=16, max_length=16, default=pyotp.random_base32())

    # Returns unique string identifying our object
    def get_id(self):
        return self.username

class Game(db.EmbeddedDocument):
    game_id = db.StringField(required=True, unique=True)
    name = db.StringField(required=True)

class UserGameList(db.Document):
    user = db.ReferenceField(User, required=True)
    games = db.ListField(db.EmbeddedDocumentField(Game), default = [])

class Review(db.Document):
    commenter = db.ReferenceField(User, required=True)
    content = db.StringField(required=True, min_length=5, max_length=500)
    date = db.StringField(required=True)
    game_id = db.StringField(required=True, length=9)
    game_title = db.StringField(required=True, min_length=1, max_length=150)
