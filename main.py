from flask import Flask
from flask import render_template
from flask import request
import fastf1 as ff1
import datetime
import requests

ff1.Cache.enable_cache('cache')

app = Flask(__name__)

@app.route("/")
def getEventsList():
    x = datetime.datetime.now()
    session = ff1.get_event_schedule(x.year)
    session = session.values.tolist()
    c = requests.get('http://ergast.com/api/f1/current/constructorStandings.json')
    d = requests.get('http://ergast.com/api/f1/current/driverStandings.json')
    constructor_Standings = c.json()
    driver_Standings = d.json()
    return render_template('index.html', session=session, today=datetime.datetime.now(),
     constructor_Standings=constructor_Standings['MRData']['StandingsTable']["StandingsLists"][0]['ConstructorStandings'],
     driver_Standings=driver_Standings['MRData']['StandingsTable']["StandingsLists"][0]['DriverStandings'])

@app.route("/<int:round>/<string:session>", methods = ['GET', 'POST'])
def getEvent(round, session):
    x = datetime.datetime.now()
    event = ff1.get_session(x.year,round,session)
    event.load()
    result = event.results
    if(request.method == 'POST'):
        print(request.form['FirstDriver'])
        return render_template('dataAnalisys.html', drivers=event.drivers, result=result.values.tolist(), session_name = event.event.EventName,
    session_type = session)
    return render_template('dataView.html', drivers=event.drivers, result=result.values.tolist(), session_name = event.event.EventName,
    session_type = session)

if __name__ == "__main__":
    app.run(host="127.0.0.1", port=8080, debug=True)