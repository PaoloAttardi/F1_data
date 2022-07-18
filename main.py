from flask import Flask
from flask import render_template
from flask import request
import fastf1 as ff1
import datetime
import requests

from analisys import DataTelemetry, RaceAnalisys

ff1.Cache.enable_cache('../cache')

driverName = {
    '1': 'VER',
    '3': 'RIC',
    '4': 'NOR',
    '5': 'VET',
    '6': 'LAT',
    '10': 'GAS',
    '11': 'PER',
    '14': 'ALO',
    '16': 'LEC',
    '18': 'STR',
    '20': 'MAG',
    '22': 'TSU',
    '23': 'ALB',
    '24': 'ZHO',
    '31': 'OCO',
    '44': 'HAM',
    '47': 'SCH',
    '55': 'SAI',
    '63': 'RUS',
    '77': 'BOT',
    '27': 'HUL',
    }

app = Flask(__name__)

@app.route("/")
def getEventsList():
    x = datetime.datetime.now()
    session = ff1.get_event_schedule(x.year, include_testing=False)
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
    d = event.drivers
    drivers = []
    result = event.results.values.tolist()
    for item in d:
        drivers.append(driverName[item])
    if(session != 'Qualifying'):
        for driver_result in result:
            driver_result[13] = str(event.laps.pick_driver(driver_result[2]).pick_fastest()['LapTime'])[10:19]
    else:
        for driver_result in result:
            driver_result[10] = str(driver_result[10])[10:19]
            driver_result[11] = str(driver_result[11])[10:19]
            driver_result[12] = str(driver_result[12])[10:19]
    if(request.method == 'POST'):
        firstDriver = request.form['FirstDriver']
        secondDriver = request.form['SecondDriver']
        typeOfAnalisys = request.form['Type']
        if(typeOfAnalisys == 'Telemetry'):
            file_name = DataTelemetry(firstDriver, secondDriver, event)
            return render_template('dataAnalisys.html', drivers=drivers, result=result, session_name = event.event.EventName,
                session_type = session, file_name=file_name)
        else:
            file_name = RaceAnalisys(firstDriver, secondDriver, event)
            return render_template('dataAnalisys.html', drivers=drivers, result=result, session_name = event.event.EventName,
                session_type = session, file_name=file_name)
    return render_template('dataView.html', drivers=drivers, result=result, session_name = event.event.EventName,
    session_type = session)

if __name__ == "__main__":
    # ff1.Cache.clear_cache('../cache')
    app.run(host="127.0.0.1", port=8080, debug=True)