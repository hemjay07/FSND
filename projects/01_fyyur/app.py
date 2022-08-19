#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#

import json
import dateutil.parser
import babel
from flask import Flask, render_template, request, Response, flash, redirect, url_for
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
import logging
from logging import Formatter, FileHandler
from flask_wtf import Form
from forms import *
from flask_migrate import Migrate
from datetime import datetime
#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config')
db = SQLAlchemy(app)
# TODO: connect to a local postgresql database
app.config['SQLALCHEMY_DATABASE_URI'] ='postgresql://postgres@localhost:5432/fyyur'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = 'False'

migrate = Migrate(app, db)

print('afhafliag')

#----------------------------------------------------------------------------#
# Models.
#----------------------------------------------------------------------------#

class Venue(db.Model):
    __tablename__ = 'Venue'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    address = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))
    website_link = db.Column(db.String(120))
    genres = db.Column(db.String(120))
    shows = db.relationship('Show', backref='Venue')
    seeking_talent= db.Column(db.Boolean) 
    seeking_description= db.Column(db.String())


class Artist(db.Model):
    __tablename__ = 'Artist'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    genres = db.Column(db.String(120))
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))
    seeking_venue = db.Column(db.Boolean)
    seeking_description = db.Column(db.String(500))
    website= db.Column(db.String(500))
    shows = db.relationship('Show', backref='Artist')


class Show(db.Model):
  __tablename__ = "Show"

  id = db.Column(db.Integer, primary_key=True, nullable=False)
  start_time = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

  artist_id = db.Column(db.Integer, db.ForeignKey('Artist.id'), nullable=False)
  venue_id = db.Column(db.Integer, db.ForeignKey('Venue.id'), nullable=False)
# TODO Implement Show and Artist models, and complete all model relationships and properties, as a database migration.


  
  

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
#  ----------------------------------------------------------------
#  ----------------------------------------------------------------

@app.route('/venues')
def venues():
  data=[]

  # get a unique city and state combo using set 
  foo = Venue.query.with_entities(Venue.city,Venue.state).all()
  bar= set(foo)


  # append each combo to "data" alongside venue which will be derived later
  for baz in bar:
    venues =[]
 

    # for each city,state combo, query the database and get the venues that qualify(venues with that state and city)
    yo = Venue.query.filter(Venue.city==baz[0], Venue.state==baz[1]).all()
    # print("yo:", yo)

    # for each of them
    # 1.create an object with attributes od id, name and num_upcoming_shows
    # 2.append the object created to the venues list
  
    for venue in yo:
      bunt={
        "id": venue.id,
      "name": venue.name
      }
      venues.append(bunt)


    subdata= {
    "city": baz[0],
    "state": baz[1],

    "venues": venues
    }
    data.append(subdata)
  
  return render_template('pages/venues.html', areas=data)


#  ----------------------------------------------------------------
  # Search venues
#  ----------------------------------------------------------------
@app.route('/venues/search', methods=['POST'])
def search_venues():
    
  search_term = request.form.get('search_term')
  searched_venues= Venue.query.filter(Venue.name.ilike('%'+search_term+'%')).all()
  data=[]
  count=0

  for venue in searched_venues:
    num_upcoming_shows = len(Show.query.filter(Show.venue_id==venue.id).all())

    subdata={
      "id": venue.id,
      "name": venue.name,
      "num_upcoming_shows": 0,
    }
    count+=1
    data.append(subdata)

  response={
    "count": count,
    "data": data
  }
 
  return render_template('pages/search_venues.html', results=response, search_term=request.form.get('search_term', ''))



#  ----------------------------------------------------------------
  # Show venues
#  ----------------------------------------------------------------
@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
 
  data_set=[]
  venues= Venue.query.all()

  for venue in venues:

    # past_shows
    past_shows= []
    pshows = Show.query.filter(Show.venue_id==venue.id).filter(Show.start_time<datetime.now()).all()
    for shows in pshows:
      artist_name = Artist.query.filter(Artist.id==shows.artist_id).first().name
      print(artist_name)
      artist_image_link=Artist.query.filter(Artist.id==shows.artist_id).first().image_link

      sobject={
        "artist_id": shows.artist_id,
        "artist_name": artist_name,
        "artist_image_link": artist_image_link,
        "start_time": shows.start_time.strftime("%m/%d/%Y, %H:%M:%S")

      }
      past_shows.append(sobject)


      # upcoming_shows
    upcoming_shows= []
    ushows = Show.query.filter(Show.venue_id==venue.id).filter(Show.start_time>datetime.now()).all()
     
    for shows in ushows:
      artist_name = Artist.query.filter(Artist.id==shows.artist_id).first().name
      artist_image_link=Artist.query.filter(Artist.id==shows.artist_id).first().image_link

      print(shows.start_time,"---------" ,shows.start_time.strftime("%m/%d/%Y, %H:%M:%S"))

      sobject={
        "artist_id": shows.artist_id,
        "artist_name": artist_name,
        "artist_image_link": artist_image_link,
        "start_time" : shows.start_time.strftime("%m/%d/%Y, %H:%M:%S")
      

      }
      upcoming_shows.append(sobject)
    

    if venue.genres:
      genres= venue.genres.split(",")
    else:
      genres=""

    # create the data using the information from the current venue
    data={
      "id": venue.id,
      "name": venue.name,
      "address": venue.address,
      "city": venue.city,
      "state": venue.state,
      "phone": venue.phone,
      "genres": genres,
      "website": venue.website_link,
      "facebook_link": venue.facebook_link,
      "seeking_talent": venue.seeking_talent,
      "seeking_description": venue.seeking_description,
      "image_link": venue.image_link,
      "past_shows": past_shows,
      "upcoming_shows": upcoming_shows,
      "past_shows_count": len(past_shows),
      "upcoming_shows_count": len(upcoming_shows),
    }

    data_set.append(data)
  
  
  
  
  data = list(filter(lambda d: d['id'] == venue_id, data_set))[0]
  return render_template('pages/show_venue.html', venue=data)


#  ----------------------------------------------------------------
  # Create venues
#  ----------------------------------------------------------------
@app.route('/venues/create', methods=['GET'])
def create_venue_form():
  form = VenueForm()
  return render_template('forms/new_venue.html', form=form)

@app.route('/venues/create', methods=['POST'])
def create_venue_submission():


  form = VenueForm(request.form)
  if form.validate():
    
    try:

      venue = Venue(
        name = form.name.data,
        city = form.city.data,
        state= form.state.data,
        phone= form.phone.data,
        genres= ",".join(form.genres.data),
        facebook_link= form.facebook_link.data,
        seeking_description= form.seeking_description.data,
        website_link= form.website_link.data,
        address=form.address.data,
        image_link= form.image_link.data,
        seeking_talent = form.seeking_talent.data,
      )
        
      db.session.add(venue)
      db.session.commit()
      # on successful db insert, flash success
      flash('Venue ' + venue.name + ' was successfully listed!') 

    except:
      db.session.rollback()
      # TODO: on unsuccessful db insert, flash an error instead.
      flash('An error occurred. Venue ' + venue.name + ' could not be listed.')

    finally:
      db.session.close()
  else:
    flash('An error occurred. Venue could not be listed.')

  return render_template('pages/home.html')





#  ----------------------------------------------------------------
  # Delete venues
#  ----------------------------------------------------------------
@app.route('/venues/<venue_id>/delete', methods=['GET'])
def delete_venue(venue_id):
  
  try:
    venue = Venue.query.get(venue_id)
    db.session.delete(venue)
    db.session.commit()
    flash("Venue " + venue.name+ " was deleted successfully!")
  except:
      db.session.rollback()
      flash("Venue was not deleted successfully.")
  finally:
    db.session.close()
    return redirect(url_for("index"))


#  ----------------------------------------------------------------
  # Edit  venue
#  ----------------------------------------------------------------
@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
  form = VenueForm()
  # print (venue_id,'++++++')



  current_venue= Venue.query.filter(Venue.id==venue_id).first()
  venue={
    "id": current_venue.id,
    "name": current_venue.name,
    "genres": current_venue.genres.split(","),
    "address": current_venue.address,
    "city": current_venue.city,
    "state": current_venue.state,
    "phone": current_venue.phone,
    "website": current_venue.website_link,
    "facebook_link": current_venue.facebook_link,
    "seeking_talent": current_venue.seeking_talent,
    "seeking_description": current_venue.seeking_description,
    "image_link": current_venue.image_link
  }
  
  return render_template('forms/edit_venue.html', form=form, venue=venue)

@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
  form = VenueForm(request.form)
  if form.validate():

    try:
      venue=Venue.query.get(venue_id)
      form = VenueForm(request.form)

      venue.name = form.name.data
      venue.city = form.city.data
      venue.state= form.state.data
      venue.phone= form.phone.data
      venue.genres= ",".join(form.genres.data)

      venue.facebook_link= form.facebook_link.data
      venue.seeking_description= form.seeking_description.data
      venue.website_link= form.website_link.data
      venue.address=form.address.data
      venue.image_link= form.image_link.data
      venue.seeking_talent = form.seeking_talent.data

    

        
      db.session.commit()
      # on successful db insert, flash success
      flash('Venue ' + venue.name + ' was successfully updated!') 

    except:
      db.session.rollback()
      flash('An error occurred. Venue ' + venue.name + ' could not be updated.')

    finally:
      db.session.close()
  else:
    flash('An error occurred. Venue could not be updated.')


  return redirect(url_for('show_venue', venue_id=venue_id))






#  Artists
#  ----------------------------------------------------------------
#  ----------------------------------------------------------------
#  ----------------------------------------------------------------
@app.route('/artists')
def artists():
  # TODO: replace with real data returned from querying the database

  data=[]
  artists = Artist.query.with_entities(Artist.id, Artist.name).all()
  print('artist:', artists)
  for artist in artists:
    data.append(artist)

  return render_template('pages/artists.html', artists=data)


#  ----------------------------------------------------------------
  # Search  artist
#  ----------------------------------------------------------------
@app.route('/artists/search', methods=['POST'])
def search_artists():
  
  search_term = request.form.get('search_term')
  searched_artist= Artist.query.filter(Artist.name.ilike('%'+search_term+'%')).all()
  data=[]
  count=0


  for artist in searched_artist:
    num_upcoming_shows = len(Show.query.filter(Show.artist_id==artist.id).all())

    subdata={
      "id": artist.id,
      "name": artist.name,
      "num_upcoming_shows": num_upcoming_shows,
    }
    count+=1
    data.append(subdata)

  response={
    "count": count,
    "data": data
  }
 
  return render_template('pages/search_artists.html', results=response, search_term=request.form.get('search_term', ''))


#  ----------------------------------------------------------------
  # Show  artist
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):

  data_set=[]
  artists= Artist.query.all()
  for artist in artists:

    # past_shows
    past_shows= []
    pshows = Show.query.filter(Show.artist_id==artist.id).filter(datetime.now()>Show.start_time ).all()
    for shows in pshows:
      venue_name = Venue.query.filter(Venue.id==shows.venue_id).first().name
      # print(venue)
      venue_image_link=Venue.query.filter(Venue.id==shows.venue_id).first().image_link

      sobject={
        "venue_id": shows.venue_id,
        "venue_name": venue_name,
        "venue_image_link": venue_image_link,
        "start_time": shows.start_time.strftime("%m/%d/%Y, %H:%M:%S")
      

      }
      past_shows.append(sobject)


    # upcoming_shows
    upcoming_shows= []
    ushows = Show.query.filter(Show.artist_id==artist.id).filter(datetime.now()<Show.start_time).all()
    for shows in ushows:
      venue_name = Venue.query.filter(Venue.id==shows.venue_id).first().name
      # print(venue)
      venue_image_link=Venue.query.filter(Venue.id==shows.venue_id).first().image_link

      sobject={
        "venue_id": shows.venue_id,
        "venue_name": venue_name,
        "venue_image_link": venue_image_link,
        "start_time": shows.start_time.strftime("%m/%d/%Y, %H:%M:%S")
      

      }
      upcoming_shows.append(sobject)
        
   
    if artist.genres:
      genres= artist.genres.split(",")
    else:
      genres=""


    data={
      "id": artist.id,
      "name": artist.name,
      "city": artist.city,
      "state": artist.state,
      "phone": artist.phone,
      "website": artist.website,
      "genres":genres,
      # "genres": genres,
      "facebook_link": artist.facebook_link,
      "seeking_venue": artist.seeking_venue,
      "seeking_description": artist.seeking_description,
      "image_link": artist.image_link,
      "facebook_link": artist.facebook_link,
      "past_shows": past_shows,
      "upcoming_shows": upcoming_shows,
      "past_shows_count": len(past_shows),
      "upcoming_shows_count": len(upcoming_shows),
    }
   
    data_set.append(data)
  data = list(filter(lambda d: d['id'] == artist_id, data_set))[0]
  return render_template('pages/show_artist.html', artist=data)






#  ----------------------------------------------------------------
  # Edit  artist
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
  form = ArtistForm()

  current_artist=Artist.query.filter(Artist.id==artist_id).first()

  artist={
    "id": current_artist.id,
    "name": current_artist.name,
    "genres": current_artist.genres.split(","),
    "city": current_artist.city,
    "state": current_artist.state,
    "phone": current_artist.phone,
    "website": current_artist.website,
    "facebook_link": current_artist.facebook_link,
    "seeking_venue": current_artist.seeking_venue,
    "seeking_description": current_artist.seeking_description,
    "image_link": current_artist.image_link
  }
  
  return render_template('forms/edit_artist.html', form=form, artist=artist)

@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
  form = ArtistForm(request.form)
  if form.validate():
    try:
      artist=Artist.query.get(artist_id)
      form = ArtistForm(request.form)


      artist.name = form.name.data
      artist.city = form.city.data
      artist.state= form.state.data
      artist.genres=",".join(form.genres.data)
      artist.phone= form.phone.data
      artist.facebook_link= form.facebook_link.data
      artist.seeking_description= form.seeking_description.data
      artist.website_link= form.website_link.data
      artist.image_link= form.image_link.data
      artist.seeking_venue = form.seeking_venue.data

      print(artist.genres,artist.seeking_venue)
        


        
      db.session.commit()
      # on successful db insert, flash success
      flash('Artist ' + artist.name + ' was successfully updated!') 

    except:
      db.session.rollback()
      flash('An error occurred. Artist ' + artist.name + ' could not be updated.')

    finally:
      db.session.close()

  else:
    flash('An error occurred. Artist could not be updated.')
  
  return redirect(url_for('show_artist', artist_id=artist_id))






#  ----------------------------------------------------------------
  # Create  artist
#  ----------------------------------------------------------------

@app.route('/artists/create', methods=['GET'])
def create_artist_form():
  form = ArtistForm()
  return render_template('forms/new_artist.html', form=form)

@app.route('/artists/create', methods=['POST'])
def create_artist_submission():
  form = ArtistForm(request.form)
  if form.validate():
    try:
      new_artist = Artist(
          name=form.name.data,
          city=form.city.data,
          state=form.state.data,
          phone=form.phone.data,
          genres=",".join(form.genres.data),
          image_link=form.image_link.data,
          facebook_link=form.facebook_link.data,
          website=form.website_link.data,
          seeking_venue=form.seeking_venue.data,
          seeking_description=form.seeking_description.data,
      )
      print('________+++',new_artist.seeking_venue,new_artist.genres,'++++++++')
      db.session.add(new_artist)
      db.session.commit()
      flash("Artist " + new_artist.name + " was successfully listed!")
    except Exception:
        db.session.rollback()
        flash('An error occurred. Artist ' + new_artist.name + ' could not be listed.')

    finally:
      db.session.close()
  else:
    flash('An error occurred. Artist could not be listed.')

  return render_template('pages/home.html')






#  Shows
#  ----------------------------------------------------------------
#  ----------------------------------------------------------------
#  ----------------------------------------------------------------
@app.route('/shows')
def shows():
  
  data=[]
  shows = Show.query.all()
  for show in shows:
    venue_name=Venue.query.with_entities(Venue.name).filter(Venue.id==show.venue_id).first()

    artist_name=Artist.query.with_entities(Artist.name).filter(Artist.id==show.artist_id).first()

    artist_image_link=Artist.query.with_entities(Artist.image_link).filter(Artist.id==show.artist_id).first()

    info={
    "venue_id": show.venue_id,
    "venue_name": venue_name,
    "artist_id": show.artist_id,
    "artist_name": artist_name,
    "artist_image_link": artist_image_link[0],
    "start_time": show.start_time.strftime("%m/%d/%Y, %H:%M:%S")
    }
    data.append(info)
 
  return render_template('pages/shows.html', shows=data)


 
#  ----------------------------------------------------------------
  # Create  show
#  ----------------------------------------------------------------
@app.route('/shows/create')
def create_shows():
  # renders form. do not touch.
  form = ShowForm()
  return render_template('forms/new_show.html', form=form)

@app.route('/shows/create', methods=['POST'])
def create_show_submission():
  form = ShowForm(request.form)

  if form.validate():
    try:
      show = Show()

      show.artist_id = form.artist_id.data
      show.venue_id = form.venue_id.data
      show.start_time = form.start_time.data
      db.session.add(show)
      db.session.commit()
      flash('Show was successfully listed!')

    
    except:
      db.session.rollback()
      flash('An error occurred. Show could not be listed.')


    finally:
      db.session.close()
  else:
      flash('An error occurred. Show could not be listed.')

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



