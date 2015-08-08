#!/usr/bin/env python

#Compiles all the emojis tweeted per bin and per neighborhood 
#as well as the most common emoji in each bin/neighborhood.
 
from collections import Counter, defaultdict
from csv import DictWriter, DictReader
import util.util, util.neighborhoods, argparse, pymongo, cProfile
from util.neighborhoods import get_neighborhood_or_muni_name
import json,ijson
import math

def run_all():
    parser = argparse.ArgumentParser()
    parser.add_argument('--point_map_file', '-p', default='point_map.csv')
    parser.add_argument('--tweets_json_file', default='/data/emojimap/emoji_tweets.json')
 
    args = parser.parse_args()

    # Build up the bins-to-nghds mapping so we can easily translate.
    bins_to_nghds = {}
    for line in DictReader(open(args.point_map_file)):
        bins_to_nghds[(float(line['lat']), float(line['lon']))] = line['nghd']

    nghd_count = 0
    freqs = defaultdict(lambda: defaultdict(int)) #freqs[nghd][word]
    TF = {}
    IDF = defaultdict(int)
    TFIDF = {}
    uniq_users_per_emoji = defaultdict(lambda: defaultdict(set))
                 #uniq_users_per_emoji[nghd][word]
    
    print "loading tweets"
    all_tweets = ijson.items(open(args.tweets_json_file,'r'),'item')
    print "loaded all tweets"

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
 
        username = tweet['user']['screen_name']
        #remove duplicate emojis within tweet
        filteredEmojiList = list(set(tweet['emoji'].split(',')))

        for emoji in filteredEmojiList:
            emoji = emoji.encode('utf-8')
            freqs[nghd][emoji] += 1
            uniq_users_per_emoji[nghd][emoji].add(username)            

    #only care about emojis tweeted by at least 10 people
    for nghd in uniq_users_per_emoji:
        for emoji in uniq_users_per_emoji[nghd]:
            if len(uniq_users_per_emoji[nghd][emoji]) < 10:
                del freqs[nghd][emoji]
        #if less than 3 emojis left, delete the nghd
        if len(freqs[nghd]) < 3:
            del freqs[nghd]

    for nghd in freqs:
        nghd_count += 1
        total_num_emojis = len(freqs[nghd])
        #doing TF= num of times an emoji appears in list/total emojis in list
        TF[nghd] = {}
        for emoji in freqs[nghd]:
            IDF[emoji] += 1
            TF[nghd][emoji] = freqs[nghd][emoji]/float(total_num_emojis)
    print "done with TF"

    #doing IDF=log_e(total num of nghds/num of nghds with emoji x in it)
    for emoji in IDF:
        IDF[emoji] = math.log(float(nghd_count)/IDF[emoji])
    print "done with IDF"

    for nghd in TF:
        TFIDF[nghd] = {}
        TFIDF[nghd]["top emojis"] = []
        TFIDF[nghd]["emoji data"] = {}
        for emoji in TF[nghd]:
            TFIDF[nghd]["emoji data"][emoji] = {}
            TFIDF[nghd]["emoji data"][emoji]["count"] = freqs[nghd][emoji]
            TFIDF[nghd]["emoji data"][emoji]["TF"] = TF[nghd][emoji]
            TFIDF[nghd]["emoji data"][emoji]["IDF"] = IDF[emoji]
            TFIDF[nghd]["emoji data"][emoji]["TFIDF"] = TF[nghd][emoji] * IDF[emoji]

        #sort the set by TFIDF
        TFIDF[nghd]["emoji data"] = sorted(TFIDF[nghd]["emoji data"].items(),\
                                 key=lambda item:item[1]["TFIDF"], reverse=True)

        #only keep top 3 words
        TFIDF[nghd]["emoji data"] = TFIDF[nghd]["emoji data"][:3]

        #add top 3 words to list (highest TFIDF)
        for i in range(3):
            if len(TFIDF[nghd]["emoji data"])>=i+1:
                TFIDF[nghd]["top emojis"].append(TFIDF[nghd]["emoji data"][i][0])

        print "done with " + nghd +" TFIDF"
    print "done with TFIDF"

    print "writing to JSON file"
    with open('outputs/nghd_emojis.json','w') as outfile:
        json.dump(TFIDF, outfile)

if __name__ == '__main__':
    cProfile.run("run_all()")
