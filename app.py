import numpy as np
import datetime as dt
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func
from flask import Flask, jsonify

#################################################
# Database Setup
#################################################
# Set Database Connection
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# Reflect an existing database into a new model
Base = automap_base()

# Reflect the tables
Base.prepare(engine, reflect=True)

# Save references to each table
Measurement = Base.classes.measurement
Station = Base.classes.station

#################################################
# Flask Setup
#################################################
app = Flask(__name__)

#################################################
# Flask Routes
#################################################

@app.route("/")
def homepage():
    return (
        f"Welcome to the Surf's Up API!<br/>"
        f"Available Routes:<br/><br/>"
        f"/api/v1.0/precipitation<br/><br/>"
        f"/api/v1.0/stations<br/><br/>"
        f"/api/v1.0/tobs<br/><br/>"
        f"/api/v1.0/<start><br/><br/>"
        f"/api/v1.0/<start>/<end><br/><br/>"
    )

@app.route("/api/v1.0/precipitation")
def precipitation():

    # Create our session (link) from Python to the DB
    session = Session(engine)

    # Find latest date in measurement table
    latest_date = (session.query(Measurement.date)
                     .order_by(Measurement.date.desc())
                     .first())

    # Extract string from query object
    latest_date = list(np.ravel(latest_date))[0]

    # Convert date string to datetime object
    latest_date = dt.datetime.strptime(latest_date, '%Y-%m-%d')

    # Extract year, month, and day as integers
    latest_year = int(dt.datetime.strftime(latest_date, '%Y'))
    latest_month = int(dt.datetime.strftime(latest_date, '%m'))
    latest_day = int(dt.datetime.strftime(latest_date, '%d'))

    # Calculate one year before latest date
    year_before_date = dt.date(latest_year, latest_month, latest_day) - dt.timedelta(days=365)

    # Query for precipitation data from Aug. 23, 2016 - Aug. 23, 2017
    results = (session.query(Measurement.date, Measurement.prcp)
                  .filter(Measurement.date >= year_before_date)
                  .order_by(Measurement.date)
                  .all())

    session.close()

    # Convert the query results to a dictionary using date as the key and prcp as the value.
    Prcp_Data = []
    for date, prcp in results:
        prcp_dict = {}
        prcp_dict["date"] = date
        prcp_dict["prcp"] = prcp
        Prcp_Data.append(prcp_dict)

    return jsonify(Prcp_Data)


@app.route("/api/v1.0/stations")
def station():
    # Create our session (link) from Python to the DB
    session = Session(engine)

    # Count stations in the station table
    results = session.query(Station.name).all()

    session.close()

    # Convert list of tuples into normal list
    stations = list(np.ravel(results))

    return jsonify(stations)


@app.route("/api/v1.0/tobs")
def tobs():
    # Create our session (link) from Python to the DB
    session = Session(engine)

    # Find latest date in measurement table
    latest_date = (session.query(Measurement.date)
                     .order_by(Measurement.date.desc())
                     .first())

    # Extract string from query object
    latest_date = list(np.ravel(latest_date))[0]

    # Convert date string to datetime object
    latest_date = dt.datetime.strptime(latest_date, '%Y-%m-%d')

    # Extract year, month, and day as integers
    latest_year = int(dt.datetime.strftime(latest_date, '%Y'))
    latest_month = int(dt.datetime.strftime(latest_date, '%m'))
    latest_day = int(dt.datetime.strftime(latest_date, '%d'))

    # Calculate one year before latest date
    year_before_date = dt.date(latest_year, latest_month, latest_day) - dt.timedelta(days=365)

    # Last 12 months for station_id = 'USC00519281'
    station_id = 'USC00519281'

    results = (session.query(Measurement.date, Measurement.tobs)
                  .filter(Measurement.date >= year_before_date)
                  .filter(Measurement.station == station_id)
                  .order_by(Measurement.date)
                  .all())

    session.close()

    # Convert list of tuples into normal list
    tobs = list(np.ravel(results))

    return jsonify(tobs)

# IN PROGRESS
@app.route("/api/v1.0/<start> ")
def start(startDate):
    # Create our session (link) from Python to the DB
    session = Session(engine)
    
    query = [Measurement.date, func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)]

    results =  (session.query(*query)
                       .filter(func.strftime("%Y-%m-%d", Measurement.date) >= startDate)
                       .group_by(Measurement.date)
                       .all())
    
    session.close()

    dates = []                       
    for data in results:
        date_dict = {}
        date_dict["Date"] = data[0]
        date_dict["Min Temp"] = data[1]
        date_dict["Avg Temp"] = data[2]
        date_dict["Max Temp"] = data[3]
        dates.append(date_dict)

    return jsonify(dates)

#IN PROGRESS   
@app.route("/api/v1.0/<start>/<end>")
def startend(start, end):
    # Create our session (link) from Python to the DB
    session = Session(engine)


    session.close()    


if __name__ == '__main__':
    app.run(debug=True)