
# Utility functions to deal with neighborhood things.

import shapely.geometry, geojson

# TODO this is all kinds of global crap where you have to call load_nghds first
# and is kind of awful, we should, uh, change this I guess
pittsburgh_outline = None
allegheny_outline = None

def load_nghds(neighborhoods_filename):
    neighborhoods = geojson.load(open(neighborhoods_filename))
    nghds = neighborhoods['features']
    for nghd in nghds:
        nghd['shape'] = shapely.geometry.asShape(nghd.geometry)
    global pittsburgh_outline
    pittsburgh_outline = nghds[0]['shape']
    for nghd in nghds:
        pittsburgh_outline = pittsburgh_outline.union(nghd['shape'])
    return nghds
    # TODO return pittsburgh_outline too
    # return [shapely.geometry.asShape(nghd) for nghd in neighborhoods['features']]

def load_allegheny_munis(allegheny_munis_file):
    munis = geojson.load(open(allegheny_munis_file))['features']
    for muni in munis:
        muni['shape'] = shapely.geometry.asShape(muni['geometry'])
    global allegheny_outline
    allegheny_outline = munis[0]['shape']
    for muni in munis:
        allegheny_outline = allegheny_outline.union(muni['shape'])
    return munis

# this takes a lot of runtime.
def get_neighborhood_name(nghds, lon, lat):
    global pittsburgh_outline # TODO ugh globals
    if pittsburgh_outline == None:
        pittsburgh_outline = nghds[0]['shape']
        for nghd in nghds:
            pittsburgh_outline = pittsburgh_outline.union(nghd['shape'])
         
    point = shapely.geometry.Point(lon, lat)
    if not pittsburgh_outline.contains(point):
        return 'Outside Pittsburgh'
    
    for nghd in nghds:
        if nghd['shape'].contains(point):
            # Move this nghd to the front of the queue so it's checked first next time
            nghds.remove(nghd)
            nghds.insert(0, nghd)
            return nghd.properties['HOOD']
    return 'Outside Pittsburgh'

def get_muni_name(munis, lon, lat):
    global allegheny_outline # TODO ugh globals
    if allegheny_outline == None:
        allegheny_outline = munis[0]['shape']
        for muni in munis:
            allegheny_outline = allegheny_outline.union(muni['shape'])
    point = shapely.geometry.Point(lon, lat)
    if not allegheny_outline.contains(point):
        return 'Outside Allegheny'
 
    for muni in munis:
        if muni['shape'].contains(point):
            # Move this muni to the front of the queue so it's checked first next time
            munis.remove(muni)
            munis.insert(0, muni)
            return muni.properties['LABEL']
    return 'Outside Allegheny'

def get_neighborhood_or_muni_name(nghds, munis, lon, lat):
    name = get_neighborhood_name(nghds, lon, lat)
    if name == 'Outside Pittsburgh':
        name = get_muni_name(munis, lon, lat)
    return name
