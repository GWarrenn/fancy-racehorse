import stravalib
from stravalib.client import Client
from stravalib.util import limiter
import configparser
import argparse
import webbrowser
import pandas as pd
import numpy as np
import time
import pdb
import io
from datetime import datetime

def authenticate():

    ## Strava API uses OAuth2, which requires users to manually allow permission, which generates
    ## a token only valid for a number of hours.

    ## get API client id and secret from config file

    config = configparser.ConfigParser()
    config.read("credentials.cfg")
    client_id = config.get('credentials', 'client_id')
    client_secret = config.get('credentials', 'client_secret')

    client = Client(rate_limiter=limiter.DefaultRateLimiter())
    scope = ['read_all', 'profile:read_all', 'activity:read_all']
    authorize_url = client.authorization_url(client_id=client_id, redirect_uri='http://localhost:8282/authorized',scope=scope)

    ## getting token -- pretty manual process for now
    
    webbrowser.open_new_tab(authorize_url)

    code = input('Enter Temporary Code: ')
    code = str(code)

    ## authenticate using API credntials + token

    token_response = client.exchange_code_for_token(client_id=client_id, client_secret=client_secret, code=code)

    return client

def pull_segments():

    ######################################################
    ##
    ## get segment leaderboards from all completed segments
    ##
    ######################################################

    client = authenticate()

    export_file = io.open('segment_leaderboard_results.txt', 'w', encoding="utf-8")

    segment_leaderboards = {}

    segment_efforts = pd.read_csv("segment_effort_results.txt")

    segments_ids = list(segment_efforts.segment_id.unique())

    i = 1

    for segment in segments_ids:

        ## in order to get around API rate-limiting, set computer to wait 15 mins and then do next block
        ## this results in a longer run time but hey, not the end of the world 

        if (i/600).is_integer():
            print("***",datetime.now().strftime("%H:%M:%S"),": Pausing at", i ,"calls for API rate-limiting")
            time.sleep(930) 

        try:

            #leaders = client.get_segment_leaderboard(segment)
            
            segment_leaderboards[segment] = {}

            #segment_leaderboards[segment]['number_of_all_attempts'] = leaders.effort_count
            #segment_leaderboards[segment]['kom_time'] = leaders[0].moving_time

            #for leader in leaders:
            #    if leader.athlete_name == 'August W.':
            #        segment_leaderboards[segment]['my_rank'] = leader.rank
            #        segment_leaderboards[segment]['my_pr_time'] = leader.moving_time

            ## for any segments where my PR was on a private ride, I won't be able to access this information        

            #if 'my_rank' not in segment_leaderboards[segment].keys():
            #    segment_leaderboards[segment]['my_rank'] = "N/A"
            #    segment_leaderboards[segment]['my_pr_time'] = "N/A"   
            #
            #i += 1        

            ## extract information about the segment            

            segment_info = client.get_segment(segment)

            segment_leaderboards[segment]['segment_name'] = segment_info.name.replace(',', '')
            segment_leaderboards[segment]['segment_elevation_gain'] = segment_info.total_elevation_gain
            segment_leaderboards[segment]['segment_distance'] = segment_info.distance
            segment_leaderboards[segment]['number_of_my_attempts'] = segment_info.athlete_segment_stats.effort_count

            segment_leaderboards[segment]['average_grade'] = segment_info.average_grade

            i += 1

        except Exception as e: 
            print("Issues with",segment,e)    
            i += 1

    ## export to file

    #export_file.write("id,number_of_all_attempts,kom_time,my_rank,my_pr_time,segment_name,segment_elevation_gain,segment_distance,number_of_my_attempts\n")
    export_file.write("id,segment_name,segment_elevation_gain,segment_distance,number_of_my_attempts,average_grade\n")
    for key in segment_leaderboards.keys():
        export_file.write("%s,"%(key))
        i = 1
        for value in segment_leaderboards[key]:
            if i < 5:
                export_file.write("%s,"%(segment_leaderboards[key][value]))
            else:
                export_file.write("%s\n"%(segment_leaderboards[key][value]))    
            i+=1  


#################

def pull_segments_cmd():
    # set up the parser/argument information with command line help
    parser= argparse.ArgumentParser(description="Pull & Save Strava Segment Leaderboard Data")

    args=parser.parse_args()

    pull_segments()

#################

def main():
    pull_segments_cmd()

#################

if __name__=="__main__":
    main()

#################
