#!/usr/bin/env python
# coding: utf-8

#For each neighborhood and each top 10 words for that neighborhood, 
#compiles a list of tweets that contain that word.
 
from collections import defaultdict
import csv,sys
from csv import DictWriter, DictReader
import util.util, util.neighborhoods, cProfile
from util.neighborhoods import get_neighborhood_or_muni_name
import json, string
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

    words_per_nghd = json.load(open('outputs/nghd_words.json'))
    top10words = {}
    tweets_per_word = defaultdict(lambda: defaultdict(list))
   
    for nghd in words_per_nghd:
        top10words[nghd] = words_per_nghd[nghd]["top words"]

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
        username = row[2]
        tweet = row[0]
        unchangedTweet = row[0]
        tweet = tweet.replace('“','"').replace('”','"')
        tweet = tweet.replace('’',"'").replace('‘',"'")
        tweet = tweet.replace("…","...")
        tweet = tweet.replace("\n","")
        #tweet = unicode(tweet, errors='ignore')
        #wordList = twokenize.tokenize(tweet)
        exclude = set(string.punctuation)
        exclude.remove('#')
        exclude.remove('-')
        exclude.remove("'")
        exclude.remove("@")
        for punct in exclude:
            tweet = tweet.replace(punct,"")
        wordList = tweet.split(" ")
        wordList = map(lambda x:x.lower(),wordList)
        if tweet_nghd in top10words:
            for word in top10words[tweet_nghd]:
                word = word.encode('utf-8')
                if word in wordList:
                    tweets_per_word[tweet_nghd][word].append(username + ": " + unchangedTweet)
   
    print "writing to JSON file"

    with open('outputs/tweets_per_nghd_words.json','w') as outfile:
        json.dump(tweets_per_word,outfile, indent=2)

run_all()
