#!/usr/bin/env python3
# Python3 only! Because it can handle unicode astral characters.

# Loops over all tweets in the mongodb, makes a json file that is a list of
# minimized tweets
# it once.

import argparse, pymongo, csv, datetime, json, re
from collections import Counter

# Returns a "shrunken" tweet that doesn't have a lot of the garbage that we
# don't need. Shrinks the total final file size.
def shrink(tweet):
    new_tweet = {}
    for field in ['coordinates', 'created_at', 'id',
            'in_reply_to_status_id', 'in_reply_to_screen_name',
            'lang', 'retweet_count', 'retweeted', 'source', 'text']:
        new_tweet[field] = tweet[field]
    new_tweet['user'] = {'screen_name': tweet['user']['screen_name']}
    return new_tweet

emoji_symbols_pictograms = re.compile(u'[\U0001f300-\U0001f5fF]')
emoji_emoticons = re.compile(u'[\U0001f600-\U0001f64F]')
emoji_transport_maps = re.compile(u'[\U0001f680-\U0001f6FF]')
emoji_symbols = re.compile(u'[\U00002600-\U000026FF]')
emoji_dingbats = re.compile(u'[\U00002700-\U000027BF]')
all_emoji = re.compile(u'([\U00002600-\U000027BF]|[\U0001f300-\U0001f64F]|[\U0001f680-\U0001f6FF])')

# Returns all the emoji in this string. 'text' is a unicode string.
def get_emoji(text):
    emojis = all_emoji.findall(text)
    if len(emojis) > 0:
        return ','.join(emojis)
    else:
        return ''

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
    total = coll.count()
    counter = 0
    for tweet in coll.find().limit(args.limit):
        
        emoji = get_emoji(tweet['text'])
        if emoji != '':
            new_tweet = shrink(tweet)
            new_tweet['emoji'] = emoji
            emoji_tweets.append(new_tweet)

        counter += 1
        if counter % 1000 == 0:
            print('Tweets processed: %d out of %d' % (counter, total))

    print("Tweets: %d, emoji tweets: %d, percent with emoji: %.01f" % (total, len(emoji_tweets), len(emoji_tweets) * 100.0 / total))
    json.dump(emoji_tweets, open(args.outfile, 'w'), indent=2)
