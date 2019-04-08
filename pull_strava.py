import stravalib
from stravalib.client import Client
import ConfigParser
import argparse
import webbrowser
import pandas as pd

def pull_strava(activities):

    ## Strava API uses OAuth2, which requires users to manually allow permission, which generates
    ## a token only valid for a number of hours.

    ## get API client id and secret from config file

    config = ConfigParser.ConfigParser()
    config.read("credentials.cfg")
    client_id = config.get('credentials', 'client_id')
    client_secret = config.get('credentials', 'client_secret')

    client = Client()
    authorize_url = client.authorization_url(client_id=client_id, redirect_uri='http://localhost:8282/authorized')

    webbrowser.open_new_tab(authorize_url)

    code = raw_input('Enter Temporary Code: ')
    code = str(code)

    ## connect get temporary token from Strava API

    token_response = client.exchange_code_for_token(client_id=client_id, client_secret=client_secret, code=code)

    access_token = token_response['access_token']
    refresh_token = token_response['refresh_token']
    expires_at = token_response['expires_at']

    client.access_token = access_token
    # You must also store the refresh token to be used later on to obtain another valid access token 
    # in case the current is already expired
    client.refresh_token = refresh_token

    # An access_token is only valid for 6 hours, store expires_at somewhere and
    # check it before making an API call.
    client.token_expires_at = expires_at

    ## fields to scrape

    cols = ['id','name','start_date','distance','elapsed_time','moving_time',
            'average_speed','max_speed','average_cadence','average_watts',
            'average_heartrate','max_heartrate','calories','commute','has_heartrate',
            'total_elevation_gain','achievement_count']

    results = pd.DataFrame(columns=cols)

    print("Pulling " + activities + " activities since 1/1/2019")

    for activity in client.get_activities(after = "2019-01-01T00:00:00Z",  limit=activities):
            
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

    ## export results to csv

    print("Exporting results to csv file...")

    results.to_csv('results.csv', index=False, encoding='utf-8-sig')

    results = pd.read_csv('results.csv')
    results['distance'] = results['distance'].str.replace(' m', '')
    results.to_csv('results.csv', index=False, encoding='utf-8-sig')


#################

def pull_strava_cmd():
    # set up the parser/argument information with command line help
    parser= argparse.ArgumentParser(description="Pull & Save Strava Cycling Data")
    parser.add_argument('activities', help="Total number of activities to pull")

    args=parser.parse_args()

    pull_strava(args.activities)

    #estimate_truthiness()

#################

def main():
    pull_strava_cmd()

#################

if __name__=="__main__":
    main()

#################


