#!/usr/bin/env python

#For each neighborhood and each top 3 emoji for that neighborhood, 
#compiles a list of tweets that have that emoji.
 
from collections import Counter, defaultdict
import csv,sys
from csv import DictWriter, DictReader
import util.util, util.neighborhoods, argparse, pymongo, cProfile
from util.neighborhoods import get_neighborhood_or_muni_name
import json,ijson

def run_all():

    csv.field_size_limit(sys.maxsize)
    
    # Build up the bins-to-nghds mapping so we can easily translate.
    bins_to_nghds = {}
    for line in DictReader(open('point_map.csv')):
        bins_to_nghds[(float(line['lat']), float(line['lon']))] = line['nghd']

    emojis_per_nghd = json.load(open('outputs/nghd_emojis.json'))
    top3emojis = {}
    tweets_per_emoji = defaultdict(lambda: defaultdict(list))    

    for nghd in emojis_per_nghd:
        top3emojis[nghd] = emojis_per_nghd[nghd]["top emojis"]

    all_tweets = ijson.items(open('/data/emojimap/emoji_tweets.json','r'),'item')

    counter = 0
    for tweet in all_tweets:
        counter += 1
        if (counter % 1000) == 0:
            print str(counter) + ' tweets processed'
        coords = tweet['coordinates']['coordinates']
        bin = util.util.round_latlon(coords[1], coords[0])
        if bin in bins_to_nghds:
            nghd = bins_to_nghds[bin]
        else:
            nghd = 'Outside Pittsburgh'

        #remove duplicate emojis within tweet
        filteredEmojiList = list(set(tweet['emoji'].split(',')))
        encodedEmojiList = [];
        for emoji in filteredEmojiList:
            encodedEmojiList.append(emoji.encode('utf-8'))

        if nghd in top3emojis:
            for emoji in top3emojis[nghd]:
                if emoji.encode('utf-8') in encodedEmojiList:
                    username = tweet['user']['screen_name']
                    text = tweet['text']
                    tweets_per_emoji[nghd][emoji].append(username + 
                                                        ":" + text) 

    print "writing to JSON file"
    with open('outputs/tweets_per_nghd_emoji.json','w') as outfile:
        json.dump(tweets_per_emoji,outfile, indent=2)

#if __name__ == '__main__':
#    cProfile.run("run_all()")

run_all()
