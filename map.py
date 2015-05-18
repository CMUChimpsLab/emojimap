#!/usr/bin/env python

import os, pymongo, json, csv, traceback, ujson, argparse, random
#from util import util
import util
from util import neighborhoods
from collections import Counter, defaultdict
from flask import Flask, render_template, request, jsonify, json, url_for, flash, redirect
from flask_debugtoolbar import DebugToolbarExtension
from csv import DictWriter,DictReader
import geojson
import sys
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

all_tweets = []

# Creates a dict of user: {bunch of info including tweets:[...]}
def init_tweets_and_responses(tweets_file_name):
    global all_tweets
    #all_tweets = ijson.items(open(tweets_file_name,'r'),'item')
    all_tweets = json.load(open(tweets_file_name))     
   
# This call kicks off all the main page rendering.
@app.route('/')
def index():
    return render_template('main.html')

@app.route('/get-user-tweets', methods=['GET'])
def get_user_tweets():
    tweets = random.sample(all_tweets, 1000)
    return jsonify(tweets=tweets)

@app.route('/get-emojis-per-bin', methods=['GET'])
def get_emojis_per_bin():
    emojis_per_bin = {}
    for line in DictReader(open('./outputs/bins_emojis.csv')):
        emojis_per_bin[str([float(line['lat']),float(line['lon'])])] = line['most_common_emoji']
    return jsonify(emojis_per_bin=emojis_per_bin)


def getCentralPointOfNghds():
    nghds_to_bins = defaultdict(list)
    for line in DictReader(open('point_map.csv')):
        nghds_to_bins[line['nghd']].append([float(line['lat']),
                                            float(line['lon'])])
    #average lat points & lon points
    nghds_to_centralPoint = defaultdict()
    for nghd in nghds_to_bins:
        if nghd!='Outside Pittsburgh':
            nghd_avg = defaultdict() 
            nghd_avg['count'] = 0.0
            nghd_avg['lat'] = 0.0
            nghd_avg['lon'] = 0.0
            for coord in nghds_to_bins[nghd]:
                lat = coord[0]
                lon = coord[1]
                nghd_avg['count']+=1.0
                nghd_avg['lat'] += lat
                nghd_avg['lon'] += lon
            nghds_to_centralPoint[nghd] = [float(nghd_avg['lat']/nghd_avg['count']),
                                      float(nghd_avg['lon']/nghd_avg['count'])]
    return nghds_to_centralPoint
    
@app.route('/get-emojis-per-nghd', methods=['GET'])
def get_emojis_per_nghd():
    #map nghd name to coordinates
    nghd_to_coord = {}
    nghds_to_centralPoint = getCentralPointOfNghds()
    emojis_per_nghd = {}

    for line in DictReader(open('./outputs/tweets_per_nghdemoji_no_duplicates.csv')):
        nghd_name = line['nghd']
        if nghd_name!='Outside Pittsburgh':
            #first_emojis = "\n".join((line['first_emojis'].split(','))[1])
            #second_emojis = "\n".join((line['second_emojis'].split(','))[1])
            #third_emojis = "\n".join((line['third_emojis'].split(','))[1])

            emojis_per_nghd[str(nghds_to_centralPoint[nghd_name])] = \
                [line['first'],line['second'],line['third'], \
           line['first_emojis'],line['second_emojis'],line['third_emojis']]
                #first_emojis,second_emojis,third_emojis]

    return jsonify(emojis_per_nghd=emojis_per_nghd)

''' this works
    for line in DictReader(open('./outputs/nghds_emojis123_no_duplicates.csv')):
        nghd_name = line['nghd']
        #print nghd_name
        if nghd_name!='Outside Pittsburgh':
            emojis_per_nghd[str(nghds_to_centralPoint[nghd_name])] = 
                         [line['first'],line['second'],line['third']]

            #print str(nghds_to_centralPoint[nghd_name])
'''  


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--tweets_json_file', default='emoji_tweets.json')
    args = parser.parse_args()
    #print "loading all tweets"
    #init_tweets_and_responses(args.tweets_json_file)
    #print "done loading all tweets"
    app.run(host='0.0.0.0', port=1025, debug=True)  # listen on localhost only (for local testing)
