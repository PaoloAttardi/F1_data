from flask import Flask
from flask import render_template
import fastf1 as ff1
from fastf1 import events
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

@app.route("/<int:round>")
def getEvent(round):
    x = datetime.datetime.now()
    session = ff1.get_event(year=x.year,gp=round)
    print(session.get_race())
    return 'hello there!'

if __name__ == "__main__":
    app.run(host="127.0.0.1", port=8080, debug=True)