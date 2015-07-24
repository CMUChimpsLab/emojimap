#!/usr/bin/env python

import os, pymongo, json, geojson, csv, traceback, ujson, argparse, random
#from util import util
import util
from util import neighborhoods
from collections import Counter, defaultdict
from flask import Flask, render_template, request, jsonify, json, url_for, flash, redirect
from flask_debugtoolbar import DebugToolbarExtension
from csv import DictWriter,DictReader
import geojson
import sys,cgi
csv.field_size_limit(sys.maxsize)

SITE_ROOT = os.path.realpath(os.path.dirname(__file__))
# general flask app settings
app = Flask('map')
app.secret_key = 'some_secret'
# related to debugging
# app.debug = True
# app.config['DEBUG_TB_PROFILER_ENABLED'] = True
# app.config['DEBUG_TB_TEMPLATE_EDITOR_ENABLED'] = True
# toolbar = DebugToolbarExtension(app)

# This call kicks off all the main page rendering.
@app.route('/')
def index():
    return render_template('main.html')

@app.route('/get-nghd-bounds', methods=['GET'])
def get_nghd_bounds():
    nghd_bounds = {}
    nghds = geojson.load(open('geodata/Pittsburgh_Neighborhoods.json'))
    nghd_features = nghds['features']
    for nghd in nghd_features: 
        nghd_name = nghd["properties"]["HOOD"]
        nghd_bounds[nghd_name] = nghd["geometry"]["coordinates"]        
    return jsonify(nghd_bounds=nghd_bounds)

@app.route('/get-emojis-per-nghd', methods=['GET'])
def get_emojis_per_nghd():
    #map nghd name to coordinates
    nghd_to_coord = {}
    nghds_to_centralPoint = {}
    emojis_per_nghd = {}

    for line in DictReader(open('nghd_central_point.csv')):
        nghds_to_centralPoint[line['nghd']]=[float(line['lat']),float(line['lon'])]
       
    print "finished loading nghd central coordinates"
    nghd_emoji_data = json.load(open('outputs/tweets_per_nghdemoji_no_duplicates.json'))
    for nghd in nghd_emoji_data:
        if nghd=="Outside Pittsburgh": continue
        if nghd=="Pittsburgh": continue
        key = str(nghds_to_centralPoint[nghd])
        emojis_per_nghd[key]=[]
        emojis_per_nghd[key].append(nghd)
        for emojis in nghd_emoji_data[nghd]:
            emojis_per_nghd[key].append(emojis)

    print "done with getting emojis per nghd"
    return jsonify(emojis_per_nghd=emojis_per_nghd)  

@app.route('/get-words-per-nghd/', methods=['GET'])
def get_words_per_nghd():
    #map nghd name to coordinates    
    nghds_to_centralPoint = {}
    for line in DictReader(open('nghd_central_point.csv')):
        nghds_to_centralPoint[line['nghd']]=[float(line['lat']),float(line['lon'])]
    
    top_words_per_nghd = defaultdict(list)
    nghd_words = json.load(open('outputs/nghd_words.json'))
    for nghd in nghd_words:
        if nghd=="Outside Pittsburgh": continue
        if nghd=="Pittsburgh": continue
        #key is [lat,lon,nghd]
        key = nghds_to_centralPoint[nghd]
        key.append("\'"+nghd+"\'") 
        top_words_per_nghd[str(key)] = nghd_words[nghd]["top words"]
    return jsonify(top_words_per_nghd=top_words_per_nghd)

@app.route('/get-tweets-per-word', methods=['GET'])
def get_tweets_per_word():
    nghd = request.args['nghd'].replace("'","")
    tweet_file_name = 'outputs/tweets_per_nghdword.json'
    if nghd.startswith("Zone"): 
        #actually at the zone level, not nghd level
        tweet_file_name = 'outputs/tweets_per_zoneword.json'
    tweets_per_nghdword = json.load(open(tweet_file_name))
    tweets_per_word = tweets_per_nghdword[nghd]
    return jsonify(tweets_per_word=tweets_per_word) 

@app.route('/get-words-per-zone', methods=['GET'])
def get_words_per_zone():
    #map zone/borough/township name to coordinates    
    nghds_in_zones = defaultdict(list)
    for line in DictReader(open('zone_map.csv')):
        nghds_in_zones["Zone " + line['zone']].append(line['nghd'])

    nghds_to_centralPoint = {}
    for line in DictReader(open('nghd_central_point.csv')):
        nghds_to_centralPoint[line['nghd']]=[float(line['lat']),float(line['lon'])]
   
    zones_to_centralPoint = {}
    for zone in nghds_in_zones:
        avg_lat = 0.0
        avg_lon = 0.0
        num_nghds = 0
        for nghd in nghds_in_zones[zone]:
            num_nghds += 1
            coords = nghds_to_centralPoint[nghd]
            avg_lat += coords[0]
            avg_lon += coords[1]    
        zones_to_centralPoint[zone] = [avg_lat/num_nghds,avg_lon/num_nghds]
            
    top_words_per_zone = defaultdict(list)
    zone_words = json.load(open('outputs/zone_words.json'))
    for zone in zone_words:
        if zone=="Outside Pittsburgh": continue
        if zone=="Pittsburgh": continue
        key = zones_to_centralPoint[zone]
        key.append("\'"+zone+"\'")
        top_words_per_zone[str(key)] = zone_words[zone]["top words"]
    return jsonify(top_words_per_zone=top_words_per_zone)

    top_words_per_nghd = defaultdict(list)
    nghd_words = json.load(open('outputs/nghd_words.json'))
    for nghd in nghd_words:
        if nghd=="Outside Pittsburgh": continue
        if nghd=="Pittsburgh": continue
        #key is [lat,lon,nghd]
        key = nghds_to_centralPoint[nghd]
        key.append("\'"+nghd+"\'") 
        top_words_per_nghd[str(key)] = nghd_words[nghd]["top words"]
    return jsonify(top_words_per_nghd=top_words_per_nghd)


    


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--tweets_json_file', default='emoji_tweets.json')
    args = parser.parse_args()
    app.run(host='0.0.0.0', port=5000, debug=True)  # listen on localhost only (for local testing)
