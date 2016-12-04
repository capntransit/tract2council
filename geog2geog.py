import sys
import os
import json
import logging
import time
from shapely.geometry import Polygon

# http://toblerity.org/shapely/manual.html

loglevel = logging.DEBUG

LOG = logging.Logger(__name__)
LOG.addHandler(logging.StreamHandler())
LOG.setLevel(loglevel)

def addPoly(coords):
    polys = []
    if (isinstance(coords[0][0], float)):
        polys.append(Polygon(coords))
    else:
        for (c) in coords:
            polys.extend(addPoly(c))
    return polys

def overlap(geogname, poly1, geo2):
    poly2 = addPoly(geo2['geometry']['coordinates'])
    geo2num = geo2['properties'][geogname]
    LOG.info("overlap(" + geogname + ", poly1, " + geo2num + ")")

    intersects = set()
    area = 0
    intersection = {}
    iap = {}

    for (i) in range (0, len(poly2)):
        geo2polygon = poly2[i]
        LOG.debug("poly2[{}]".format(str(i)))
        LOG.debug(geo2polygon)
        area += geo2polygon.area
        for (dn, dp) in poly1.items():
            LOG.debug("poly1[{}]".format(dn))
            for (p) in dp:
                if (p.contains(geo2polygon)):
                    iap[dn] = 1
                    break;
                elif (p.intersects(geo2polygon)):
                    intersects.add(dn)
                    if dn not in intersection:
                        intersection[dn] = p.intersection(geo2polygon).area
                    else:
                        intersection[dn] += p.intersection(geo2polygon).area

    if (len(intersection) > 0):
        for (dn, inter) in intersection.items():
            iap[dn] = inter / area
    LOG.debug(iap)
    return (geo2num, iap)

if __name__ == '__main__':

    if (len(sys.argv) < 4):
        print("Usage: geog2geog.py geog1 geog2 file1.json file2.json")
        print("\n  geog1 and geog2 are the identifiers of the geographies in \
        the geoJSON files file1.json and file2.json")
        print("\n  e.g. geog2geog.py BCTCB2000 CounDist nycb2000.geojson \
        council2010a.json")
        exit()

    gname = sys.argv[1:3]
    file = sys.argv[3:5]
    indata = []
    geo2poly = {}
    contains = {}
    intersects = {}
    unmatched = []

    for i in (0, 1):
        index = 0
        if not os.path.isfile(file[i]):
            LOG.error("File " + file[i] + " is not readable or not found")
            exit()

        try:
           with open(file[i]) as fh:
                indata.append(json.load(fh))
                index = len(indata) - 1
        except Exception as e:
            LOG.exception("Unable to read file " + file[i])
            exit()

        LOG.info("there are " + str(
                len(indata[index]['features'])
            ) + " geographies in " + file[i])

    LOG.debug(indata[1]['features'])
    for (geo) in indata[1]['features']:
        dn = geo['properties'][gname[1]]
        LOG.debug("geo2poly[{}]".format(dn))
        poly = geo['geometry']['coordinates']
        geo2poly[dn] = addPoly(poly)
        LOG.debug(geo2poly[dn])

    LOG.info("Done loading features")

    for (geo) in indata[0]['features']:
        (tn, i) = overlap(gname[0], geo2poly, geo)
        intersects[tn] = i

    intersectsFile = 'tracts_' + str(round(time.time())) + '.json'

    with open(intersectsFile, 'w') as intersectsfo:
        json.dump(intersects, intersectsfo)

