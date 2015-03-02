#!/usr/bin/env python

# Looping over all tweets in a collection is expensive, so let's try to only do
# it once.

import argparse, pymongo, csv, datetime, json
from collections import Counter

# Returns a "shrunken" tweet that doesn't have a lot of the garbage that we
# don't need. Shrinks the total final file size.
def shrink(tweet):
    new_tweet = {}
    for field in ['coordinates', 'created_at', 'id',
            'in_reply_to_status_id', 'in_reply_to_screen_name',
            'lang', 'place', 'retweet_count', 'retweeted', 'source', 'text']:
        new_tweet[field] = tweet[field]
    new_tweet['user'] = {'screen_name': tweet['user']['screen_name']}
    return new_tweet

# Returns all the emoji in this string.
def get_emoji(text):
    return text
    # for char in text:

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--city', '-c', 
        help='Which city to get data from.', default='pgh',
        choices=['pgh', 'sf', 'ny', 'chicago', 'houston', 'detroit', 'miami',
        'cleveland', 'seattle', 'london'])
    parser.add_argument('--limit', '-l', type=int, default=10000)
    parser.add_argument('--outfile', '-o', default='emoji_tweets.json')
    args = parser.parse_args()
    dir = 'descriptive_stats/outputs/'

    db = pymongo.MongoClient('localhost', 27017)['tweet']
    coll = db['tweet_' + args.city]

    emoji_tweets = []
    counter = 0 # hah
    total = coll.count()
    for tweet in coll.find().limit(args.limit):
        emoji = get_emoji(tweet['text'])
        if emoji != '':
            new_tweet = shrink(tweet)
            # new_tweet['emoji'] = tweet['emoji']
            emoji_tweets.append(new_tweet)

        counter += 1
        if counter % 1000 == 0:
            print 'Tweets processed: %d out of %d' % (counter, total)

    json.dump(emoji_tweets, open(args.outfile, 'w'), indent=2)
