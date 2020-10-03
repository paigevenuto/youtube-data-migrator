from waitress import serve
from flask import Flask, render_template, request, redirect, session, flash, jsonify
from forms import AddLoginForm, AddSignUpForm
from models import db, connect_db, User, Subscription, LikedVideo, Playlist, PlaylistVideo, Credential
from flask_bcrypt import Bcrypt
import datetime
import jwt
from functools import wraps
import os
import ytmapi
import json

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

def get_session_user():
    authtoken = session['auth']
    authtoken = jwt.decode(authtoken, JWT_KEY)
    username = authtoken['user']
    return username

def get_user(username):
    user = User.query.filter_by(username=username).first_or_404()
    return user

def create_login_token(username):
    token = {
            'user' : username,
            'exp' : datetime.datetime.utcnow() + datetime.timedelta(days=14),
            }
    jwttoken = jwt.encode(token, JWT_KEY)
    session['auth'] = jwttoken
    return

def login_required(function):
    @wraps(function)
    def wrapper(*args, **kwargs):
        try:
            username = get_session_user()
            user = get_user(username)
            if user.username == username:
                return function()
            else:
                return redirect('/login')
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

    # Dictionary for potential login errors
    errors = {
        'username' : {
            'error' : '',
            'labelclass' : '',
            'icon' : ''
            },
        'password' : {
            'error' : '',
            'labelclass' : '',
            'icon' : ''
            }
        }
    form = AddLoginForm()

    # CSRF check
    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data

        # User in database check
        try:
            username = get_session_user()
            user = get_user(username)

            # Password correct check
            if bcrypt.check_password_hash(user.password_hash, password):
                # Provide user login token
                create_login_token(username)
                return redirect("/dashboard")
            else:
                errors['password']['error'] = 'Password is incorrect!'
                errors['password']['labelclass'] = 'mdc-text-field--invalid'
                errors['password']['icon'] = 'error'
        except:
            errors['username']['error'] = 'User does not exist!'
            errors['username']['labelclass'] = 'mdc-text-field--invalid'
            errors['username']['icon'] = 'error'
    return render_template('login.html', form=form, errors=errors)
    
@app.route('/signup', methods=["GET", "POST"])
def signup():
    # Dictionary for potential login errors
    errors = {
        'username' : {
            'error' : '',
            'labelclass' : '',
            'icon' : ''
            },
        }

    form = AddSignUpForm()
    if form.validate_on_submit():

        # Get form values
        username = form.username.data
        password = form.password.data
        privacyAgree = form.privacyAgree.data
        
        # Check if user already exists
        try:
            userExists = get_user(username)
            if bool(userExists):
                userExists = True
        except:
            userExists = False
        
        if userExists:
            errors['username']['error'] = 'User already exists!'
            errors['username']['labelclass'] = 'mdc-text-field--invalid'
            errors['username']['icon'] = 'error'

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
            create_login_token(username)
            return redirect("/dashboard")

        return render_template('signup.html', form=form, errors=errors)
    else:
        return render_template('signup.html', form=form, errors=errors)

@app.route('/dashboard')
@login_required
def dashboard():
    # Generate authorization_url and state token
    authorization_url = ytmapi.get_authorization_url()

    # Save current state to user's session
    session['state'] = authorization_url[1]
    url = authorization_url[0]

    return render_template('dashboard.html', authorization_url=url)

@app.route('/auth')
def auth():
    # Ensure that the request is not a forgery and that the user sending
    # this connect request is the expected user.
    if request.args.get('state', '') != session['state']:
      response = make_response(json.dumps('Invalid state parameter.'), 401)
      response.headers['Content-Type'] = 'application/json'
      return response

    # Retreive auth code from query or return error
    auth_code = request.args.get('code', '')
    if auth_code == '':
      response = make_response(json.dumps(request.args['error']), 401)
      response.headers['Content-Type'] = 'application/json'
      return response

    # Turn auth code into an access token
    state = request.args['state']
    username = get_session_user()
    user = get_user(username)
    credentials = ytmapi.get_access_token(auth_code, state)
    # ytmapi.save_credentials(credentials, user)
    # return 'hopefully this just saved the creds to the db'
    return str(credentials.refresh_token + "<br>" + credentials._refresh_token + "<br>" + credentials.refresh)

@app.route('/list')
def list():
    username = get_session_user()
    user = get_user(username) 
    
    likeslist = LikedVideo.query.filter_by(user_id=user.id).all()
    subslist = Subscription.query.filter_by(user_id=user.id).all()
    playlistlist = Playlist.query.filter_by(user_id=user.id).all()
    
    return render_template('list.html', subs=subslist, likes=likeslist, playlists=playlistlist)

@app.route('/likes')
@login_required
def test():
    username = get_session_user()
    user = get_user(username)
    token = Credential.query.filter_by(user_id=user.id)
    likes = ytmapi.get_liked_videos(token.token)
    ytmapi.save_liked_videos(likes)
    return 'hopefully this just saved likes to the db'

serve(app, port=PORT)
