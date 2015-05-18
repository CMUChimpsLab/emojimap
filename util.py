# Utility functions for working w/ tweets. Let's keep these well documented :-/
# Also, this is an attempt to impose some kind of consistency, etc.

from collections import Counter
import pytz, datetime

month_map = {'Jan': 1, 'Feb': 2, 'Mar':3, 'Apr':4, 'May':5, 'Jun':6, 'Jul':7, 
    'Aug':8,  'Sep': 9, 'Oct':10, 'Nov': 11, 'Dec': 12}

# Special case date parsing. All our dates are like this:
# Wed Jan 22 23:19:19 +0000 2014
# 012345678901234567890123456789
# so let's just parse them like that. 
def parse_date(d):
    return datetime.datetime(int(d[26:30]), month_map[d[4:7]], int(d[8:10]),\
        int(d[11:13]), int(d[14:16]), int(d[17:19]), 0, pytz.timezone('UTC')) # 0=usec

# Returns a list of tweets sorted by date.
def sort_tweets_by_date(tweets):
    return sorted(tweets, key=lambda t: parse_date(t['created_at']))

def has_valid_coordinates(tweet):
    if 'coordinates' not in tweet or tweet['coordinates'] == None:
        return False
    elif 'coordinates' not in tweet['coordinates']:
        return False
    elif tweet['coordinates']['coordinates'] == [0.0, 0.0]:
        return False
    else:
        return True

# Rounds lat and lon to 2 decimal places and returns a tuple of them both.
def round_latlon(lat, lon):
    if lat is None or lon is None:
        return (None, None)
    return (round(float(lat), 2), round(float(lon), 2))

# Given a list of tweets, counts them by coordinates and returns a Counter of
# those coordinates.
def make_coordinate_bins(tweets):
    with_coords = 0
    without_coords = 0
    bins = Counter()
    for tweet in tweets:
        if has_valid_coordinates(tweet):
            with_coords += 1
            coords = tweet['coordinates']['coordinates']
            lon = coords[0]
            lat = coords[1]
            bins[round_latlon(lat, lon)] += 1
        else:
            without_coords += 1
    # print 'Done binning: without coords: %d, with coords %d' % (with_coords, without_coords)
    return bins

# Given a list of tweets, returns a Counter of their neighborhoods.
def make_nghd_bins(tweets):
    bins = Counter()
    for tweet in tweets:
        # if 'neighborhood' not in tweet:
        #     print tweet
        bins[tweet['neighborhood']] += 1
    return bins

# Return the hour (from 0 to 23) that the tweet was in. (convert to US/Eastern
# time zone first.)
def get_tweet_hour(tweet):
    tweet_time_utc = parse_date(tweet['created_at'])
    tweet_time = tweet_time_utc.astimezone(pytz.timezone('US/Eastern')).time()
    return tweet_time.hour

# Return the day (from 0 (sun) to 6 (sat)) that the tweet was in. (convert to
# US/Eastern time zone first.)
def get_tweet_day(tweet):
    tweet_time_utc = parse_date(tweet['created_at'])
    tweet_day = tweet_time_utc.astimezone(pytz.timezone('US/Eastern')).weekday()
    return tweet_day
  
# Get whether it's "day" (9-5 weekdays) or "night" (everything else, including
# all weekends). (convert to US/Eastern in the process.)
def get_tweet_time(tweet):
    tweet_time_utc = parse_date(tweet['created_at'])
    tweet_time = tweet_time_utc.astimezone(pytz.timezone('US/Eastern')).time()
    tweet_day = tweet_time_utc.astimezone(pytz.timezone('US/Eastern')).weekday()
    # Python weekday(): 0=Mon, 4=Fri, 5=Sat, 6=Sun
    if tweet_day > 4 or tweet_time < datetime.time(9, 0, 0) or tweet_time > datetime.time(17, 0, 0):
        return 'night'
    else:
        return 'day'

SURVEY_LAST_DAY = parse_date('Fri Nov 07 00:00:00 +0000 2014')
# Returns number of days this was before the Survey Last Day.
def get_days_ago(tweet):
    tweet_time = parse_date(tweet['created_at'])
    delta = SURVEY_LAST_DAY - tweet_time
    return delta.days

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

def shrink_all(tweets):
    return [shrink(tweet) for tweet in tweets]


