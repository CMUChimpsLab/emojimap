#!/usr/bin/env python

#Compiles all the emojis tweeted per bin and per neighborhood 
#as well as the most common emoji in each bin/neighborhood.
 
from collections import Counter, defaultdict
from csv import DictWriter, DictReader
import util.util, util.neighborhoods, argparse, pymongo, cProfile
from util.neighborhoods import get_neighborhood_or_muni_name
import json,ijson

def run_all():
    parser = argparse.ArgumentParser()
    parser.add_argument('--munis_file', '-m', default='geodata/Allegheny_Munis.json',
        help='GeoJSON file with Allegheny county municipal boundaries')
    parser.add_argument('--neighborhoods_file', '-n', default='geodata/Pittsburgh_Neighborhoods.json',
        help='GeoJSON file with neighborhood boundaries')
    parser.add_argument('--point_map_file', '-p', default='point_map.csv')
    parser.add_argument('--neighborhoods_outfile', default='outputs/nghds_emojis_no_duplicates.csv')
    parser.add_argument('--bins_outfile', default='outputs/bins_emojis_no_duplicates.csv')
    
    parser.add_argument('--tweets_json_file', default='emoji_tweets.json')
 
    args = parser.parse_args()

    nghds = util.neighborhoods.load_nghds(args.neighborhoods_file)
    munis = util.neighborhoods.load_allegheny_munis(args.munis_file)
    print "loaded Pittsurgh neighborhood boundaries"

    # Build up the bins-to-nghds mapping so we can easily translate.
    bins_to_nghds = {}
    for line in DictReader(open(args.point_map_file)):
        bins_to_nghds[(float(line['lat']), float(line['lon']))] = line['nghd']

    bin_tweets = Counter()
    bin_emojis = defaultdict(list)
    nghd_tweets = Counter()
    nghd_emojis = defaultdict(list)

    nghds_writer = DictWriter(open(args.neighborhoods_outfile, 'w'),
        ['nghd', 'num_tweets', 'all_emojis','most_common_emoji'])
    nghds_writer.writeheader()
    bins_writer = DictWriter(open(args.bins_outfile, 'w'),
        ['lat', 'lon', 'num_tweets', 'all_emojis','most_common_emoji'])
    bins_writer.writeheader()

    print "loading tweets"

    #db = pymongo.MongoClient('localhost', 27017)['tweet']
    all_tweets = ijson.items(open(args.tweets_json_file,'r'),'item')

    print "loaded all tweets"

    counter = 0
    for tweet in all_tweets:
        counter += 1
        if (counter % 1000) == 0:
            print str(counter) + ' tweets processed'
        coords = tweet['coordinates']['coordinates']
        bin = util.util.round_latlon(coords[1], coords[0])
        bin_tweets[bin] += 1

        #remove duplicate emojis within tweet
        filteredEmojiList = list(set(tweet['emoji'].split(',')))
        #filteredEmojiString = ','.join(filteredEmojiList)
        for emoji in filteredEmojiList:
            bin_emojis[bin].append(emoji)

        if bin in bins_to_nghds:
            nghd = bins_to_nghds[bin]
        else:
            nghd = 'Outside Pittsburgh'
        nghd_tweets[nghd] += 1
        for emoji in filteredEmojiList:
            nghd_emojis[nghd].append(emoji)
  
    print "added emojis to dictionary"
 
    def findMostCommonEmoji(emojiList):
        #emojiString = ','.join(tweets)
        #emojiList = emojiString.split(',')
        return max(set(emojiList),key=emojiList.count).encode('utf-8')
 
    for nghd in nghd_tweets:
        nghds_writer.writerow({'nghd': nghd, 'num_tweets': nghd_tweets[nghd],
            'all_emojis': nghd_emojis[nghd],
            'most_common_emoji': findMostCommonEmoji(nghd_emojis[nghd])})
    for bin in bin_tweets:
        bins_writer.writerow({'lat': bin[0], 'lon': bin[1],
            'num_tweets': bin_tweets[bin], 'all_emojis': bin_emojis[bin],
            'most_common_emoji':findMostCommonEmoji(bin_emojis[bin])})

if __name__ == '__main__':
    cProfile.run("run_all()")
