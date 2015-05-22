#!/usr/bin/env python

#Computes the central coordinate point of each neighborhood 
#for visualization purposes. 
 
from collections import Counter, defaultdict
import csv,sys
from csv import DictWriter, DictReader
import cProfile

def run_all():

    csv.field_size_limit(sys.maxsize)

    nghds_to_bins = defaultdict(list)
    for line in DictReader(open('point_map.csv')):
        nghds_to_bins[line['nghd']].append([float(line['lat']),
                                            float(line['lon'])])

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
