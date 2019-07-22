import stravalib
from stravalib.client import Client
import configparser
import argparse
import webbrowser
import pandas as pd
import numpy as np
import pdb

def pull_strava(activities):

    ## Strava API uses OAuth2, which requires users to manually allow permission, which generates
    ## a token only valid for a number of hours.

    ## get API client id and secret from config file

    config = configparser.ConfigParser()
    config.read("credentials.cfg")
    client_id = config.get('credentials', 'client_id')
    client_secret = config.get('credentials', 'client_secret')

    client = Client()
    authorize_url = client.authorization_url(client_id=client_id, redirect_uri='http://localhost:8282/authorized')

    ## getting token -- pretty manual process for now
    
    webbrowser.open_new_tab(authorize_url)

    code = input('Enter Temporary Code: ')
    code = str(code)

    ## authenticate using API credntials + token

    token_response = client.exchange_code_for_token(client_id=client_id, client_secret=client_secret, code=code)

    ## fields to scrape

    cols = ['id','name','start_date','distance','elapsed_time','moving_time',
            'average_speed','max_speed','average_cadence','average_watts',
            'average_heartrate','max_heartrate','calories','commute','has_heartrate',
            'total_elevation_gain','achievement_count']

    results = pd.DataFrame(columns=cols)

    print("Pulling " + activities + " activities since 1/1/2019")

    for activity in client.get_activities(after = "2019-01-01T00:00:00Z",  limit=int(activities)):
            
        id = activity.id
        name = activity.name
        start_date = activity.start_date
        distance = activity.distance
        elapsed_time = activity.elapsed_time.seconds
        moving_time = activity.moving_time.seconds
        average_speed = activity.average_speed.num
        max_speed = activity.max_speed.num
        average_cadence = activity.average_cadence
        average_watts = activity.average_watts
        average_heartrate = activity.average_heartrate
        max_heartrate = activity.max_heartrate
        calories = activity.calories
        commute = activity.commute
        has_heartrate = activity.has_heartrate
        total_elevation_gain = activity.total_elevation_gain.num
        achievement_count = activity.achievement_count

        data = pd.DataFrame(columns=cols)		

        data.loc[1] = [id,name,start_date,distance,elapsed_time,moving_time,
        average_speed,max_speed,average_cadence,average_watts,
        average_heartrate,max_heartrate,calories,commute,has_heartrate,
        total_elevation_gain,achievement_count]

        results = results.append(data)

    results = results.reset_index()

    ## freedom units!

    ## converting avg/max speeds from meters/sec to miles/hour

    results['average_speed'] = results.average_speed * 2.23694
    results['max_speed'] = results.max_speed * 2.23694

    ## converting meters to feet

    results['total_elevation_gain'] = results.total_elevation_gain * 3.28084

    ## converting meters to miles

    results['distance'] = results.distance * 0.000621371   

    ## timestamp

    results['date_pulled'] = pd.datetime.now().strftime("%m/%d/%Y %I:%M:%S %p ET")

    ## export results to csv

    print("Exporting results to csv file...")

    results.to_csv('results.csv', index=False, encoding='utf-8-sig')

    results = pd.read_csv('results.csv')
    results['distance'] = results['distance'].str.replace(' m', '')

    ## painmeter

    cols =['distance','moving_time','average_speed',
                            'max_speed','average_watts','average_heartrate',
                            'max_heartrate','total_elevation_gain']

    results.reset_index(inplace=True)                        

    commute = results[results['commute']].reset_index(drop=True)
    not_commute = results[~results['commute']].reset_index(drop=True)                     

    for col in cols:

        new_col = col + "_mean"

        # Make room for a new column
        commute[new_col] = np.nan
        not_commute[new_col] = np.nan

        # Fill the new column with values
        for i in commute.index + 1:
            if i == 1:
                commute[new_col].iloc[0] = commute[col].iloc[0]
            else:
                commute[new_col].iloc[i-1] = commute[col].rolling(window = i+1, min_periods=1).mean()[i-1]

        for i in not_commute.index + 1:
            if i == 1:
                not_commute[new_col].iloc[0] = not_commute[col].iloc[0]
            else:
                not_commute[new_col].iloc[i-1] = not_commute[col].rolling(window = i+1, min_periods=1).mean()[i-1]

    results = commute.append(not_commute)

##    avg_metrics = results[['commute','distance','moving_time','average_speed',
##    						'max_speed','average_watts','average_heartrate',
##    						'max_heartrate','total_elevation_gain']].groupby(['commute']).mean()

##    avg_metrics.columns = [str(col) + '_mean' for col in avg_metrics.columns]

##    results = results.merge(avg_metrics,how='inner',on='commute')

    cols = ['distance','moving_time','average_speed',
    						'max_speed','average_watts','average_heartrate',
    						'max_heartrate','total_elevation_gain']

    rel_effort_cols = []
    mean_cols = []

    for col in cols:

    	mean = col + "_mean"
    	effort = col + "_rel_effort"

    	try:
            results[effort] = pd.to_numeric(results[col]) / pd.to_numeric(results[mean])
            rel_effort_cols.append(effort)
            mean_cols.append(mean)
        
    	except:
            print('Error with calculation for',col)	

    results['painmeter'] = results[rel_effort_cols].mean(axis=1)

    ##results.drop([rel_effort_cols],axis=1,inplace=True)
    ##results.drop([mean_cols],axis=1,inplace=True)

    results.to_csv('results.csv', index=False, encoding='utf-8-sig')

#################

def pull_strava_cmd():
    # set up the parser/argument information with command line help
    parser= argparse.ArgumentParser(description="Pull & Save Strava Cycling Data")
    parser.add_argument('activities', help="Total number of activities to pull")

    args=parser.parse_args()

    pull_strava(args.activities)

#################

def main():
    pull_strava_cmd()

#################

if __name__=="__main__":
    main()

#################


