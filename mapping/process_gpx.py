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
from datetime import datetime
import fitparse
from joblib import Parallel, delayed

import pdb

def process_gpx(file,data):

    pattern = re.compile(r"../dc_data/08_rcp/export_4778598/")
    file_filter = pattern.sub("", file)
    print(file)

    dict = {}

    gpx_file = open(file, 'r')
    
    try:
        gpx = gpxpy.parse(gpx_file)
    except:
        print("skipping..")
        return
    
    for track in gpx.tracks:
        dict[track.name] = {}

        dict[track.name]['commute'] = str(data['Commute'][data['Filename'] == str(file_filter)].values[0])
        dict[file_filter]['activity_date'] = data['Activity Date'].dt.date[data['Filename'] == str(file_filter)].values[0].strftime("%Y-%m-%d")

        dict[track.name]['geo'] = []
        for segment in track.segments:
            for point in segment.points:
                dict[track.name]['geo'].append([point.longitude,point.latitude])
                #time_secs = ((point.time.hour * 360) + (point.time.minute * 60) + point.time.second) / 12239
                #dict[track.name]['timestamp'].append([time_secs])

    return(dict)

def process_tcx(file,data):

    dict = {}

    pattern = re.compile(r"../dc_data/08_rcp/export_4778598/")
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
    dict[file_filter]['activity_date'] = data['Activity Date'].dt.date[data['Filename'] == str(file_filter)+".gz"].values[0].strftime("%Y-%m-%d")

    dict[file_filter]['geo'] = []
    dict[file_filter]['timestamp'] = []
    
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
                if elem.tag == '{%s}Time'%ns1:
                    for node in elem.iter():
                        node.text = re.sub('-0[0-9]:00', '', node.text)
                        node.text = re.sub('\+0[0-9]:00', '', node.text)
                        try:
                            new_time = datetime.strptime(node.text, '%Y-%m-%dT%H:%M:%S.%f')
                            time_secs = ((new_time.hour * 360) + (new_time.minute * 60) + new_time.second) / 12239
                            dict[file_filter]['timestamp'].append(time_secs)
                        except Exception as e:
                            new_time = datetime.strptime(node.text, '%Y-%m-%dT%H:%M:%SZ')
                            time_secs = ((new_time.hour * 360) + (new_time.minute * 60) + new_time.second) / 12239
                            dict[file_filter]['timestamp'].append(time_secs)
    
    for i in range(0,len(lat),2):
        dict[file_filter]['geo'].append([float(lon[i]),float(lat[i])])

    return(dict)

def process_fit(file,data):

    pattern = re.compile(r"../dc_data/08_rcp/export_4778598/")
    file_filter = pattern.sub("", file) 
    
    pattern = re.compile(".gz")
    file = pattern.sub("",file)

    dict = {}

    try:

        fitfile = fitparse.FitFile(file)

        dict[file_filter] = {}
        dict[file_filter]['commute'] = str(data['Commute'][data['Filename'] == str(file_filter)+'.gz'].values[0])
        dict[file_filter]['activity_date'] = data['Activity Date'].dt.date[data['Filename'] == str(file_filter)+".gz"].values[0].strftime("%Y-%m-%d")

        dict[file_filter]['geo'] = []
        dict[file_filter]['timestamp'] = []

        lat = []
        lon = []  

        try:      

            # Iterate over all messages of type "record"
            for record in fitfile.get_messages("record"):
                for data_item in record:
                    if data_item.name == "position_lat":
                        if data_item.value is not None:
                            lat.append(data_item.value * ( 180 / (2**31) ))
                    if data_item.name == "position_long":
                        if data_item.value is not None:
                            lon.append(data_item.value * ( 180 / (2**31) ))

        except Exception as e:
            print('Issue #1 with {}: {}'.format(record,e))

        for i in range(0,len(lat),2):
            dict[file_filter]['geo'].append([float(lon[i]),float(lat[i])])
    
    except Exception as e:
        print('File read Issue #2 with: {}'.format(e))

    return(dict)

def process_all_files(files,data):

    dict = []
    bad_files = []

    for file in files:
        try:
            gpx_search = re.compile("gpx")
            if gpx_search.search(file):
                dict.append(process_gpx(file,data))

            tcx_search = re.compile("tcx")
            if tcx_search.search(file):
                dict.append(process_tcx(file,data))

            fit_search = re.compile("fit")
            if fit_search.search(file):
                dict.append(process_fit(file,data))
        
        except Exception as e:
            bad_files.append(file)

    if dict is None:
        return(None)

    return(dict,file)
    
def main():

    ## get list of current events from activity file

    data = pd.read_csv('../dc_data/08_rcp/export_4778598/activities.csv')
    data['Activity Date'] = pd.to_datetime(data['Activity Date'])
    data = data[data['Activity Type'] == 'Ride']

    orig_files = data['Filename'].tolist()

    pattern = re.compile(r".gz$")
    files = [pattern.sub("", item) for item in orig_files]
    files = ['../dc_data/08_rcp/export_4778598/' + item for item in files]

    def chunks(lst, n):
        """Yield successive n-sized chunks from lst."""
        for i in range(0, len(lst), n):
            yield lst[i:i + n]

    file_list = chunks(files,100)

    dict_list = Parallel(n_jobs=4,timeout=99999)(delayed(process_all_files)(file,data) for file in file_list)

    result_dict = {}

    for item in dict_list:
        for record in item[0]:
            for value in record:
                result_dict[value] = record[value]

    features = []

    for key in result_dict.keys():
        features.append(Feature(geometry=LineString(result_dict[key]['geo']),
                                properties={"Name": key,
                                            "Commute" : result_dict[key]['commute'],
                                            "Date" : result_dict[key]['activity_date']}))

    ## dump data to json file for mapping        
            
    with open('result_20250201.json', 'w') as fp:
        json.dump(features, fp)

if __name__ == '__main__':
    main()