#!/usr/bin/env python

#Compiles emojis per bin and per neighborhood as well as the most common
#emoji in each bin/neighborhood.
 
from collections import Counter, defaultdict
import csv,sys
from csv import DictWriter, DictReader
import util.util, util.neighborhoods, argparse, pymongo, cProfile
from util.neighborhoods import get_neighborhood_or_muni_name
import json,ijson

def run_all():

    csv.field_size_limit(sys.maxsize)

    nghd_emojis = defaultdict(list)

    for line in DictReader(open('outputs/nghds_emojis123_no_duplicates.csv')):
            nghd_emojis[line['nghd']] = [line['first'],
                                        line['second'],
                                        line['third']]  
 
    print "loading tweets"  
 
    all_tweets = ijson.items(open('../../../data/emojimap/emoji_tweets.json','r'),'item')

    print "loaded tweets"
    
    # Build up the bins-to-nghds mapping so we can easily translate.
    bins_to_nghds = {}
    for line in DictReader(open('point_map.csv')):
        bins_to_nghds[(float(line['lat']), float(line['lon']))] = line['nghd']

    organized_tweets = defaultdict(list) #indexed by (nghd,emoji)
    num = Counter()
     
    nghds_writer = DictWriter(open('outputs/tweets_per_nghdemoji_no_duplicates','w'),
        ['nghd', 'first','first_emojis','second',
        'second_emojis','third','third_emojis'])
    nghds_writer.writeheader()

    print "loading tweets"

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

        emojis = tweet['emoji']
        emojiList = emojis.split(',')

        #remove duplicates from the emojiList
        emojiSet = set(emojiList)
        emojiListFixed = list(emojiSet)

        for emoji in emojiListFixed:
            if nghd in nghd_emojis:
                if emoji.encode('utf-8') in nghd_emojis[nghd]:
                    username = tweet['user']['screen_name']
                    text = tweet['text']
                    organized_tweets[(nghd,emoji.encode('utf-8'))].append(username + 
                                                        ":" + text) 
    print "added all tweets to dictionary"

    for nghd in nghd_emojis:
        nghds_writer.writerow({'nghd': nghd, 'first':nghd_emojis[nghd][0],
            'first_emojis': organized_tweets[(nghd,nghd_emojis[nghd][0])],
                   'second':nghd_emojis[nghd][1],
            'second_emojis': organized_tweets[(nghd,nghd_emojis[nghd][1])],
                    'third':nghd_emojis[nghd][2],
            'third_emojis': organized_tweets[(nghd,nghd_emojis[nghd][2])]})

if __name__ == '__main__':
    cProfile.run("run_all()")
