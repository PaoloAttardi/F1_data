import fastf1 as ff1
from fastf1 import plotting
from fastf1 import utils

from matplotlib import pyplot as plt
from matplotlib.pyplot import figure

import numpy as np
import pandas as pd
import os.path

trackStatus = {
    '1': 'Track clear',
    '2': 'Yellow flag',
    '3': 'unknown',
    '4': 'Safety Car',
    '5': 'Red Flag',
    '6': 'Virtual Safety',
    '7': 'Virtual Safety',
}

def DataTelemetry(driver_1, driver_2, quali):
    
    plot_title = f"{quali.event.year} {quali.event.EventName} - {quali.name} - {driver_1} VS {driver_2}"
    plot_filename = "static/image/" + plot_title.replace(" ", "") + ".png"
    if(os.path.exists(plot_filename)):
        return plot_filename

    # Laps can now be accessed through the .laps object coming from the session
    laps_driver_1 = quali.laps.pick_driver(driver_1)
    laps_driver_2 = quali.laps.pick_driver(driver_2)

    # Select the fastest lap
    fastest_driver_1 = laps_driver_1.pick_fastest()
    fastest_driver_2 = laps_driver_2.pick_fastest()

    # Retrieve the telemetry and add the distance column
    telemetry_driver_1 = fastest_driver_1.get_telemetry().add_distance()
    telemetry_driver_2 = fastest_driver_2.get_telemetry().add_distance()

    # Make sure whe know the team name for coloring
    team_driver_1 = fastest_driver_1['Team']
    team_driver_2 = fastest_driver_2['Team']

    delta_time, ref_tel, compare_tel = utils.delta_time(fastest_driver_1, fastest_driver_2)

    plot_size = [15, 15]
    plot_ratios = [1, 3, 2, 1, 1, 2, 1]

    # Make plot a bit bigger
    plt.rcParams['figure.figsize'] = plot_size

    # Create subplots with different sizes
    fig, ax = plt.subplots(7, gridspec_kw={'height_ratios': plot_ratios})

    # Set the plot title
    ax[0].title.set_text(plot_title)


    # Delta line
    ax[0].plot(ref_tel['Distance'], delta_time)
    ax[0].axhline(0)
    ax[0].set(ylabel=f"Gap to {driver_2} (s)")

    # Speed trace
    ax[1].plot(telemetry_driver_1['Distance'], telemetry_driver_1['Speed'], label=driver_1, color=ff1.plotting.driver_color(driver_1))
    ax[1].plot(telemetry_driver_2['Distance'], telemetry_driver_2['Speed'], label=driver_2, color=ff1.plotting.driver_color(driver_2))
    ax[1].set(ylabel='Speed')
    ax[1].legend(loc="lower right")

    # Throttle trace
    ax[2].plot(telemetry_driver_1['Distance'], telemetry_driver_1['Throttle'], label=driver_1, color=ff1.plotting.driver_color(driver_1))
    ax[2].plot(telemetry_driver_2['Distance'], telemetry_driver_2['Throttle'], label=driver_2, color=ff1.plotting.driver_color(driver_2))
    ax[2].set(ylabel='Throttle')

    # Brake trace
    ax[3].plot(telemetry_driver_1['Distance'], telemetry_driver_1['Brake'], label=driver_1, color=ff1.plotting.driver_color(driver_1))
    ax[3].plot(telemetry_driver_2['Distance'], telemetry_driver_2['Brake'], label=driver_2, color=ff1.plotting.driver_color(driver_2))
    ax[3].set(ylabel='Brake')

    # Gear trace
    ax[4].plot(telemetry_driver_1['Distance'], telemetry_driver_1['nGear'], label=driver_1, color=ff1.plotting.driver_color(driver_1))
    ax[4].plot(telemetry_driver_2['Distance'], telemetry_driver_2['nGear'], label=driver_2, color=ff1.plotting.driver_color(driver_2))
    ax[4].set(ylabel='Gear')

    # RPM trace
    ax[5].plot(telemetry_driver_1['Distance'], telemetry_driver_1['RPM'], label=driver_1, color=ff1.plotting.driver_color(driver_1))
    ax[5].plot(telemetry_driver_2['Distance'], telemetry_driver_2['RPM'], label=driver_2, color=ff1.plotting.driver_color(driver_2))
    ax[5].set(ylabel='RPM')

    # DRS trace
    ax[6].plot(telemetry_driver_1['Distance'], telemetry_driver_1['DRS'], label=driver_1, color=ff1.plotting.driver_color(driver_1))
    ax[6].plot(telemetry_driver_2['Distance'], telemetry_driver_2['DRS'], label=driver_2, color=ff1.plotting.driver_color(driver_2))
    ax[6].set(ylabel='DRS')
    ax[6].set(xlabel='Lap distance (meters)')


    # Hide x labels and tick labels for top plots and y ticks for right plots.
    for a in ax.flat:
        a.label_outer()
        
    # Store figure
    plt.savefig(plot_filename, dpi=300)
    return plot_filename
    # plt.show()

    # pd.DataFrame.to_csv(path_or_buf='F1_project/' + driver_1 + '_' + csv_name + '_Lap_time.csv', self=laps_driver_1)
    # pd.DataFrame.to_csv(path_or_buf='F1_project/' + driver_2 + '_' + csv_name + '_Lap_time.csv', self=laps_driver_2)
    # writeData(lapData=laps_driver_1, header=laps_driver_1.head(0).columns)

def RaceAnalisys(driver_1, driver_2, driver_3, driver_4, race):

    plot_title = f"{race.event.year} {race.event.EventName} - {race.name} - {driver_1} VS {driver_2} VS {driver_3} VS {driver_4}"
    plot_filename = "static/image/" + plot_title.replace(" ", "") + ".png"
    if(os.path.exists(plot_filename)):
        return plot_filename

    laps = race.load_laps()

    # Convert laptimes to seconds
    laps['LapTimeSeconds'] = laps['LapTime'].dt.total_seconds()

    # To get accurate laps only, we exclude in- and outlaps
    laps = laps.loc[(laps['PitOutTime'].isnull() & laps['PitInTime'].isnull())]

    # Also, we remove outliers since those don't represent the racepace,
    # using the Inter-Quartile Range (IQR) proximity rule
    q75, q25 = laps['LapTimeSeconds'].quantile(0.75), laps['LapTimeSeconds'].quantile(0.25)

    intr_qr = q75 - q25

    laptime_max = q75 + (1.5 * intr_qr) # IQR proximity rule: Max = q75 + 1,5 * IQR
    laptime_min = q25 - (1.5 * intr_qr) # IQR proximity rule: Min = q25 + 1,5 * IQR

    laps.loc[laps['LapTimeSeconds'] < laptime_min, 'LapTimeSeconds'] = np.nan
    laps.loc[laps['LapTimeSeconds'] > laptime_max, 'LapTimeSeconds'] = np.nan
    # To make sure we won't get any equally styled lines when comparing teammates
    visualized_teams = []

    # Make plot a bit bigger
    plt.rcParams['figure.figsize'] = [10, 10]

    # Create 2 subplots (1 for the boxplot, 1 for the lap-by-lap comparison)
    fig, ax = plt.subplots(3)

    drivers_to_visualize = [driver_1, driver_2, driver_3, driver_4]

    ##############################
    #
    # Boxplot for average racepace
    #
    ##############################
    xlab = []
    laptimes = [laps.pick_driver(x)['LapTimeSeconds'].dropna() for x in drivers_to_visualize]
    for d in range(len(drivers_to_visualize)):
        medians = np.mean(laptimes[d])
        medians = round(medians,2)
        xlab.append(drivers_to_visualize[d] + ' ' + str(medians))
        print(xlab)

    ax[0].boxplot(laptimes, labels=xlab)

    ax[0].set_title('Average racepace comparison')
    ax[0].set(ylabel = 'Laptime (s)')

    ##############################
    #
    # Lap-by-lap racepace comparison
    #
    ##############################
    for driver in drivers_to_visualize:
        driver_laps = laps.pick_driver(driver)[['LapNumber', 'LapTimeSeconds', 'Team']]
        
        # Select all the laps from that driver
        driver_laps = driver_laps.dropna()
        
        # Extract the team for coloring purploses
        team = pd.unique(driver_laps['Team'])[0]
        
        # X-coordinate is the lap number
        x = driver_laps['LapNumber']
        
        # Y-coordinate a smoothed line between all the laptimes
        poly = np.polyfit(driver_laps['LapNumber'], driver_laps['LapTimeSeconds'], 5)
        y_poly = np.poly1d(poly)(driver_laps['LapNumber'])
        
        # Make sure that two teammates don't get the same line style
        linestyle = '-' if team not in visualized_teams else ':'
        
        # Plot the data
        ax[1].plot(x, y_poly, label=driver, color=ff1.plotting.team_color(team), linestyle=linestyle)
        
        # Include scatterplot (individual laptimes)
        # y = driver_laps['LapTimeSeconds']
        # scatter_marker = 'o' if team not in visualized_teams else '^' 
        # ax[1].scatter(x, y, label=driver, color=ff1.plotting.team_color(team), marker=scatter_marker)
        
        # Append labels
        ax[1].set(ylabel = 'Laptime (s)')
        ax[1].set(xlabel = 'Lap')
        
        # Set title
        ax[1].set_title('Smoothed lap-by-lap racepace')

        # Generate legend
        ax[1].legend()
        
        # Add the team to the visualized teams variable so that the next time the linestyle will be different
        visualized_teams.append(team)

    # Add the strategy analisys to the plot
    driver_stints = laps[['Driver', 'Stint', 'Compound', 'LapNumber']].groupby(
    ['Driver', 'Stint', 'Compound']).count().reset_index()

    driver_stints = driver_stints.rename(columns={'LapNumber': 'StintLength'})

    driver_stints = driver_stints.sort_values(by=['Stint'])

    compound_colors = {
        'SOFT': '#FF3333',
        'MEDIUM': '#FFF200',
        'HARD': '#EBEBEB',
        'INTERMEDIATE': '#39B54A',
        'WET': '#00AEEF',
        'UNKNOWN': '#55FF55'
    }

    plt.rcParams["figure.figsize"] = [15, 10]
    plt.rcParams["figure.autolayout"] = True

    for driver in drivers_to_visualize:
        stints = driver_stints.loc[driver_stints['Driver'] == driver]
        
        previous_stint_end = 0
        for _, stint in stints.iterrows():
            plt.barh(
                [driver], 
                stint['StintLength'], 
                left=previous_stint_end, 
                color=compound_colors[stint.get('Compound')], 
                edgecolor = "black"
            )
            
            previous_stint_end = previous_stint_end + stint['StintLength']
            
    # Set title
    # plt.title(f'Race strategy')
            
    # Set x-label
    plt.xlabel('Lap')

    # Invert y-axis 
    plt.gca().invert_yaxis()

    # Remove frame from plot
    ax[2].spines['top'].set_visible(False)
    ax[2].spines['right'].set_visible(False)
    ax[2].spines['left'].set_visible(False)

    plt.savefig(plot_filename, dpi=300)
    return plot_filename
    
def DriversLap(drivers, event):
    lapsD = event.laps.pick_drivers(drivers)
    if len(drivers) == 2:
        lapsD.drop(['Time', 'DriverNumber', 'Sector1SessionTime', 'Sector2SessionTime', 'Sector3SessionTime',
        'SpeedI1', 'SpeedI2', 'SpeedFL', 'SpeedST', 'FreshTyre', 'LapStartTime', 'LapStartDate', 'IsAccurate', 'IsPersonalBest'], axis=1, inplace=True)
    else: lapsD.drop(['Time', 'DriverNumber', 'Sector1SessionTime', 'Sector2SessionTime', 'Sector3SessionTime',
        'SpeedI1', 'SpeedI2', 'SpeedFL', 'SpeedST', 'FreshTyre', 'LapStartTime', 'IsAccurate', 'IsPersonalBest'], axis=1, inplace=True)
    lapsD.rename(columns = {'Sector1Time':'Sector1','Sector2Time':'Sector2','Sector3Time':'Sector3'}, inplace=True)
    columns_name = ['Driver', 'Team', 'LapTime', 'LapNumber', 'Stint', 'PitOutTime', 'PitInTime', 'Sector1', 'Sector2', 'Sector3', 'Compound', 'TyreLife', 'TrackStatus']
    lapsD = lapsD.reindex(columns=columns_name)
    laps = lapsD.values.tolist()
    header = lapsD.columns.values
    for lap in laps:
        lap[2] = str(lap[2])[10:19]
        lap[5] = str(lap[5])[10:19]
        lap[6] = str(lap[6])[10:19]
        lap[7] = str(lap[7])[10:19]
        lap[8] = str(lap[8])[10:19]
        lap[9] = str(lap[9])[10:19]
        lap[12] = trackStatus[lap[12][0]]
    return header,laps