#!/usr/bin/env python
# coding: utf-8

#Computes the top 10 tweeted words per neighborhood using TF-IDF and entropy

#The more common and unique a term is to a nghd compared to other nghds, the
#higher the TF-IDF
#The more distributed a term is across users, the higher the entropy.

import cProfile,json,string,math,gc
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
    top_100_english_words = []
    for line in open('top_100_english_words.txt'):
        top_100_english_words.append(line)

    psql_conn = psycopg2.connect("dbname='tweet'")
    psycopg2.extras.register_hstore(psql_conn)
    pg_cur = psql_conn.cursor(cursor_factory=psycopg2.extras.DictCursor)

    pg_cur.execute("SELECT text,ST_ASGEOJSON(coordinates),user_screen_name FROM tweet_pgh;")

    print "done with accessing tweets from postgres"
    
    nghd_count = 0
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
        
        for word in wordList:
            #don't include if a single letter
            if len(word)==1:
                continue
            #don't include if it's punctation marks
            if all(char in string.punctuation for char in word):
                continue
            #take out top 100 english words
            if word in top_100_english_words:
                continue
            #<3 becomes &lt;3 -> ['&','lt',';3'] after twokenize
            if word=='lt' or word=='&lt;' or word=='gt' or word=='&gt;' \
            or word==';3' or word=='rt' or word=='#rt' or word=='ur' \
            or word=='w/' or word==':d' or word=='im' or word=="i'm":
                continue            
            #remove any usernames and html urls
            if word.startswith('@') or words.startswith('http'):
                continue

            freqs[nghd][word.lower()] += 1
            uniq_users_per_word[nghd][word.lower()].add(username)
    print "finished with all tweets"

    for nghd in uniq_users_per_word:
        for word in uniq_users_per_word[nghd]:
            num_uniq_users = len(uniq_users_per_word[nghd][word])

            '''#Version 1: TFIDF * log(N)
            entropy[nghd][word] =  math.log(num_uniq_users,2) #log base 2
                #if word tweeted by only 1 person, entropy = log2(1) = 0'''
            
            '''#Version 2: TFIDF * <5 ppl=0,>5 ppl=log(N)
            if num_uniq_users < 5:
                entropy[nghd][word]=0
            else:
                entropy[nghd][word] = math.log(num_uniq_users,2) #Log base 2'''

            '''#Version 3: TFIDF * <5 ppl=0,>5 ppl=N
            if num_uniq_users < 5:
                entropy[nghd][word] = 0
            else:
                entropy[nghd][word] = num_uniq_users
            #overpowers TFIDF too much''' 

            #Version 4: TFIDF >5 only
            if num_uniq_users < 5:
                entropy[nghd][word] = 0
            else:
                entropy[nghd][word] = 1            

            if entropy[nghd][word]==0:
                #only care about words tweeted by at least __ # of people 
                del freqs[nghd][word]
                del entropy[nghd][word] 
            uniq_users_per_word[nghd][word].clear()
        uniq_users_per_word[nghd].clear()
    print "done with entropy"

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
            TFIDF[nghd]["word data"][word]["entropy"] = entropy[nghd][word]
            #score = TFIDF * entropy
            TFIDF[nghd]["word data"][word]["score"] = \
                TFIDF[nghd]["word data"][word]["TFIDF"] * \
                TFIDF[nghd]["word data"][word]["entropy"] 
        
        #sort the set by score
        TFIDF[nghd]["word data"] = sorted(TFIDF[nghd]["word data"].items(),\
                                 key=lambda item:item[1]["score"], reverse=True)

        #only keep top 10 words
        TFIDF[nghd]["word data"] = TFIDF[nghd]["word data"][:10]
 
        #add top 10 words to list (highest TFIDF)
        for i in range(10):
            if len(TFIDF[nghd]["word data"])>=i+1:
                TFIDF[nghd]["top words"].append(TFIDF[nghd]["word data"][i][0])

        print "done with " + nghd +" TFIDF"
    print "done with TFIDF"

    print "writing to JSON file"
    with open('outputs/nghd_words.json','w') as outfile:
        json.dump(TFIDF, outfile)

 
if __name__ == '__main__':
    cProfile.run("run_all()")
