#!/usr/bin/env python
# coding: utf-8

#Computes the top 10 tweeted words per neighborhood using TF-IDF

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

    psql_conn = psycopg2.connect("dbname='tweet'")
    psycopg2.extras.register_hstore(psql_conn)
    pg_cur = psql_conn.cursor(cursor_factory=psycopg2.extras.DictCursor)

    pg_cur.execute("SELECT text,ST_ASGEOJSON(coordinates) FROM tweet_pgh;")

    print "done with accessing tweets from postgres"
    
    nghd_count = 0
    freqs = defaultdict(lambda: defaultdict(int)) #freqs[nghd][word]
    TF = {}
    IDF = defaultdict(int)
    TFIDF = {}

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
    
        tweet = row[0]
        #replace curly double quotes with normal double quotes
        tweet = tweet.replace('“','"').replace('”','"')
        tweet = unicode(tweet, errors='ignore')
        wordList = twokenize.tokenize(tweet)
        
        #case where tweet is "@personTweeting: sometext" replytext
        #remove @personTweeting
        if wordList!=[] and wordList[0].startswith('"@'):
            wordList.pop(0)
                  
        '''#if 1st word in the tweet is a twitter handle, remove it
        if wordList!=[] and wordList[0]!='':
            if list(wordList[0])[0]=='@':
                #case where tweet is "@personTweetedAt some text"
                print "1st case"    
                wordList.pop(0)'''
 
        for word in wordList:
            #remove any usernames and html urls
            if not word.startswith('@') and not word.startswith('http'):
                freqs[nghd][word] += 1
            
    print "finished with all tweets"

    for nghd in freqs:
        nghd_count += 1
        total_num_words = len(freqs[nghd])
        #doing TF= num of times a word appears in list/total words in list
        TF[nghd] = {}
        for word in freqs[nghd]: 
            IDF[word] += 1
            TF[nghd][word] = freqs[nghd][word]/float(total_num_words)
    print "done with TF"

    #doing IDF=log_e(total num of nghds/num of nghds with word w in it)
    for word in IDF:
        IDF[word] = math.log(float(nghd_count)/IDF[word])
    print "done with IDF"

    for nghd in TF:
        TFIDF[nghd] = {}
        TFIDF[nghd]["top words"] = []
        TFIDF[nghd]["word data"] = {}
        for word in TF[nghd]:
            TFIDF[nghd]["word data"][word] = {}
            TFIDF[nghd]["word data"][word]["count"] = freqs[nghd][word]
            TFIDF[nghd]["word data"][word]["TF"] = TF[nghd][word]
            TFIDF[nghd]["word data"][word]["IDF"] = IDF[word]
            TFIDF[nghd]["word data"][word]["TFIDF"] = TF[nghd][word] * IDF[word]
        
        #sort the set by TFIDF
        TFIDF[nghd]["word data"] = sorted(TFIDF[nghd]["word data"].items(),\
                                 key=lambda item:item[1]["TFIDF"], reverse=True)

        #only keep top 10 words
        TFIDF[nghd]["word data"] = TFIDF[nghd]["word data"][:10]
 
        #add top 10 words to list (highest TFIDF)
        for i in range(10):
            if len(TFIDF[nghd]["word data"])>=i+1:
                TFIDF[nghd]["top words"].append(TFIDF[nghd]["word data"][i][0])

        print "done with " + nghd +" TFIDF"
    print "done with TFIDF"

    print "writing to JSON file"
    with open('outputs/nghd_words_no_usernames.json','w') as outfile:
        json.dump(TFIDF, outfile)

 
#if __name__ == '__main__':
#    cProfile.run("run_all()")
run_all()
