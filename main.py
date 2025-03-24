from flask import Flask
from flask import render_template
from flask import request
from fastf1.ergast import Ergast
from analisys import DataTelemetry, RaceAnalisys, DriversLap

import fastf1 as ff1
import datetime

ff1.Cache.enable_cache('cache')
ergast = Ergast()

app = Flask(__name__)

@app.route("/")
def LoadHomePage():
    x = datetime.datetime.now()
    session = ff1.get_event_schedule(x.year, include_testing=True)
    session = session[['RoundNumber', 'Country', 'OfficialEventName', 'EventDate', 'EventName', 'Session1', 'Session1Date',
                        'Session2', 'Session2Date', 'Session3', 'Session3Date', 'Session4', 'Session4Date', 'Session5', 'Session5Date']]
    constructor_Standings = ergast.get_constructor_standings(season=x.year,result_type='raw')
    driver_Standings = ergast.get_driver_standings(season=x.year,result_type='raw')
    return render_template('home.html', session=session, today=datetime.datetime.now(), year=x.year,
        constructor_Standings=constructor_Standings[0]['ConstructorStandings'], driver_Standings=driver_Standings[0]['DriverStandings'])

@app.route("/Qualify/<int:round>/<string:session>")
def getQualiyingEvent(round, session):
    x = datetime.datetime.now()
    event = ff1.get_session(x.year,round,session)
    event.load()
    drivers = {}
    # change lap time format for Q1, Q2, Q3
    result = event.results[['Position','FullName','TeamName','Q1','Q2','Q3','Abbreviation','DriverNumber']]
    result[["Q1", "Q2", "Q3"]] = result[["Q1", "Q2", "Q3"]].astype(str)
    for idx in range(len(result)):
        drivers[result['DriverNumber'].iloc[idx]] = result['Abbreviation'].iloc[idx]
        result.loc[result['DriverNumber'].iloc[idx], 'Q1'] = result['Q1'].iloc[idx][10:19]
        result.loc[result['DriverNumber'].iloc[idx], 'Q2'] = result['Q2'].iloc[idx][10:19]
        result.loc[result['DriverNumber'].iloc[idx], 'Q3'] = result['Q3'].iloc[idx][10:19]
            
    return render_template('qualyResults.html', drivers=drivers, result=result.values.tolist(), session_name = event.event.EventName,
        session_type = session)

@app.route("/Race/<int:round>/<string:session>")
def GetRaceEvent(round, session):
    x = datetime.datetime.now()
    event = ff1.get_session(x.year,round,session)
    event.load()
    drivers = {}
    result = event.results[['Position','FullName','GridPosition','TeamName','Points','Abbreviation','DriverNumber']]
    result = result.copy()
    result.loc[:, 'LapTime'] = 'No Recorded Time'
    # get F.L. for every driver
    for idx in range(len(result)):
        drivers[result['DriverNumber'].iloc[idx]] = result['Abbreviation'].iloc[idx]
        if event.laps.pick_drivers(result['Abbreviation'].iloc[idx]).pick_fastest() is not None: 
            result.loc[result['DriverNumber'].iloc[idx], 'LapTime'] = str(event.laps.pick_drivers(result['Abbreviation'].iloc[idx]).pick_fastest()['LapTime'])[10:19]
    # Get race analysis
    file_name = RaceAnalisys(event, drivers)
    
    return render_template('raceResults.html', drivers=drivers, result=result.values.tolist(), session_name = event.event.EventName,
        session_type = session, file_name=file_name)

@app.route("/Practice/<int:round>/<string:session>")
def GetPracticeEvent(round, session):
    x = datetime.datetime.now()
    if round == 0: 
        event = ff1.get_testing_session(x.year,1,int(session.split()[-1])) # hardcoded test_number = 1, will break if multiple tests take places in the same year
    else: event = ff1.get_session(x.year,round,session)
    event.load()
    drivers = {}
    result = event.results[['Position','FullName','GridPosition','TeamName','Points','Abbreviation','DriverNumber']]
    result = result.copy()
    result.loc[:, 'LapTime'] = 'No Recorded Time'
    # get F.L. for every driver
    for idx in range(len(result)):
        drivers[result['DriverNumber'].iloc[idx]] = result['Abbreviation'].iloc[idx]
        if event.laps.pick_drivers(result['Abbreviation'].iloc[idx]).pick_fastest() is not None: 
            result.loc[result['DriverNumber'].iloc[idx], 'LapTime'] = str(event.laps.pick_drivers(result['Abbreviation'].iloc[idx]).pick_fastest()['LapTime'])[10:19]
    if result['Position'].isna().all(): 
        result.sort_values(by='LapTime', ignore_index=True, inplace=True) # need to be sorted for test events
        result.loc[:,'Position'] = result.index + 1
    return render_template('practiceResults.html', drivers=drivers, result=result.values.tolist(), session_name = event.event.EventName,
    session_type = session)

@app.route("/<int:round>/<string:session>/<string:drivers>")
def RacePracticeAnalisys(round, session):
    event, drivers, result = None
    firstDriver = request.form['FirstDriver']
    secondDriver = request.form['SecondDriver']
    typeOfAnalisys = request.form['Type']
    if(typeOfAnalisys == 'Telemetry'):
        file_name = DataTelemetry(firstDriver, secondDriver, event)
        header, laps = DriversLap([firstDriver, secondDriver], event)
        return render_template('dataAnalisys.html', drivers=drivers, result=result, session_name = event.event.EventName,
            session_type = session, file_name=file_name, header=header, laps=laps)
    else:
        thirdDriver = request.form['ThirdDriver']
        fourthDriver = request.form['FourthDriver']
        file_name = RaceAnalisys(firstDriver, secondDriver, thirdDriver, fourthDriver, event)
        header, laps = DriversLap([firstDriver, secondDriver, thirdDriver, fourthDriver], event)
        return render_template('dataAnalisys.html', drivers=drivers, result=result, session_name = event.event.EventName,
            session_type = session, file_name=file_name, header=header, laps=laps)
    pass

if __name__ == "__main__":
    ff1.Cache.clear_cache('cache')
    app.run(host="0.0.0.0", port=80, debug=True)