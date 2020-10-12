from waitress import serve
from flask import Flask, render_template, request, redirect, session, flash, send_file
from forms import AddLoginForm, AddSignUpForm, AddDelAccForm, AddSelectionForm, AddImportForm
from models import db, connect_db, User, Subscription, LikedVideo, Playlist, PlaylistVideo, Credential
from flask_bcrypt import Bcrypt
import datetime
import jwt
from functools import wraps
import os
import ytmapi
import json
import tempfile

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

@app.route('/privacy')
def privacyPolicy():
    return render_template('privacy_policy.html')

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


@app.route('/auth/google/signin')
@login_required
def authenticate():
    # Generate authorization_url and state token
    authorization_url = ytmapi.get_authorization_url()

    # Save current state to user's session
    session['state'] = authorization_url[1]
    url = authorization_url[0]
    return redirect(url)

@app.route('/auth/google/callback')
@login_required
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
    ytmapi.save_credentials(credentials, user)
    return 'this window should close automatically'

@app.route('/dashboard')
@login_required
def dashboard():
    username = get_session_user()
    user = get_user(username) 
    
    likeslist = LikedVideo.query.filter_by(user_id=user.id).all()
    subslist = Subscription.query.filter_by(user_id=user.id).all()
    playlistlist = Playlist.query.filter_by(user_id=user.id).all()
    
    delAccForm = AddDelAccForm()
    selectionForm = AddSelectionForm()
    importForm = AddImportForm()

    return render_template('dashboard.html', subs=subslist, likes=likeslist, playlists=playlistlist, delAccForm=delAccForm, selectionForm=selectionForm, importForm=importForm)

@app.route('/delacc', methods=["POST"])
@login_required
def delAcc():
    delAccForm = AddDelAccForm()
    if delAccForm.validate_on_submit():
        username = get_session_user()
        user = get_user(username)
        db.session.delete(user)
        db.session.commit()
    return redirect("/")

@app.route('/delete', methods=["POST"])
# @login_required
def deleteSelection():
    selectionform = AddSelectionForm()
    if selectionform.validate_on_submit():
        username = get_session_user()
        user = get_user(username)
        items = request.form.to_dict()
        items.pop("csrf_token")
        for item in items.keys():
            if item[-7:] == 'videoid':
                LikedVideo.query.filter_by(user_id=user.id).filter_by(video_id=item[:-7]).delete()
            elif item[-7:] == 'channel':
                Subscription.query.filter_by(user_id=user.id).filter_by(channel_id=item[:-7]).delete()
            elif item[-7:] == 'playlis':
                playlist = Playlist.query.filter_by(user_id=user.id).filter_by(resource_id=item[:-7]).delete()
                db.session.delete(playlist)
        db.session.commit()
    return redirect("/dashboard")

@app.route('/logout')
@login_required
def logout():
    session.clear()
    return redirect('/')

@app.route('/import', methods=["POST"])
@login_required
def importData():
    importForm = AddImportForm()
    if importForm.validate_on_submit():
        username = get_session_user()
        user = get_user(username)
        if importForm.subscriptions.data:
            ytmapi.import_subscriptions(user)
        if importForm.likedVideos.data:
            ytmapi.import_liked_videos(user)
        if importForm.playlists.data:
            ytmapi.import_playlists(user)
    return redirect('/dashboard')

@app.route("/download-json", methods=["POST"])
@login_required
def downloadJson():
    selectionform = AddSelectionForm()
    if selectionform.validate_on_submit():
        username = get_session_user()
        user = get_user(username)
        items = request.form.to_dict()
        items.pop("csrf_token")
        fd, filepath = tempfile.mkstemp()
        data = {
                "liked_videos":[],
                "subscriptions":[],
                "playlists":[]
                }
        for item in items.keys():
            if item[-7:] == 'videoid':
                video = LikedVideo.query.filter_by(user_id=user.id).filter_by(video_id=item[:-7]).first_or_404()
                videoDict = {
                        'channel_title' : video.channel_title,
                        'video_title' : video.title,
                        'video_id' : video.video_id
                        }
                data['liked_videos'].append(videoDict)
            elif item[-7:] == 'channel':
                channel = Subscription.query.filter_by(user_id=user.id).filter_by(channel_id=item[:-7]).first_or_404()
                channelDict = {
                        'channel_title' : channel.title,
                        'channel_id' : channel.channel_id
                        }
                data['subscriptions'].append(channelDict)
            elif item[-7:] == 'playlis':
                playlist = Playlist.query.filter_by(user_id=user.id).filter_by(resource_id=item[:-7]).first_or_404()
                # playlist_items = PlaylistVideo.query.filter_by(user_id=user.id).filter_by(playlist_id=item[:-7]).all()
                # playlist_contents = map(lambda x: x.video_id, playlist_items)
                playlistDict = {
                        'playlist_title' : playlist.title,
                        'privacy_status' : playlist.privacy_status,
                        'playlist_id' : playlist.resource_id,
                        # 'playlist_items' : playlist_contents
                        }
                data['playlists'].append(playlistDict)

        with os.fdopen(fd, "w") as f:
            json.dump(data, f)
    return send_file(filepath, as_attachment=True, attachment_filename="Your_YouTube_Data.json")

@app.route("/export", methods=["POST"])
@login_required
def exportData():
    selectionform = AddSelectionForm()
    if selectionform.validate_on_submit():
        username = get_session_user()
        user = get_user(username)
        items = request.form.to_dict()
        items.pop("csrf_token")
        for item in items.keys():
            if item[-7:] == 'videoid':
                video = LikedVideo.query.filter_by(user_id=user.id).filter_by(video_id=item[:-7]).first_or_404()
            elif item[-7:] == 'channel':
                channel = Subscription.query.filter_by(user_id=user.id).filter_by(channel_id=item[:-7]).first_or_404()
            elif item[-7:] == 'playlis':
                playlist = Playlist.query.filter_by(user_id=user.id).filter_by(resource_id=item[:-7]).first_or_404()
    return 'This may take a while, please wait for results'

@app.route('/testplaylists')
def testplaylists():
    username = get_session_user()
    user = get_user(username)
    playlists = ytmapi.get_playlists(user)
    ytmapi.save_playlists(playlists, user)

serve(app, port=PORT)
