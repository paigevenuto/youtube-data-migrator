from flask_sqlalchemy import SQLAlchemy
import datetime

db = SQLAlchemy()

def connect_db(app):
    """Connect to database."""

    db.app = app
    db.init_app(app)

class User(db.Model):
    """User."""

    __tablename__ = "users"

    id = db.Column( db.Integer, primary_key=True, autoincrement=True)
    username = db.Column( db.Text, nullable=False)
    password_hash = db.Column( db.Text, nullable=False)


class Subscription(db.Model):
    """Subscription."""

    __tablename__ = "subscriptions"

    id = db.Column( db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column( db.Integer, db.ForeignKey('users.id'))
    channel_id = db.Column( db.Text, nullable=False)

class LikedVideo(db.Model):
    """liked Video."""

    __tablename__ = "liked_videos"

    id = db.Column( db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column( db.Integer, db.ForeignKey('users.id'))
    video_id = db.Column( db.Text, nullable=False)
    title = db.Column( db.Text, nullable=False)
    channel_title = db.Column( db.Text, nullable=False)
    thumbnail_url = db.Column( db.Text, nullable=False)

class Watchlater(db.Model):
    """Watch Later."""

    __tablename__ = "watch_later"

    id = db.Column( db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column( db.Integer, db.ForeignKey('users.id'))
    video_id = db.Column( db.Text, nullable=False)
    title = db.Column( db.Text, nullable=False)
    channel_title = db.Column( db.Text, nullable=False)
    thumbnail_url = db.Column( db.Text, nullable=False)

class AddedPlaylist(db.Model):
    """Added Playlist."""

    __tablename__ = "added_playlists"

    id = db.Column( db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column( db.Integer, db.ForeignKey('users.id'))
    thumbnail_url = db.Column( db.Text, nullable=False)
    title = db.Column( db.Text, nullable=False)
    channel_title = db.Column( db.Text, nullable=False)
    playlist_id = db.Column( db.Text, nullable=False)

class UserPlaylist(db.Model):
    """User Playlist."""

    __tablename__ = "user_playlists"

    id = db.Column( db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column( db.Integer, db.ForeignKey('users.id'))
    thumbnail_url = db.Column( db.Text, nullable=False)
    title = db.Column( db.Text, nullable=False)
    privacy_status = db.Column( db.Text, nullable=False)
    playlist_id = db.Column( db.Text, nullable=False)

class PlaylistVideo(db.Model):
    """Playlist Video."""

    __tablename__ = "playlist_videos"

    id = db.Column( db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column( db.Integer, db.ForeignKey('users.id'))
    user_playlist_id = db.Column( db.Integer, db.ForeignKey('user_playlists.id'))
    video_id = db.Column( db.Text, nullable=False)
    title = db.Column( db.Text, nullable=False)
    channel_title = db.Column( db.Text, nullable=False)
    thumbnail_url = db.Column( db.Text, nullable=False)
