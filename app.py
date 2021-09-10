from os import stat
import numpy as np

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func
from scipy import stats

from flask import Flask, jsonify


engine = create_engine(f"sqlite:///resources/hawaii.sqlite")

Base = automap_base()

Base.prepare(engine, reflect=True)

Measurement = Base.classes.measurement
Station = Base.classes.station


app = Flask(__name__)



@app.route('/')
def welcome():
    """List of all available api routes."""
    return(
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"<br/>custom date ranges below:<br/>"
        f"(2010-01-01 to 2017-08-23)<br/><br/>"
        f"/api/v1.0/start-date<br/>"
        f"/api/v1.0/start-date/end-date"
    )

@app.route("/api/v1.0/precipitation")
def precipitation():
    # Create our session (link) from Python to the DB
    session = Session(engine)

    """Convert the query results to a dictionary using date as the key and prcp as the value."""
    # Query precipitation
    results = session.query(Measurement.date, Measurement.prcp).all()

    session.close()

    # Create a dictionary from the row data and append to a list
    prcp_list = []
    for date, prcp in results:
        prcp_dict = {}
        prcp_dict["date"] = date
        prcp_dict["precipitation"] = prcp
        prcp_list.append(prcp_dict)
    return jsonify(prcp_list)


@app.route("/api/v1.0/stations")
def stations():
    # Create our session (link) from Python to the DB
    session = Session(engine)

    """Return a JSON list of stations from the dataset."""
    # Query all passengers
    results = session.query(Measurement.station).distinct().all()

    session.close()

    return jsonify(results)

@app.route("/api/v1.0/tobs")
def tobs():
    # Create our session (link) from Python to the DB
    session = Session(engine)

    """Return a JSON list of temperature observations (TOBS) for the previous year."""
    # Query all passengers
    results = session.query(Measurement.date, Measurement.tobs).\
                filter(Measurement.station == 'USC00519281').\
                filter(Measurement.date >= '2016-08-23').\
                order_by(Measurement.date).all()

    session.close()

    return jsonify(results)


@app.route("/api/v1.0/<start>")
def startdate(start):
    # Create our session (link) from Python to the DB
    session = Session(engine)

    """When given the start only, calculate TMIN, TAVG, and TMAX for all dates greater than and equal to the start date."""
    # Query range based on input start date

    rmin = session.query(func.min(Measurement.tobs),Measurement.station,Measurement.date).\
                    filter(Measurement.date >= start).all()
    
    rmax = session.query(func.max(Measurement.tobs),Measurement.station,Measurement.date).\
                    filter(Measurement.date >= start).all()

    ravg = session.query(func.avg(Measurement.tobs),Measurement.station,Measurement.date).\
                    filter(Measurement.date >= start).all()

    session.close()

    return jsonify(rmin, rmax, ravg)





@app.route("/api/v1.0/<start>/<end>")
def start_end(start,end):
    # Create our session (link) from Python to the DB
    session = Session(engine)

    """When given the start and end date, calculate TMIN, TAVG, and TMAX for all dates in the range."""
    # Query range based on input start date and end date

    rmin = session.query(func.min(Measurement.tobs),Measurement.station,Measurement.date).\
                    filter(Measurement.date >= start).\
                    filter(Measurement.date <= end).all()
    
    rmax = session.query(func.max(Measurement.tobs),Measurement.station,Measurement.date).\
                    filter(Measurement.date >= start).\
                    filter(Measurement.date <= end).all()

    ravg = session.query(func.avg(Measurement.tobs),Measurement.station,Measurement.date).\
                    filter(Measurement.date >= start).\
                    filter(Measurement.date <= end).all()


    session.close()


    # return jsonify(rmin)
    return jsonify(rmin, rmax, ravg)


if __name__ == '__main__':
    app.run(debug=True)
