Data in this directory is in the form of geojson files and directories of
shapefiles.

Pittsburgh_Neighborhoods contains info about Pittsburgh neighborhoods.
neighborhoods. Original shapefiles from http://pittsburghpa.gov/dcp/gis/gis-data

Pittsburgh_City_Boundary is a shapefile for just the boundary of the city of
Pittsburgh. In case that's important. From the same place as Pittsburgh_Neighborhoods.

Allegheny_Munis is municipal boundaries in Allegheny County. From here:
http://www.pasda.psu.edu/uci/SearchResults.aspx?originator=Allegheny%20County&Keyword=&searchType=originator&entry=PASDA&sessionID=3935708482013101611143
(which I got to from here: http://www.alleghenycounty.us/dcs/gis/available.aspx )

Pittsburgh_Blocks is census blocks (the smallest unit)
Pittsburgh_Block_Groups is census block groups (bigger than a block).
Pittsburgh_Tracts is census tracts (bigger than a block group).

geojson files created using ogr2ogr, as in this d3 demo: http://bost.ocks.org/mike/map/
example command:
ogr2ogr -f GeoJSON -t_srs EPSG:4326 neighborhoods.json Pittsburgh_Neighborhoods/Neighborhood.shp
(the -t_srs EPSG:4326 is magic to me, it changes things from whatever gridded
coordinate mumbo jumbo into regular old lat/lon - I think it’s the same as -t_srs crs:84)
