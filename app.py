#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#

from ast import And
from email.policy import default
from itertools import count
import json
import logging
from sre_parse import State
import sys
# from distutils.log import error
from logging import FileHandler, Formatter
from tokenize import String
from urllib import response

import babel
import dateutil.parser
from flask import (Flask, Response, flash, jsonify, redirect, render_template,
                   request, session, url_for)
from flask_migrate import Migrate
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import Form
from sqlalchemy import Column, Unicode, and_, true, update
import datetime

from forms import *

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


#----------------------------------------------------------------------------#
# Filters.
#----------------------------------------------------------------------------#

def format_datetime(value, format='medium'):
  date = dateutil.parser.parse(value)
  if format == 'full':
      format="EEEE MMMM, d, y 'at' h:mma"
  elif format == 'medium':
      format="EE MM, dd, y h:mma"
  return babel.dates.format_datetime(date, format, locale='en')

app.jinja_env.filters['datetime'] = format_datetime

#----------------------------------------------------------------------------#
# Controllers.
#----------------------------------------------------------------------------#

@app.route('/')
def index():
  return render_template('pages/home.html')


#  Venues
#  ----------------------------------------------------------------

@app.route('/venues')
def venues():
 
  try:
    error = False
    data = []
    places = Venue.query.with_entities(Venue.city, Venue.state).distinct().all()
  
    for city_state in places:
      city = city_state[0]
      state = city_state[1]
      venues = Venue.query.filter_by(city=city, state=state).all()
      data.append({
      "city" : city,
      "state" : state,
      "venues" : venues
    })
    
  except:    
    error = True
    db.session.rollback()
    print(sys.exc_info())
  finally:
    db.session.close()  
  return render_template('pages/venues.html', areas=data)

@app.route('/venues/search', methods=['POST'])
def search_venues():
 
  try :
    error = False
    data= []
    response = {}
    tag =request.form["search_term"]
    search = "%{}%".format(tag)
    results = Venue.query.filter(Venue.name.ilike(search)).all()
    
    for i in results :
      data.append({
        "id": i.id,
        "name": i.name,           
      })

    response["data"] = data
    result_lenth = len(data)
    response["count"] = result_lenth   
    
  except:
    error = True
    db.session.rollback()
    print(sys.exc_info())    
  finally:
    db.session.close()
    return render_template('pages/search_venues.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
 
  response = {}
  try:
    error = False
    past_shows = []
    upcoming_shows = []
    venue = Venue.query.get(venue_id)
    
    response['id'] = venue.id
    response['name'] = venue.name
    response['genres'] = venue.genres
    response['city'] = venue.city
    response['state'] = venue.state
    response['phone'] = venue.phone
    response['website'] = venue.website
    response['address'] = venue.address
    response['facebook_link'] = venue.facebook_link
    response['seeking_talent'] = venue.seeking_talent
    response['seeking_description'] = venue.seeking_description
    response['image_link'] = venue.image_link
    
    artist = venue.performing_artist

    for r in artist:
      show = Show.query.filter_by( venue_id = venue_id, artist_id = r.id).first()
      if show.start_time > datetime.now():
        upcoming_shows.append({
          "artist_id": r.id,
          "artist_name": r.name,
          "artist_image_link": r.image_link,
          "start_time": str(show.start_time)
        })
      else:
         past_shows.append({
          "artist_id": r.id,
          "artist_name": r.name,
          "artist_image_link": r.image_link,
          "start_time": str(show.start_time)
        })
      
    response['upcoming_shows'] = upcoming_shows
    response['past_shows'] = past_shows
    response['past_shows_count'] = len(past_shows)
    response['upcoming_shows_count'] = len(upcoming_shows)

  except:
    error = True
    print(sys.exc_info())
    db.session.rollback()
  finally:
    db.session.close()
 
  
  return render_template('pages/show_venue.html', venue=response)

#  Create Venue
#  ----------------------------------------------------------------

@app.route('/venues/create', methods=['GET'])
def create_venue_form():
  form = VenueForm()
  return render_template('forms/new_venue.html', form=form)


@app.route('/venues/create', methods=['POST'])
def create_venue_submission():
  error = False
  
  try:  
    venue = Venue(
    name = request.form.get('name'),
    city = request.form.get('city') ,
    state = request.form.get('state'),   
    address = request.form.get('address'),
    genres = request.form.getlist('genres') ,
    phone = request.form.get('phone') ,
    website = request.form.get('website', ""),
    facebook_link = request.form.get('facebook_link', ""),
    image_link = request.form.get('image_link'),
    seeking_talent = request.form.get('seeking_talent', ""),
    seeking_description = request.form.get('seeking_description', "")
    )

    db.session.add(venue)   
    db.session.commit()
   
    flash('venue '+  venue.name + ' was successfully listed!')
    
  except:
      error = True
      db.session.rollback()
      print(sys.exc_info())
  finally:
      db.session.close()
      return render_template('pages/home.html')
    
@app.route('/venues/<venue_id>', methods=['DELETE'])
def delete_venue(venue_id):
  # TODO: Complete this endpoint for taking a venue_id, and using
  # SQLAlchemy ORM to delete a record. Handle cases where the session commit could fail.

  # BONUS CHALLENGE: Implement a button to delete a Venue on a Venue Page, have it so that
  # clicking that button delete it from the db then redirect the user to the homepage
  return None

#  Artists
#  ----------------------------------------------------------------
@app.route('/artists')
def artists():    
  data = Artist.query.all()
  return render_template('pages/artists.html', artists=data)

@app.route('/artists/search', methods=['POST'])
def search_artists():
  
  try :
    error = False
    data= []
    response = {}
    tag =request.form["search_term"]
    search = "%{}%".format(tag)
    results = Artist.query.filter(Artist.name.ilike(search)).all()
    
    for i in results :
      data.append({
        "id": i.id,
        "name": i.name,
        "num_upcoming_shows": 0,   
      })

    response["data"] = data
    result_lenth = len(data)
    response["count"] = result_lenth   
    return render_template('pages/search_artists.html', results=response, search_term=request.form.get('search_term', ''))
  except:
    error = True
    db.session.rollback()
    print(sys.exc_info())    
  finally:
    db.session.close()
    

@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
 

  response = {}
  try:
    upcoming_venue_info = []
    past_venue_info = []
   
    artist = Artist.query.get(artist_id)
    
    show_venue = artist.venue
    for r in show_venue:      
      show = Show.query.filter_by(artist_id = artist_id, venue_id = r.id).first()
      
      if show.start_time > datetime.now():         
        upcoming_venue_info.append({
          "venue_id": r.id,
          "venue_name": r.name,
          "venue_image_link": r.image_link,
          "start_time": str(show.start_time)
        })
      else:
        past_venue_info.append({
          "venue_id": r.id,
          "venue_name": r.name,
          "venue_image_link": r.image_link,
          "start_time": str(show.start_time)
        })
      
      response['upcoming_shows'] = upcoming_venue_info
      response['past_shows'] = past_venue_info
      response['upcoming_shows_count'] = len(upcoming_venue_info)
      response['past_shows_count'] = len(past_venue_info)
      response['id']= artist.id
      response['name']= artist.name
      response['genres']= artist.genres
      response['city']= artist.city
      response['state']= artist.state
      response['phone']= artist.phone
      response['website']= artist.website_link
      response['seeking_venue']= artist.seeking_venue
      response['facebook_link']= artist.facebook_link
      response['image_link']= artist.image_link    

  except:
    error = True
    db.session.rollback()
    print(sys.exc_info())
  finally:
    db.session.close()
  
  return render_template('pages/show_artist.html', artist=response)

#  Update
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
  form = ArtistForm()
 
  query = Artist.query.get(artist_id)
  artist = {
    "id": query.id,
    "name" : query.name,
    "city" : query.city,
    "state" : query.state,
    "phone" : query.phone,
    "website" : query.website_link,
    "facebook_link" : query.facebook_link,
    "seeking_venue" : query.seeking_venue,    
    "image_link" : query.image_link,
  }
  
  return render_template('forms/edit_artist.html', form=form, artist=artist)

@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
  
  # artist record with ID <artist_id> using the new attributes
  try:
    error = False
    artist = Artist.query.get(artist_id)
    # updating the records for artist
    artist.name = request.form.get('name')
    artist.city = request.form.get('city')    
    artist.state = request.form.get('state')   
    artist.address = request.form.get('address')   
    artist.genres = request.form.getlist('genres') 
    artist.phone = request.form.get('phone') 
    artist.website_link = request.form.get('website', '')
    artist.facebook_link = request.form.get('facebook_link', '')
    artist.image_link = request.form.get('image_link')    
    artist.seeking_talent = request.form.get('seeking_talent', '')
    artist.seeking_description = request.form.get('seeking_description', '')

    db.session.commit()
    flash("Artist " + artist.name + "records updated successfully")
  except:
    error = True
    print(sys.exc_info())
    db.session.rollback()
  finally:
    return redirect(url_for('show_artist', artist_id=artist_id))

@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
  form = VenueForm()
  
  query = Venue.query.get(venue_id)
  venue = {
    "id": query.id,
    "name": query.name,
    "genres": query.genres,
    "address": query.address,
    "city":query.city,
    "state": query.state,
    "phone": query.phone,
    "website": query.website,
    "facebook_link": query.facebook_link,
    "seeking_talent": query.seeking_talent,
    "seeking_description": query.seeking_description,
    "image_link": query.image_link,
    
  }

  return render_template('forms/edit_venue.html', form=form, venue=venue)

@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):

  try:
    error = False
    # Getting the record with the ID venue_id
    venue = Venue.query.get(venue_id)
    # Updating the record with the submitted data
    venue.name = request.form.get('name')
    venue.city = request.form.get('city')    
    venue.state = request.form.get('state')   
    venue.address = request.form.get('address')   
    venue.genres = request.form.getlist('genres') 
    venue.phone = request.form.get('phone') 
    venue.website = request.form.get('website')
    venue.facebook_link = request.form.get('facebook_link')
    venue.image_link = request.form.get('image_link')    
    venue.seeking_talent = request.form.get('seeking_talent')
    venue.seeking_description = request.form.get('seeking_description')
    
    db.session.commit()
  except:
    error = True
    print(sys.exc_info())
    db.session.rollback()
  finally:
    db.session.close()
    return redirect(url_for('show_venue', venue_id=venue_id))

#  Create Artist
#  ----------------------------------------------------------------

@app.route('/artists/create', methods=['GET'])
def create_artist_form():
  form = ArtistForm()
  return render_template('forms/new_artist.html', form=form)

@app.route('/artists/create', methods=['POST'])
def create_artist_submission():
  msg = []
  try:
    error = False
    artist = Artist(
      name = request.form.get('name'),
      city = request.form.get('city'),
      state = request.form.get('state'),      
      genres = request.form.getlist('genres'), 
      phone = request.form.get('phone'),
      website_link = request.form.get('website', ''),
      facebook_link = request.form.get('facebook_link', ''),
      image_link = request.form.get('image_link'),
      seeking_venue = request.form.get('seeking_talent',''),
      seeking_description = request.form.get('seeking_description', '')
    )
    db.session.add(artist)
    db.session.commit()
    flash('Artist ' + artist.name + ' was successfully listed!')

  except:
    error = True
    db.session.rollback()
    print(sys.exc_info())
    flash('An error occurred. Artist ' +request.form['name'] + ' could not be listed.')
  finally :
    db.session.close()  
  return render_template('pages/home.html')


#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
  data = []
  query = Show.query.all()
  for r in query:
    
    artist = Artist.query.with_entities(Artist.id, Artist.name, Artist.image_link).filter_by(id = r.performing_artist).first()
    venue = Venue.query.with_entities(Venue.id, Venue.name).filter_by(id = r.venue_for_show).first()
    data.append({
      "venue_id": venue,
      "venue_name": venue.name,
      "artist_id": artist.id,
      "artist_name": artist.name,
      "artist_image_link": artist.image_link,
      "start_time": str(r.start_time)
    })   
    
  return render_template('pages/shows.html', shows=data)

@app.route('/shows/create')
def create_shows():
  # renders form. do not touch.
  form = ShowForm()
  return render_template('forms/new_show.html', form=form)

@app.route('/shows/create', methods=['POST'])
def create_show_submission():
    
  try:    
    artist = request.form['artist_id']
    venue = request.form['venue_id']
    time = request.form['start_time']
    artist_id = ''.join(artist)    
    venue_id = ''.join(venue)

    # creaating many-many relations
    get_artist = Artist.query.get(artist_id)
    get_venue = Venue.query.get(venue_id)
    get_artist.venue.append(get_venue) 
        
    show = Show(
    artist_id = artist_id,
    venue_id = venue_id,
    start_time = time,
    performing_artist = artist_id,
    venue_for_show = venue_id
    )
    db.session.add(show)
    db.session.commit()
    flash('Show was successfully listed!')
  except:
      error = True
      db.session.rollback()    
      print(sys.exc_info())
      flash('An error occurred. Show could not be listed.')
  finally:
      db.session.close()
  return render_template('pages/home.html')
  
@app.errorhandler(404)
def not_found_error(error):
    return render_template('errors/404.html'), 404

@app.errorhandler(500)
def server_error(error):
    return render_template('errors/500.html'), 500


if not app.debug:
    file_handler = FileHandler('error.log')
    file_handler.setFormatter(
        Formatter('%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]')
    )
    app.logger.setLevel(logging.INFO)
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
    app.logger.info('errors')

#----------------------------------------------------------------------------#
# Launch.
#----------------------------------------------------------------------------#

# Default port:
if __name__ == '__main__':
    app.run()

# Or specify port manually:
'''
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
'''
