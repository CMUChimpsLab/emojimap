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

    pg_cur.execute("SELECT text,ST_ASGEOJSON(coordinates) FROM tweet_pgh;")

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
        for word in tweet.split(" "):
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
    print "done with TF"

    #doing IDF=log_e(total num of nghds/num of nghds with word w in it)
    for word in IDF:
        IDF[word] = math.log(float(nghd_count)/IDF[word])
    print "done with IDF"

    for nghd in TF:
        TFIDF[nghd] = {}
        TFIDF[nghd]["top words"] = []
        TFIDF[nghd]["all words"] = {}
        for word in TF[nghd]:
            TFIDF[nghd]["all words"][word] = {}
            TFIDF[nghd]["all words"][word]["count"] = freqs[nghd][word]
            TFIDF[nghd]["all words"][word]["TFIDF"] = TF[nghd][word] * IDF[word]
        
        #sort the set
        TFIDF[nghd]["all words"] = sorted(TFIDF[nghd]["all words"].items(),\
                                 key=lambda item:item[1], reverse=True)
 
        #add top 3 words (highest TFIDF)
        if len(TFIDF[nghd]["all words"])>=1:
            TFIDF[nghd]["top words"].append(TFIDF[nghd]["all words"][0][0])
        if len(TFIDF[nghd]["all words"])>=2:
            TFIDF[nghd]["top words"].append(TFIDF[nghd]["all words"][1][0])
        if len(TFIDF[nghd]["all words"])>=3:
            TFIDF[nghd]["top words"].append(TFIDF[nghd]["all words"][2][0])
        if len(TFIDF[nghd]["all words"])>=4:
            TFIDF[nghd]["top words"].append(TFIDF[nghd]["all words"][3][0])
        if len(TFIDF[nghd]["all words"])>=5:
            TFIDF[nghd]["top words"].append(TFIDF[nghd]["all words"][4][0])

        print "done with " + nghd +" TFIDF"
    print "done with TFIDF"

    print "writing to JSON file"
    with open('outputs/nghd_words.json','w') as outfile:
        json.dump(TFIDF, outfile)

 
#if __name__ == '__main__':
#    cProfile.run("run_all()")
run_all()
