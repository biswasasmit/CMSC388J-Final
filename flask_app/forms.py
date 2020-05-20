from flask_login import current_user
from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileRequired, FileAllowed
from werkzeug.utils import secure_filename
from wtforms import StringField, IntegerField, SubmitField, TextAreaField, PasswordField, DateField
from wtforms.validators import (InputRequired, DataRequired, NumberRange, Length, Email, 
                                EqualTo, ValidationError)
import pyotp
import re

from .models import User

class SearchForm(FlaskForm):
    search_query = StringField('Query', validators=[InputRequired(), Length(min=1, max=100)])
    submit = SubmitField('Search')

class GameReviewForm(FlaskForm):
    text = TextAreaField('Review', validators=[InputRequired(), Length(min=5, max=500)], render_kw={"placeholder": "Fantastic game!"})
    submit = SubmitField('Enter Review')

class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[InputRequired(), Length(min=1, max=40)])
    email = StringField('Email', validators=[InputRequired(), Email()])
    password = PasswordField('Password', validators=[InputRequired(), Length(min=8)])
    confirm_password = PasswordField('Confirm Password', 
                                    validators=[InputRequired(), EqualTo('password')])
    submit = SubmitField('Sign Up')

    def validate_username(self, username):
        user = User.objects(username=username.data).first()
        if user is not None:
            raise ValidationError('Username is taken.')

    def validate_email(self, email):        
        user = User.objects(email=email.data).first()
        if user is not None:
            raise ValidationError('Email is taken.')

    def validate_password(self, password):
        password = str(password.data)

        regexes = [
            (re.compile(r"[A-Z]"), 'Password must have at least one uppercase letter.'),
            (re.compile(r"\d"), 'Password must have at least one number.'),
            (re.compile(r"[^A-Za-z0-9]"), 'Password must have at least one special character.')
        ]
        
        errors = [e for (r, e) in regexes if not r.search(password)]
        if len(errors) > 0:
            raise ValidationError(' '.join(errors))

class LoginForm(FlaskForm):
    username = StringField('Username', validators=[InputRequired(), Length(min=1, max=40)])
    password = PasswordField('Password', validators=[InputRequired(), Length(min=1)])
    token = StringField('Token', validators=[InputRequired(), Length(min=6, max=6)])
    submit = SubmitField('Login')

    def validate_token(self, token):
        user = User.objects(username=self.username.data).first()
        if user is not None:
            tok_verified = pyotp.TOTP(user.otp_secret).verify(token.data)
            if not tok_verified:
                raise ValidationError("Invalid Token")


class UpdateUsernameForm(FlaskForm):
    new_username = StringField('Update username:', validators=[InputRequired(), Length(min=1, max=40)])
    submit = SubmitField('Update')

    def validate_new_username(self, new_username):
        user = User.objects(username=new_username.data).first()
        if user is not None:
            raise ValidationError('Username is taken')

class InviteFriendForm(FlaskForm):
    email = StringField('Email', validators=[InputRequired(), Email()])
    subject = StringField('Subject', validators=[Length(min=1, max=40)])
    body = TextAreaField('Email Body', validators=[InputRequired(), Length(min=5, max=500)], default = "Come join me on Goodplays! Sign up today!")
    send = SubmitField('Send')

allowed_exts = ['jpg', 'png', 'jpeg', 'gif']
class UpdateProfilePicForm(FlaskForm):
    pic = FileField('Update profile picture:', \
        validators=[FileRequired(), FileAllowed(allowed_exts, 'Images only')])
    submit = SubmitField('Update')

class AddToListButton(FlaskForm):
    submit = SubmitField("Add to Play Later")

class AddToPlayedForm(FlaskForm):
    finished_on = DateField('Date', validators=[InputRequired()], render_kw={"placeholder": "2020-05-20"})
    review = TextAreaField('Comment', validators=[InputRequired(), Length(min=5, max=500)], render_kw={"placeholder": "I loved this game!"})
    submit = SubmitField("Mark as Played")

class AddToPlayedButton(FlaskForm):
    submit = SubmitField("Mark as Played")