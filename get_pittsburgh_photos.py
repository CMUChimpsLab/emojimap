#!/usr/bin/env python

#From flickr 100M CC photos, get the photos that are in Pittsburgh
import csv,sys
from csv import DictReader, DictWriter
import argparse
import util.util

csv.field_size_limit(sys.maxsize)

parser = argparse.ArgumentParser()
parser.add_argument('--flickr_photo_file', '-f', default='/data/flickr_100M_CC_photos/yfcc100m_dataset-0')
args = parser.parse_args()

#pittsburgh bin to nghd mapping
bins_to_nghds = {}
for line in DictReader(open('point_map.csv')):
    bins_to_nghds[(float(line['lat']), float(line['lon']))] = line['nghd']

counter = 0
with open(args.flickr_photo_file) as tsv:
    for line in csv.reader(tsv, dialect="excel-tab"): #line is a list
        counter += 1
        if (counter % 1000000) == 0:
            print str(counter) + ' photos processed'
        lat = line[11]
        lon = line[10]
        if lat=='' or lon=='':
            #photo is not geotagged :(
            continue
        bin = util.util.round_latlon(lat,lon)
        if bin in bins_to_nghds: 
            #photo is in pittsburgh!        
            nghd = bins_to_nghds[bin]
        else:
            #don't care about this photo
            continue
        with open("/data/flickr_100M_CC_photos/pittsburgh_photos", "a") as myfile:
            myfile.write(nghd + '\t' + '\t'.join(line) + "\n")
