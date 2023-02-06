import numpy as np

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

from flask import Flask, jsonify


#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(engine, reflect = True)

# Save reference to the table
Measurement = Base.classes.measurement
Station = Base.classes.station

#################################################
# Flask Setup
#################################################
app = Flask(__name__)

#################################################
# Flask Routes
#################################################

# Create a home page and list all available route
@app.route("/")
def welcome():
    """List all available api routes."""
    return (
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/startdate<br/>"
        f"(Please enter start date as YYYY-MM-DD)<br/>"
        f"/api/v1.0/startdate/enddate<br/>"
        f"(Please enter start date and end date as YYYY-MM-DD)<br/>"
        f"(Note: Please only enter the available date from 2010-01-01 to 2017-08-23)<br/>"
    )

# Create app route for precipitation
@app.route("/api/v1.0/precipitation")
def precipitation():
    # Create our session (link) from Python to the DB
    session = Session(engine)

    """Return a list of all date and precipitation"""
    # Query all date and precipitation
    results = session.query(Measurement.date, Measurement.prcp).all()

    session.close()

    # Create a dictionary from the row data and append to a list of all date and measurements
    all_prcp = []
    for date, prcp in results:
        prcp_dict= {}
        prcp_dict["date"] = date
        prcp_dict["prcp"] = prcp
        all_prcp.append(prcp_dict)

    return jsonify(all_prcp)


# Create app route for stations
@app.route("/api/v1.0/stations")
def stations():
    # Create our session (link) from Python to the DB
    session = Session(engine)

    """Return a list of all stations"""
    # Query all stations
    results = session.query(Station.name).filter(Measurement.station == Station.station).group_by(Station.station).all()

    session.close()

    # Convert list of tuples into normal list
    all_stations = list(np.ravel(results))

    return jsonify(all_stations)

# Create app route for temprature observations of the most active statrion for the previous year
@app.route("/api/v1.0/tobs")
def tobs():
    # Create our session (link) from Python to the DB
    session = Session(engine)

    """Return a list of all tempature observations for the previous year"""

    # Most active station
    most_active = session.query(Measurement.station,func.count(Measurement.date)).group_by(Measurement.station).\
                order_by(func.count(Measurement.date).desc()).first()

    # Import datetime 
    import datetime as dt
    from datetime import datetime

    # Query date
    most_recent= session.query(Measurement.date).order_by(Measurement.date.desc()).first()
    most_recent_date = datetime.strptime(most_recent[0], "%Y-%m-%d")
    query_date = most_recent_date - dt.timedelta(days = 365)
    
    # Query all required tobs of the most active station for the previous year
    results = session.query(Measurement.date, Measurement.tobs).filter(Measurement.date >=query_date).\
        filter(Measurement.station == most_active[0]).all()

    session.close()

    # Create a dictionary from the row data and append to a list of all date and temprature observations
    all_tobs = []
    for date, tob in results:
        tobs_dict= {}
        tobs_dict["date"] = date
        tobs_dict["tobs"] = tob
        all_tobs.append(tobs_dict)

    return jsonify(all_tobs)

# Create app route for /api/v1.0/<start> and /api/v1.0/<start>/<end>
@app.route("/api/v1.0/<start>")
def get_start_date(start):

    # Create our session (link) from Python to the DB
    session = Session(engine)

    """Return a list the minimum, the average and the maximum temperature for a specified start or start-end range"""

    # Query the min, max and avg temprature for the start date
    sel = [func.min(Measurement.tobs), func.max(Measurement.tobs), func.avg(Measurement.tobs)]
    results = session.query(*sel).filter(Measurement.date>= start).all()
    session.close()

        # Convert list of tuples into normal list
    needed_info = list(np.ravel(results))
    return jsonify(needed_info)
            
@app.route("/api/v1.0/<start>/<end>")
def get_start_end_date(start, end):
    # Create our session (link) from Python to the DB
    session = Session(engine)

    """Return a list the minimum, the average and the maximum temperature for a specified start or start-end range"""

    # Query the min, max and avg temprature for the start date and end date
    sel = [func.min(Measurement.tobs), func.max(Measurement.tobs), func.avg(Measurement.tobs)]
    results = session.query(*sel).filter(Measurement.date>= start).\
    filter(Measurement.date<=end).all()

    session.close()

        # Convert list of tuples into normal list
    needed_info = list(np.ravel(results))
    return jsonify(needed_info)

if __name__ == '__main__':
    app.run(debug=True)


