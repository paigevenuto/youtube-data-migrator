from models import db, connect_db, User, Subscription, LikedVideo, Playlist, PlaylistVideo, Credential
import datetime

DATABASE_URL = os.environ['DATABASE_URL']
app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE_URL
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ECHO'] = True
connect_db(app)
db.create_all()

timenow = datetime.datetime.utcnow().timestamp()
vids = LikedVideo.query.filter(LikedVideo.expiration_date >= timenow).all()
db.session.delete(vids)
subs = Subscription.query.filter(Subscription.expiration_date >= timenow).all()
db.session.delete(subs)
lists = Playlist.query.filter(Playlist.expiration_date >= timenow).all()
db.session.delete(lists)

db.session.commit()
