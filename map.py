#!/usr/bin/env python

import os, json, geojson, csv, traceback, ujson, argparse, random
#from util import util
import util
from util import neighborhoods
from collections import Counter, defaultdict
from flask import Flask, render_template, request, jsonify, json, url_for, flash, redirect
from flask_debugtoolbar import DebugToolbarExtension
from flask.ext.compress import Compress
from csv import DictWriter,DictReader
import geojson
import sys,cgi
csv.field_size_limit(sys.maxsize)

SITE_ROOT = os.path.realpath(os.path.dirname(__file__))
# general flask app settings
app = Flask('map')
app.secret_key = 'some_secret'
Compress(app)
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
    bounds = {}
    nghds = geojson.load(open('geodata/Pittsburgh_Neighborhoods.json'))
    nghd_features = nghds['features']
    for nghd in nghd_features: 
        nghd_name = nghd["properties"]["HOOD"]
        bounds[nghd_name] = nghd["geometry"]["coordinates"]    
    boroughs = geojson.load(open('geodata/Allegheny_Munis.json'))
    borough_features = boroughs['features']
    for borough in borough_features:
        borough_name = borough["properties"]["LABEL"]
        if borough_name=="Pittsburgh": continue
        bounds[borough_name] = borough["geometry"]["coordinates"]
    return jsonify(bounds=bounds)

@app.route('/get-nghd-names/', methods=['GET'])
def get_nghd_names():
    nghd_words = json.load(open('outputs/nghd_words.json'))

    nghds_to_centralPoint = {}
    for line in DictReader(open('nghd_central_point.csv')):
        nghd = line['nghd']
        if nghd in nghd_words:
            if nghd=="Outside Pittsburgh": continue
            if nghd=="Pittsburgh": continue 
            nghds_to_centralPoint[line['nghd']]=[float(line['lat']),float(line['lon'])]
    
    return jsonify(nghds_to_centralPoint=nghds_to_centralPoint)

@app.route('/get-emojis-per-nghd', methods=['GET'])
def get_emojis_per_nghd():
    #map nghd name to coordinates
    nghds_to_centralPoint = {}
    for line in DictReader(open('nghd_central_point.csv')):
        nghds_to_centralPoint[line['nghd']]=[float(line['lat']),float(line['lon'])]
       
    top_emojis_per_nghd = defaultdict(list)
    nghd_emojis = json.load(open('outputs/nghd_emojis.json'))
    for nghd in nghd_emojis:
        if nghd=="Outside Pittsburgh": continue
        if nghd=="Pittsburgh": continue
        key = nghds_to_centralPoint[nghd]
        key.append("\'"+nghd.encode('utf-8')+"\'")
        top_emojis_per_nghd[str(key)] = nghd_emojis[nghd]["top emojis"]
    return jsonify(top_emojis_per_nghd=top_emojis_per_nghd)  

@app.route('/get-tweets-per-emoji', methods=['GET'])
def get_tweets_per_emoji():
    nghd = request.args['nghd'].replace("'","")
    tweet_file_name = 'outputs/tweets_per_nghd_emoji.json'
    tweets_per_nghd_emojis = json.load(open(tweet_file_name))
    tweets_per_emoji = tweets_per_nghd_emojis[nghd]
    return jsonify(tweets_per_emoji=tweets_per_emoji)  

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
        key.append("\'"+nghd.encode('utf-8')+"\'")
        top_words_per_nghd[str(key)] = nghd_words[nghd]["top words"]
    return jsonify(top_words_per_nghd=top_words_per_nghd)

@app.route('/get-tweets-per-word', methods=['GET'])
def get_tweets_per_word():
    nghd = request.args['nghd'].replace("'","")
    tweet_file_name = 'outputs/tweets_per_nghd_words.json'
    if nghd.startswith("Zone"): 
        #actually at the zone level, not nghd level
        tweet_file_name = 'outputs/tweets_per_zone_words.json'
    tweets_per_nghd_words = json.load(open(tweet_file_name))
    tweets_per_word = tweets_per_nghd_words[nghd]
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
