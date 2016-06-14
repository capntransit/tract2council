# tract2council
This script creates a mapping between US census tracts and political districts.

It takes as input two GeoJSON files representing census tracts and political districts, such as [those produced by New York's City Planning Department](http://www1.nyc.gov/site/planning/data-maps/open-data/districts-download-metadata.page), and uses [Shapely](http://toblerity.org/shapely/manual.html) to find which districts contain or intersect with each tract.

The output is a JSON file containing an object of census tracts.  Each pair in the object consists of the census tract's "BoroCT" number (see below) and an object containing each district that intersects with it.  In that object, each pair consists of the district number and the fraction of the tract (by area) that it intersects.

For example, roughly the three-quarters of Census tract 532 south of Avenue I in Brooklyn is in City Council District 44 (currently represented by David Greenfield) and the rest is in District 45 (represented by Jumaane Williams):

```json
"3053200": {"44": 0.7505059291747771, "45": 0.2494940708250868}
```
All of Census tract 146.01 on Manhattan's Upper East Side is in City Council District 5 (represented by Ben Kallos):

```json
"1014601": {"5": 1}
```

The US Census does not produce tables by New York City Council district, so the output JSON file can be used to tabulate population features in this way.

## BoroCT conversion
The BoroCT codes used by the New York Department of City Planning take the following format:

* A single-digit code representing the borough, as follows:

Borough | County | FIPS Code | BoroCT Code
------- | ------ | --------- | -----------
Manhattan | New York | 61 | 1
Bronx | Bronx | 05 | 2
Brooklyn | Kings | 47 | 3
Queens | Queens | 81 | 4
Staten Island | Richmond | 85 | 5

* A four digit census tract number, zero-padded
* A two-digit sub-tract number (00 if there is no sub-tract)
