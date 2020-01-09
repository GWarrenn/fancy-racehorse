import stravalib
from stravalib.client import Client
import configparser
import argparse
import webbrowser
import pandas as pd
import numpy as np
import pdb

def pull_segments():

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

    cols = ['segment_id','name','number_of_my_attempts',
            'number_of_all_attempts','my_rank','my_pr_time',
            'leader_pr_time','segment_elevation_gain','segment_distance']

    results = pd.DataFrame(columns=cols)        

    ## first get all segments in big square around DMV

    segments = client.explore_segments([('38.701097', '-77.310778'),('39.090828','-76.863819')])

    print("Pulling segment data for:")

    for s in segments: 

        print(" -- " + s.name)

        ## extract segment leaderboard information

        segment_id = s.id
        name = s.name

        leaders = client.get_segment_leaderboard(s.id)
        number_of_all_attempts = leaders.effort_count
        leader_pr_time = leaders[0].moving_time

        for leader in leaders:
            if leader.athlete_name == 'August W.':
                my_rank = leader.rank
                my_pr_time = leader.moving_time    

        ## extract information about the segment            

        segment_info = client.get_segment(s.id)

        segment_elevation_gain = segment_info.total_elevation_gain
        segment_distance = segment_info.distance
        number_of_my_attempts = segment_info.athlete_segment_stats.effort_count

        data = pd.DataFrame(columns=cols)      

        data.loc[1] = [segment_id,name,number_of_my_attempts,
            number_of_all_attempts,my_rank,my_pr_time,
            leader_pr_time,segment_elevation_gain,
            segment_distance]       

        results = results.append(data)
    
    print("Exporting results to csv file...")

    results.to_csv('segment_results.csv', index=False, encoding='utf-8-sig')

#################

def pull_segments_cmd():
    # set up the parser/argument information with command line help
    parser= argparse.ArgumentParser(description="Pull & Save Strava Cycling Data")

    pull_segments()

#################

def main():
    pull_segments_cmd()

#################

if __name__=="__main__":
    main()

#################
