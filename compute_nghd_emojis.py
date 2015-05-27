#!/usr/bin/env python

#Computes the top 3 emojis per neighborhood
 
from collections import Counter, defaultdict
import csv,ast
from csv import DictWriter, DictReader
#import util.util, util.neighborhoods, argparse, pymongo, cProfile
import cProfile,sys
from util.neighborhoods import get_neighborhood_or_muni_name

def run_all():

    csv.field_size_limit(sys.maxsize)
    nghd_emojis = {}
    emojis_in_nghd = {}

    def formatEmojiList(emojiList):
        #unstring
        emojiList = ast.literal_eval(emojiList)
        #fixing uneven grouping of emojis
        emojiString = ','.join(emojiList)
        emojiList_separated = emojiString.split(',') 
        return emojiList_separated


    for line in DictReader(open('outputs/nghds_emojis_no_duplicates.csv')):
        emojis_in_nghd[line['nghd']] = formatEmojiList(line['all_emojis'])
        nghd_emojis[line['nghd']] = []

    nghds_writer = DictWriter(open('outputs/nghds_emojis123_no_duplicates.csv','w'),
        ['nghd','first','second','third'])
    nghds_writer.writeheader()

    def findMostCommonEmoji(emojiList):
        mostcommon =  max(set(emojiList),key=emojiList.count)
        return mostcommon

    for k,v in emojis_in_nghd.items():
        #get 1st most common emoji
        nghd_emojis[k].append(findMostCommonEmoji(emojis_in_nghd[k]))
        #remove 1st most common emoji
        emojis_in_nghd[k] = [x for x in v if x!=nghd_emojis[k][0]]
        #get 2nd most common emoji
        nghd_emojis[k].append(findMostCommonEmoji(emojis_in_nghd[k]))
        #remove 2nd most common emoji from emoji list
        emojis_in_nghd[k] = [x for x in emojis_in_nghd[k] if x!=nghd_emojis[k][1]]
        #get 3rd most common emoji
        nghd_emojis[k].append(findMostCommonEmoji(emojis_in_nghd[k]))

    for nghd,emojis in nghd_emojis.items():
        nghds_writer.writerow({'nghd': nghd,
            'first': emojis[0].encode('utf-8'),
            'second': emojis[1].encode('utf-8'),
            'third': emojis[2].encode('utf-8')})

if __name__ == '__main__':
    cProfile.run("run_all()")
