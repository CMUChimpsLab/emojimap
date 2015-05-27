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

    nghd_emojis = defaultdict(list)

    for line in DictReader(open('outputs/nghds_emojis123_no_duplicates.csv')):
           nghd_emojis[line['nghd']] = [line['first'],
                                        line['second'],
                                        line['third']]  
 
    print "loading tweets"  
 
    all_tweets = ijson.items(open('../../../../data/emojimap/emoji_tweets.json','r'),'item')

    print "loaded tweets"
    
    # Build up the bins-to-nghds mapping so we can easily translate.
    bins_to_nghds = {}
    for line in DictReader(open('point_map.csv')):
        bins_to_nghds[(float(line['lat']), float(line['lon']))] = line['nghd']

    organized_tweets = {}
    for nghd in nghd_emojis:
        organized_tweets[nghd] = defaultdict(list)

    num = Counter()
     
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
                    organized_tweets[nghd][emoji.encode('utf-8')].append(username + 
                                                        ":" + text) 

    finalEmojiData = defaultdict(list)
    for nghd in nghd_emojis:
        first_emoji = nghd_emojis[nghd][0]
        finalEmojiData[nghd].append(first_emoji)
        finalEmojiData[nghd].append(organized_tweets[nghd][first_emoji])
        second_emoji = nghd_emojis[nghd][1]
        finalEmojiData[nghd].append(second_emoji)
        finalEmojiData[nghd].append(organized_tweets[nghd][second_emoji])
        third_emoji = nghd_emojis[nghd][2]
        finalEmojiData[nghd].append(third_emoji)
        finalEmojiData[nghd].append(organized_tweets[nghd][third_emoji])
        #need to format as a list to maintain order of emojis

    print "added all tweets to dictionary"

    with open('outputs/tweets_per_nghdemoji_no_duplicates.json','w') as outfile:
        json.dump(finalEmojiData,outfile, indent=2)

if __name__ == '__main__':
    cProfile.run("run_all()")
