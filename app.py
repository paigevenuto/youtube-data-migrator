from waitress import serve
from flask import Flask, render_template, request, redirect, session, flash, jsonify
from forms import AddLoginForm, AddSignUpForm
from models import db, connect_db, User, Subscription, LikedVideo, Watchlater, AddedPlaylist, UserPlaylist, PlaylistVideo
from flask_bcrypt import Bcrypt
import datetime
import jwt
from functools import wraps
import os

app = Flask(__name__)

# Get secrets from environment
app.config["SECRET_KEY"] = os.environ['FLASK_KEY']
JWT_KEY = os.environ['JWT_KEY']
DATABASE_URL = os.environ['DATABASE_URL']
PORT = os.environ['PORT']

# App config
app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE_URL
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ECHO'] = True
SESSION_COOKIE_SAMESITE = 'Strict'

bcrypt = Bcrypt()

connect_db(app)
db.create_all()

def login_required(function):
    @wraps(function)
    def wrapper(*args, **kwargs):
        try:
            authtoken = session['auth']
            authtoken = jwt.decode(authtoken, JWT_KEY)
            if authtoken['user']:
                return function()
        except:
            return redirect('/login')
        return redirect('/login')
    return wrapper

@app.route('/')
def mainpage():
    return render_template('welcome.html')

@app.route('/learnmore')
def learnmore():
    return render_template('learnmore.html')

@app.route('/login', methods=["GET", "POST"])
def login():
    form = AddLoginForm()
    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data
        user = User.query.filter_by(username=username).first_or_404()
        if bcrypt.check_password_hash(user.password_hash, password):
            token = {
                    'user' : username,
                    'exp' : datetime.datetime.utcnow() + datetime.timedelta(days=14),
                    }
            jwttoken = jwt.encode(token, JWT_KEY)
            session['auth'] = jwttoken
            return redirect("/dashboard")
    return render_template('login.html', form=form)
    
test = 'test'

@app.route('/signup', methods=["GET", "POST"])
def signup():
    form = AddSignUpForm()
    if form.validate_on_submit():

        # Get form values
        username = form.username.data
        password = form.password.data
        privacyAgree = form.privacyAgree.data
        
        # Check if user already exists
        try:
            userExists = User.query.filter_by(username=username).first_or_404()
            if bool(userExists):
                userExists = True
        except:
            userExists = False

        if not userExists and privacyAgree:
            # Hash password
            hash = bcrypt.generate_password_hash(password)
            hashutf = hash.decode("utf8")

            # Save user to database
            newuser = User(
                    username = username,
                    password_hash = hashutf
                    )
            db.session.add(newuser)
            db.session.commit()

            # Generate login token
            token = {
                    'user' : username,
                    'exp' : datetime.datetime.utcnow() + datetime.timedelta(days=14),
                    }
            jwttoken = jwt.encode(token, JWT_KEY)
            session['auth'] = jwttoken
            return redirect("/dashboard")
        else:
            return 'username taken'
    else:
        return render_template('signup.html', form=form)

@app.route('/dashboard')
@login_required
def dashboard():
    return "dashboard"

serve(app, port=PORT)
