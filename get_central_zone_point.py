#!/usr/bin/env python

#Computes the central coordinate point of each zone/borough/township 
#for visualization purposes. 
 
from collections import Counter, defaultdict
import csv,sys
from csv import DictWriter, DictReader
import cProfile

def run_all():

    csv.field_size_limit(sys.maxsize)

    nghds_to_zones = {}
    for line in DictReader(open('zone_map.csv')):
        nghds_to_zones[line['nghd']] = line['zone'] 

    nghd_central_points = {}
    for line in DictReader(open('nghd_central_point.csv')):
        nghd_central_points[line['nghd']] = [float(line['lat']),
                                             float(line['lon'])]

    #correct up to here

    #average lat points and on points
    nghds_to_centralPoint = defaultdict()
    for nghd in nghds_to_bins:
         if nghd!='Outside Pittsburgh':
            nghd_avg = defaultdict() 
            nghd_avg['count'] = 0.0
            nghd_avg['lat'] = 0.0
            nghd_avg['lon'] = 0.0
            for coord in nghds_to_bins[nghd]:
                lat = coord[0]
                lon = coord[1]
                nghd_avg['count']+=1.0
                nghd_avg['lat'] += lat
                nghd_avg['lon'] += lon
            nghds_to_centralPoint[nghd] = [float(nghd_avg['lat']/nghd_avg['count']),
                                      float(nghd_avg['lon']/nghd_avg['count'])]
       

    nghds_writer = DictWriter(open('nghd_central_point','w'),
        ['nghd', 'lat','lon'])
    nghds_writer.writeheader()

    for nghd in nghds_to_centralPoint:
        nghds_writer.writerow({'nghd': nghd, 
            'lat': nghds_to_centralPoint[nghd][0],
            'lon': nghds_to_centralPoint[nghd][1]})

if __name__ == '__main__':
    cProfile.run("run_all()")
