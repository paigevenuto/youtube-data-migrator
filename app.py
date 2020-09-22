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
app.config["SECRET_KEY"] = os.environ['FLASK_KEY']
jwtkey = os.environ['jwtkey']
oauth_secret = os.environ['oauth_secret']

app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql:///ytmdb'
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
            authtoken = jwt.decode(authtoken, jwtkey)
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
            jwttoken = jwt.encode(token, jwtkey)
            session['auth'] = jwttoken
            return redirect("/dashboard")
    return render_template('login.html', form=form)
    
@app.route('/signup', methods=["GET", "POST"])
def signup():
    form = AddSignUpForm()
    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data
        privacyAgree = form.privacyAgree.data
        hash = bcrypt.generate_password_hash(password)
        hashutf = hash.decode("utf8")
        newuser = User(
                username = username,
                password_hash = hashutf
                )
        db.session.add(newuser)
        db.session.commit()
        return redirect("/dashboard")
    else:
        return render_template('signup.html', form=form)

@app.route('/dashboard')
@login_required
def dashboard():
    return "dashboard"

serve(app, port=5000)
