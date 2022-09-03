from flask_sqlalchemy import SQLAlchemy
from flask_moment import Moment
from sqlalchemy import Column, Unicode, and_, true, update
from flask import (Flask)
from flask_migrate import Migrate

#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#
app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config')
db = SQLAlchemy(app)
migrate = Migrate(app, db)


#----------------------------------------------------------------------------#
# Models.
#----------------------------------------------------------------------------#

artist_venue = db.Table('artist_venue',
  db.Column('artist_id', db.Integer, db.ForeignKey('artist.id'), primary_key=True),
  db.Column('venue_id', db.Integer, db.ForeignKey('venue.id'), primary_key=True)
)
  

class Venue(db.Model):
    __tablename__ = 'venue'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    genres = db.Column(db.ARRAY(db.String))
    city = db.Column(db.String(120) , nullable = False)
    state = db.Column(db.String(120) , nullable = False)
    address = db.Column(db.String(120) , nullable = False)
    phone = db.Column(db.String(120) , nullable = False)
    website = db.Column(db.String(120))
    seeking_talent = db.Column(db.String(120))
    seeking_description = db.Column(db.String(120))
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))
    show = db.relationship('Show', backref='venue', lazy=True)
 

def __repr__(self):
      return f'<Venue ID: {self.id}, name: {self.name}>'

class Artist(db.Model):
    __tablename__ = 'artist'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable = False)
    genres = db.Column(db.ARRAY(db.String)) 
    city = db.Column(db.String(120), nullable = False)
    state = db.Column(db.String(120), nullable = False)
    phone = db.Column(db.String(120))
    website_link = db.Column(db.String(120))
    image_link = db.Column(db.String(500))    
    facebook_link = db.Column(db.String(120))
    seeking_venue = db.Column(db.String(120))
    seeking_description = db.Column(db.String(300))
    venue = db.relationship('Venue', 
    secondary=artist_venue,
    backref=db.backref('performing_artist', lazy=True)
    )
    show = db.relationship('Show', backref='artist', lazy=True)
    
    # def __repr__(self):
    #   return f'<Artist ID: {self.id}, name: {self.name}>'

class Show(db.Model):
  __tablename__ = 'show'
  id = db.Column(db.Integer, primary_key=True)
  artist_id = db.Column(db.Integer, nullable = False)  
  venue_id = db.Column(db.Integer, nullable = False)
  start_time = db.Column(db.DateTime(), nullable = False)
  performing_artist = db.Column(db.Integer, db.ForeignKey('artist.id'), nullable = False)
  venue_for_show = db.Column(db.Integer, db.ForeignKey('venue.id'), nullable = False)
  
db.create_all()

