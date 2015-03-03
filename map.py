#!/usr/bin/env python

import os, pymongo, json, csv, traceback, ujson, argparse, random
from util import util
from collections import Counter
from flask import Flask, render_template, request, jsonify, json, url_for, flash, redirect
from flask_debugtoolbar import DebugToolbarExtension

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
    all_tweets = ujson.load(open(tweets_file_name))
        
# This call kicks off all the main page rendering.
@app.route('/')
def index():
    return render_template('main.html')
 
# Actually returns tweets from all users, we're just reusing buttons that were
# already there.
@app.route('/get-user-tweets', methods=['GET'])
def get_user_tweets():
    tweets = random.sample(all_tweets, 1000)
    for tweet in tweets:
        tweet['emoji'] = ''.join(tweet['emoji'].split(','))

    return jsonify(tweets=tweets)

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--tweets_json_file', default='emoji_tweets.json')
    args = parser.parse_args()
    print "loading all tweets"
    init_tweets_and_responses(args.tweets_json_file)
    print "done loading all tweets"
    app.run(host='127.0.0.1', debug=True)  # listen on localhost only (for local testing)
