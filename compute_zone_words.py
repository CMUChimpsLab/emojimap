#!/usr/bin/env python
# coding: utf-8

#For each zone (http://pittsburghpa.gov/police/zones), computes the top 10
#tweeted words using TF-IDF

import cProfile,json,string,math
from csv import DictReader
from collections import defaultdict
import util.util
import psycopg2, psycopg2.extras, ppygis
import twokenize

def run_all():
 
    #Build up the bins-to-nghds mapping so we can easily translate.
    bins_to_nghds = {}
    for line in DictReader(open('point_map.csv')):
        bins_to_nghds[(float(line['lat']), float(line['lon']))] = line['nghd']
    #get nghd to zone mapping
    nghds_to_zones = {}
    for line in DictReader(open('zone_map.csv')):
        nghds_to_zones[line['nghd']] = line['zone']

    psql_conn = psycopg2.connect("dbname='tweet'")
    psycopg2.extras.register_hstore(psql_conn)
    pg_cur = psql_conn.cursor(cursor_factory=psycopg2.extras.DictCursor)

    pg_cur.execute("SELECT text,ST_ASGEOJSON(coordinates),user_screen_name FROM tweet_pgh;")

    print "done with accessing tweets from postgres"
    
    zone_count = 6
    freqs = defaultdict(lambda: defaultdict(int)) #freqs[nghd][word]
    TF = {}
    IDF = defaultdict(int)
    TFIDF = {}
    uniq_users_per_word = defaultdict(lambda: defaultdict(set))
                #uniq_users_per_word[nghd][word]
    entropy = defaultdict(lambda: defaultdict(int))

    counter = 0
    for row in pg_cur:
        counter += 1
        if (counter % 10000) == 0:
            print str(counter) + ' tweets processed'
        coords = json.loads(row[1])['coordinates']
        bin = util.util.round_latlon(coords[1],coords[0])
        if bin in bins_to_nghds:
            nghd =  bins_to_nghds[bin]
        else:
            nghd = 'Outside Pittsburgh'
        username = row[2]
    
        tweet = row[0]
        #replace curly double quotes with normal double quotes
        tweet = tweet.replace('“','"').replace('”','"')
        tweet = unicode(tweet, errors='ignore')
        wordList = twokenize.tokenize(tweet)
        
        #case where tweet is "@personTweeting: sometext" replytext
        #remove @personTweeting
        if wordList!=[] and wordList[0].startswith('"@'):
            wordList.pop(0)
                  
        for word in wordList:
            #remove any usernames and html urls
            if not word.startswith('@') and not word.startswith('http'):
                #map nghd to zone if possible - if not, it's a bourough/township
                if nghd in nghds_to_zones:
                    zone = "Zone " + nghds_to_zones[nghd]
                    freqs[zone][word.lower()] += 1
                    uniq_users_per_word[zone][word.lower()].add(username)
                else:
                    freqs[nghd][word.lower()] += 1
                    uniq_users_per_word[nghd][word.lower()].add(username)
            
    print "finished with all tweets"

    for zone in uniq_users_per_word:
        for word in uniq_users_per_word[zone]:
            num_uniq_users = len(uniq_users_per_word[zone][word])
            if num_uniq_users < 5:
                entropy[zone][word] = 0
            else:
                entropy[zone][word] = 1
    
            if entropy[zone][word]==0:
                del freqs[zone][word]
                del entropy[zone][word]
            uniq_users_per_word[zone][word].clear()
        uniq_users_per_word[zone].clear()
    print "done with entropy"

    for zone in freqs:
        total_num_words = len(freqs[zone])
        #doing TF= num of times a word appears in list/total words in list
        TF[zone] = {}
        for word in freqs[zone]: 
            IDF[word] += 1
            TF[zone][word] = freqs[zone][word]/float(total_num_words)
    print "done with TF"

    #doing IDF=log_e(total num of nghds/num of nghds with word w in it)
    for word in IDF:
        IDF[word] = math.log(float(zone_count)/IDF[word])
    print "done with IDF"

    for zone in TF:
        TFIDF[zone] = {}
        TFIDF[zone]["top words"] = []
        TFIDF[zone]["word data"] = {}
        for word in TF[zone]:
            TFIDF[zone]["word data"][word] = {}
            TFIDF[zone]["word data"][word]["count"] = freqs[zone][word]
            TFIDF[zone]["word data"][word]["TF"] = TF[zone][word]
            TFIDF[zone]["word data"][word]["IDF"] = IDF[word]
            TFIDF[zone]["word data"][word]["TFIDF"] = TF[zone][word] * IDF[word]
            TFIDF[zone]["word data"][word]["entropy"] = entropy[zone][word]
            #score = TFIDF * entropy
            TFIDF[zone]["word data"][word]["score"] = \
                TFIDF[zone]["word data"][word]["TFIDF"] * \
                TFIDF[zone]["word data"][word]["entropy"]
        
        #sort the set by score
        TFIDF[zone]["word data"] = sorted(TFIDF[zone]["word data"].items(),\
                                 key=lambda item:item[1]["score"], reverse=True)

        #only keep top 10 words
        TFIDF[zone]["word data"] = TFIDF[zone]["word data"][:10]
 
        #add top 10 words to a list (highest TFIDF)
        for i in range(10):
            if len(TFIDF[zone]["word data"])>=i+1:
                TFIDF[zone]["top words"].append(TFIDF[zone]["word data"][i][0])

        print "done with " + zone +" TFIDF"
    print "done with TFIDF"

    print "writing to JSON file"
    with open('outputs/zone_words.json','w') as outfile:
        json.dump(TFIDF, outfile)

 
#if __name__ == '__main__':
#    cProfile.run("run_all()")
run_all()
