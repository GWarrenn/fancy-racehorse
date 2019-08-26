# fancy-racehorse

For 2019, I decided to set a goal: bike 2000 miles over the course of the year. The number was somewhat random but the motivation was to get out and bike more. In order to keep myself accountable and to track my progress, I developed this repo, which grabs the biking data I record through Strava and then displays the progress on my website: https://gwarrenn.github.io/A-Terrible-Resolution/. As an added bonus, I also created a betting pool, which I am not able to view until Jan 1. 2020, that allowed my friends to guess on how far I would actually make it. 

## Scraping Strava Data

In order to keep track of my progress, I needed a way to pull data from my Strava account and, considering I ride my bike about 6/7 times a week, manual entry was not an ideal form of data collection. After reading through the Strava API documentation, I discovered an existing Strava Python package -- [stravalib](https://github.com/hozn/stravalib) -- that made interfacing with the API very simple (once I figured out how OAuth2 works). The resulting program -- [pull_data.py](https://github.com/GWarrenn/fancy-racehorse/blob/master/pull_strava.py) -- is a command-line python program that reads in a config file containing API secret keys and saves to a local csv file. This process still requires me to manually pull and upload the data, as the OAuth2 authentication behind Strava's API requires generating and feeding a one-time key to the program.

## Visualizing Progress

Once the ride-level Strava data is processed and stored in my GitHub repo, the data is fed to a number of D3.js visualizations on my personal website. 

## Further/Ongoing Work

- [ ] Mapping GPX/TCX files 
