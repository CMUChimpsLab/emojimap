#!/usr/bin/env python

#Computes the top 3 tweeted words per neighborhood using TF-IDF

import cProfile,json,string,math
from csv import DictReader
from collections import defaultdict, Counter
import util.util
import psycopg2, psycopg2.extras, ppygis

def run_all():
    #Build up the bins-to-nghds mapping so we can easily translate.
    bins_to_nghds = {}
    for line in DictReader(open('point_map.csv')):
        bins_to_nghds[(float(line['lat']), float(line['lon']))] = line['nghd']


    psql_conn = psycopg2.connect("dbname='tweet'")
    psycopg2.extras.register_hstore(psql_conn)
    pg_cur = psql_conn.cursor(cursor_factory=psycopg2.extras.DictCursor)

    #TODO:reduce memory usage so I don't have to limit 3000000
    pg_cur.execute("SELECT text,ST_ASGEOJSON(coordinates) FROM tweet_pgh limit 3000000;")

    print "done with accessing tweets from postgres"
    
    words_per_nghd = defaultdict(list) #indexed by nghd
    nghd_count = 0
    freqs = {}
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
    
        #take out punctuation
        exclude = set(string.punctuation)
        exclude.remove('@') #keep the @s
        tweet = row[0]
        tweet = ''.join(ch for ch in tweet if ch not in exclude)
        wordList = tweet.split(" ")
        #if 1st word in the tweet is a twitter handle, remove it
        if wordList!=[] and wordList[0]!='':
            if list(wordList[0])[0]=='@':
                wordList.pop(0)
        for word in wordList:
            words_per_nghd[nghd].append(word.lower())
            
    print "finished with all tweets"

    for nghd in words_per_nghd:
        nghd_count += 1
        #count number of times each word appears in the list
        freqs[nghd] = Counter(words_per_nghd[nghd])
        total_num_words = len(freqs[nghd])
        #doing TF= num of times a word appears in list/total words in list
        TF[nghd] = {}
        for word in freqs[nghd]: 
            IDF[word] += 1
            TF[nghd][word] = freqs[nghd][word]/float(total_num_words)
        #print "done with " + nghd + " TF"
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

        #TODO: clear up memory here

        print "done with " + nghd +" TFIDF"
    print "done with TFIDF"

    print "writing to JSON file"
    with open('outputs/nghd_words.json','w') as outfile:
        json.dump(TFIDF, outfile)

 
#if __name__ == '__main__':
#    cProfile.run("run_all()")
run_all()
