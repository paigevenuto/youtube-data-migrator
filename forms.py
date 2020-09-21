from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField

class AddLoginForm(FlaskForm):
    """Form for logging in"""
    username = StringField("Username")
    password = PasswordField("Password")

class AddSignUpForm(FlaskForm):
    """Form for signing up"""
    username = StringField("Username")
    password = PasswordField("Password")
    privacyAgree = BooleanField("Privacy Agreement")
