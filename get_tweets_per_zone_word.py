#!/usr/bin/env python
# coding: utf-8

#For each neighborhood and each top 10 words for that neighborhood, 
#compiles a list of tweets that contain that word.
 
from collections import defaultdict
import csv,sys
from csv import DictWriter, DictReader
import util.util, util.neighborhoods, cProfile
from util.neighborhoods import get_neighborhood_or_muni_name
import json
import psycopg2, psycopg2.extras, ppygis
import twokenize

def run_all():

    csv.field_size_limit(sys.maxsize)

    psql_conn = psycopg2.connect("dbname='tweet'")
    psycopg2.extras.register_hstore(psql_conn)
    pg_cur = psql_conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    
    # Build up the bins-to-nghds mapping so we can easily translate.
    bins_to_nghds = {}
    for line in DictReader(open('point_map.csv')):
        bins_to_nghds[(float(line['lat']), float(line['lon']))] = line['nghd']
    #get nghd to zone mapping
    nghds_to_zones = {}
    for line in DictReader(open('zone_map.csv')):
        nghds_to_zones[line['nghd']] = line['zone']

    words_per_zone = json.load(open('outputs/zone_words.json'))
    top10words = {}
    tweets_per_word = defaultdict(lambda: defaultdict(list))
   
    for zone in words_per_zone:
        top10words[zone] = words_per_zone[zone]["top words"]

    pg_cur.execute("SELECT text, ST_ASGEOJSON(coordinates), user_screen_name " + 
                                                        "FROM tweet_pgh;")
    counter = 0
    for row in pg_cur:
        counter += 1
        if (counter % 10000) == 0:
            print str(counter) + ' tweets processed'
        coords = json.loads(row[1])['coordinates']
        bin = util.util.round_latlon(coords[1], coords[0])
        if bin in bins_to_nghds:
            tweet_nghd = bins_to_nghds[bin]
        else:
            tweet_nghd = 'Outside Pittsburgh'
        if tweet_nghd in nghds_to_zones:
            zone = "Zone " + nghds_to_zones[tweet_nghd]
        else:
            zone = tweet_nghd
        tweet = row[0]
        tweet = tweet.replace('“','"').replace('”','"')
        tweet = unicode(tweet, errors='ignore')
        username = row[2]
        wordList = twokenize.tokenize(tweet)
        wordList = map(lambda x:x.lower(),wordList) 
        for word in top10words[zone]:
            if word in wordList:
                tweets_per_word[zone][word].append(username + ": " + tweet)
   
    print "writing to JSON file"

    with open('outputs/tweets_per_zoneword.json','w') as outfile:
        json.dump(tweets_per_word,outfile, indent=2)

run_all()
