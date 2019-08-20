import gpxpy
import gpxpy.gpx
import json
import re
import lxml    
from lxml import etree
import lxml.etree as ET
from os import listdir
from os.path import isfile, join
from geojson import LineString, Feature, FeatureCollection, dump
import numpy as np

import pdb

files = [f for f in listdir('./activities/') if isfile(join('./activities/', f))]

#files = ['2731561468.tcx']

dict = {}

for file in files:
    
    gpx_search = re.compile("gpx$")
    
    if gpx_search.search(file):
    
        print(file)

        gpx_file = open(file, 'r')
        
        gpx = gpxpy.parse(gpx_file)
        
        for track in gpx.tracks:
            dict[track.name] = {}
            dict[track.name]['geo'] = []
            for segment in track.segments:
                for point in segment.points:
                    dict[track.name]['geo'].append([point.longitude,point.latitude])

    tcx_search = re.compile("tcx$")
    if tcx_search.search(file):
        
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
        dict[file] = {}
        dict[file]['geo'] = []
        
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
            dict[file]['geo'].append([float(lon[i]),float(lat[i])])
     
## now convert dict to geojson file

features = []

for key in dict.keys():
    features.append(Feature(geometry=LineString(dict[key]['geo']),properties={"Name": key}))
        
## dump data to json file for mapping        
        
with open('result.json', 'w') as fp:
    json.dump(features, fp)
