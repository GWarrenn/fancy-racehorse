import gpxpy
import gpxpy.gpx
import json
import re
import lxml    
from lxml import etree
from os import listdir
from os.path import isfile, join
from geojson import LineString, Feature, FeatureCollection, dump
import numpy as np
import pandas as pd

import pdb

## get list of current events from activity file

data = pd.read_csv('C:/Users/augus/Desktop/mapping/export_4778598/activities.csv')
data['Activity Date'] = pd.to_datetime(data['Activity Date'])
data = data[data['Activity Date'] > '2019-01-01']

orig_files = data['Filename'].tolist()

pattern = re.compile(r".gz$")
files = [pattern.sub("", item) for item in orig_files]
files = ['C:/Users/augus/Desktop/mapping/export_4778598/'+item for item in files]

dict = {}

for file in files:
    
    gpx_search = re.compile("gpx$")
    
    if gpx_search.search(file):

        pattern = re.compile(r"C:/Users/augus/Desktop/mapping/export_4778598/")
        file_filter = pattern.sub("", file)
        print(file)

        gpx_file = open(file, 'r')
        
        gpx = gpxpy.parse(gpx_file)

        i = 0
        
        for track in gpx.tracks:
            dict[track.name] = {}
            dict[track.name]['commute'] = str(data['Commute'][data['Filename'] == str(file_filter)].values[0])

            dict[track.name]['geo'] = []
            for segment in track.segments:
                for point in segment.points:
                    if i > 20:
                        dict[track.name]['geo'].append([point.longitude,point.latitude])
                        i = i+1

    tcx_search = re.compile("tcx$")
    if tcx_search.search(file):

        pattern = re.compile(r"C:/Users/augus/Desktop/mapping/export_4778598/")
        file_filter = pattern.sub("", file)
        
        print(file)
        
        ## the xml declaration of every tcx file is indented, which breaks things.
        ## fix this by reading in the file and replacing the first line to remove indent
        ## only really have to run once per data pull
        
        with open(file) as f:
            lines = f.readlines()
            
        lines[0] = '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>\n'

        ## now write file back out

        with open(file, "w") as f:
            f.writelines(lines)

        ## h/t to https://github.com/cast42/vpower/blob/master/vpower.py
        ## for helping me figure out how to parse tcx files
        
        ns1 = 'http://www.garmin.com/xmlschemas/TrainingCenterDatabase/v2'
        ns2 = 'http://www.garmin.com/xmlschemas/ActivityExtension/v2'
        
        tree = etree.parse(file)
        root = tree.getroot()
        
        tracks = []
        dict[file_filter] = {}
        dict[file_filter]['commute'] = str(data['Commute'][data['Filename'] == str(file_filter)+'.gz'].values[0])

        dict[file_filter]['geo'] = []
        
        for element in root.iter():
                if element.tag == '{%s}Track'%ns1:
                    tracks.append(element)

        lat = []
        lon = []           
        
        for element in tracks:
            for child in element:
                for elem in child.iter():
                    if elem.tag == '{%s}LatitudeDegrees'%ns1:
                        for node in elem.iter():
                            lat.append(node.text)
                    if elem.tag == '{%s}LongitudeDegrees'%ns1:    
                        for node in elem.iter():
                            lon.append(node.text)
        
        for i in range(0,len(lat)):
            if i > 20 & i < len(lat) - 20:
                dict[file_filter]['geo'].append([float(lon[i]),float(lat[i])])

## now convert dict to geojson file

features = []

for key in dict.keys():
    features.append(Feature(geometry=LineString(dict[key]['geo']),properties={"Name": key,"Commute" : dict[key]['commute']}))
        
## dump data to json file for mapping        
        
with open('result.json', 'w') as fp:
    json.dump(features, fp)
