import sys, os, json, time
from shapely.geometry import Polygon

# http://toblerity.org/shapely/manual.html

contains = {}
intersects = {}
dPoly = {}
unmatched = []
TRACTCOL = 'BoroCT2010' # rename this for 2000 census

def addPoly(coords):
    polys = []
    if (isinstance(coords[0][0], float)):
        polys.append(Polygon(coords))
    else:
        for (c) in coords:
            polys.extend(addPoly(c))
    return polys

def inDistrict(tract):
    tPoly = addPoly(tract['geometry']['coordinates'])
    tractNum = tract['properties'][TRACTCOL]

    intersects = set()
    area = 0
    intersection = {}
    iap = {}

    for (i) in range (0, len(tPoly)):
        tractPolygon = tPoly[i]
        area += tractPolygon.area
        for (dn, dp) in dPoly.items():
            for (p) in dp:
                if (p.contains(tractPolygon)):
                    iap[dn] = 1
                    break;
                elif (p.intersects(tractPolygon)):
                    intersects.add(dn)
                    if dn not in intersection:
                        intersection[dn] = p.intersection(tractPolygon).area
                    else:
                        intersection[dn] += p.intersection(tractPolygon).area

    if (len(intersection) > 0):
        for (dn, inter) in intersection.items():
            iap[dn] = inter / area
    return (tractNum, iap)

if __name__ == '__main__':

    if (len(sys.argv) < 2):
        print ("Usage: tract2council.py tract.json council.json")
        exit()

    tractfile = sys.argv[1]
    councilfile = sys.argv[2]

    for (f) in (tractfile, councilfile):
        if (not os.path.isfile(f)):
            print ("File " + f + " is not readable")
            exit()

    try:
       with open(tractfile) as tractfo:
           tractData = json.load(tractfo)
    except Exception:
        print ("Unable to read tract file " + tractfile)
        exit()

    try:
        with open(councilfile) as councilfo:
            councilData = json.load(councilfo)

    except Exception as e:
        print ("Unable to read council file " + councilfile+": {0}".format(e))
        exit()

    for (district) in councilData['features']:
        dn = district['properties']['CounDist']
        c = district['geometry']['coordinates']
        dPoly[dn] = addPoly(c)

    print ("there are " + str(len(tractData['features'])) + " census tracts")
    for (tract) in tractData['features']:
        (tn, i) = inDistrict(tract)
        intersects[tn] = i

    intersectsFile = 'tracts_' + str(round(time.time())) + '.json'

    with open(intersectsFile, 'w') as intersectsfo:
        json.dump(intersects, intersectsfo)

