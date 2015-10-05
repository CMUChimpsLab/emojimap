#!/usr/bin/env python

import os, json, geojson, csv, traceback, ujson, argparse, random
from collections import Counter, defaultdict
from flask import Flask, render_template, request, jsonify, json, url_for, flash, redirect
from flask_debugtoolbar import DebugToolbarExtension
from flask.ext.compress import Compress
from csv import DictWriter,DictReader
import geojson
import sys,cgi
import re
csv.field_size_limit(sys.maxsize)

SITE_ROOT = os.path.realpath(os.path.dirname(__file__))
# general flask app settings
app = Flask('map')
app.secret_key = 'some_secret'
Compress(app)

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

@app.route('/get-words-emojis-for-nghd', methods=['GET'])
def get_words_emojis_for_nghd():
    nghd = request.args['nghd'].replace("'","")
    top_words_and_emojis = {}
    nghd_words = json.load(open('outputs/nghd_words.json'))
    top_words_and_emojis["top words"] = nghd_words[nghd]["top words"]
    nghd_emojis = json.load(open('outputs/nghd_emojis.json'))
    top_words_and_emojis["top emojis"] = nghd_emojis[nghd]["top emojis"]
    return jsonify(top_words_and_emojis=top_words_and_emojis)


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
    tweets_per_nghd_words = json.load(open(tweet_file_name))
    tweets_per_word = defaultdict(list)
    #bold key word in the tweet
    for word in tweets_per_nghd_words[nghd]:
        for tweet in tweets_per_nghd_words[nghd][word]:
            tweet = re.sub(word,"<b>" + word + "</b>",tweet,flags=re.IGNORECASE)
            #make links clickable
            #for possibleUrl in tweet.split(" "):
            #    if possibleUrl.startswith("http"):
            #        print possibleUrl
            #        tweet = re.sub(possibleUrl, '<a href="' + possibleUrl +
            #            '" target="_blank">' + possibleUrl + '</a>',tweet)
            tweets_per_word[word].append(tweet)
    return jsonify(tweets_per_word=tweets_per_word) 

if __name__ == '__main__':
    #app.run(host='0.0.0.0', port=5000, debug=False) 
    app.run(host='0.0.0.0', debug=False)
 
