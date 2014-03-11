# runs PEST identpar utility and plots results for pilot points
# pilot point tpl files must be named as points<layer>.tpl
# (e.g. points1.tpl)
# requires: pandas, fiona (for writing geospatial output), shapely (for generating shapefile)

__author__ = 'aleaf'

import xml.etree.ElementTree as ET
import os
import numpy as np
import pandas as pd
from fiona import collection
from shapely.geometry import Point, mapping
import shutil

# get inputs from XML input file
infile = 'Postproc_input.XML'
try:
    inpardat = ET.parse(infile)
except:
    raise IOError("Cannot open {0}!".format(infile))

inpars = inpardat.getroot()

path = inpars.findall('.//path')[0].text
GIS_folder = inpars.findall('.//GIS_folder')[0].text
basename = inpars.findall('.//pest_basename')[0].text

N = 300 # number of singular values defining the solution space
vecfilebase = 'null' # filename base to which eigencomponent sensitivity vectors are to be written
matfile = 'null' # matrix file to which the V1 matrix is to be written
identfile = 'BadRiver_ident.dat' # file to which parameter identifiability data are to be written
coords_mult = 0.3048 # convert from model units (in 'points' tpl files) to GIS units
prj = inpars.findall('.//PRJfile')[0].text
outshape = '{0}_PPident.shp'.format(basename) # output shapefile for plotting

# functions
def read_points_tpl(f):
    # read pilot point names and coordinates from points tpl file into pandas dataframe
    df = pd.read_csv(f, delim_whitespace=True, usecols=[0, 1, 2], dtype=None, header=0, names=['parname', 'X', 'Y'])
    df.index = [n.lower() for n in df['parname']]
    layer = int([c for c in f if c.isdigit()][0])
    df['layer'] = np.ones(len(df)) * layer
    if 'z' in f.lower():
        dir = 'kz'
    else:
        dir = 'kh'
    df['dir'] = [dir]*len(df)
    return df

# change dir to path folder and run identpar
print '\nrunning identpar...'
startdir = os.getcwd()
os.chdir(path)
if not os.path.isdir(GIS_folder):
    os.mkdir(GIS_folder)

if not os.path.isfile(identfile):
    os.system("identpar {0} {1} {2} {3} {4}".format(basename, N, vecfilebase, matfile, identfile))

print "reading {0} into pandas dataframe...".format(os.path.join(path, identfile))
df = pd.read_csv(identfile, delim_whitespace=True, index_col='parameter', dtype=None)
df.index.name = 'parameter'

# remove prefix from pilot point names for join with PP coordinates
df.index = [p[2:] for p in df.index]

print "getting pilot point coordinates from tpl files in {0}...".format(os.getcwd())
tpls = [f for f in os.listdir(os.getcwd()) if 'point' in f and f.endswith('.tpl')]

# initialize dataframe with first points tpl; append info from remaining tpls
points_df = read_points_tpl(tpls[0])
for tpl in tpls[1:]:
    print '{0}'.format(tpl)
    cdf = read_points_tpl(tpl)
    points_df = points_df.append(cdf)

# stole this code from http://www.macwright.org/2012/10/31/gis-with-python-shapely-fiona.html
# names must be shorter than shapefile character limit!
schema = {'geometry': 'Point', 'properties': {'parameter': 'str', 'dir': 'str', 'layer': 'int', 'ident': 'float'}}
shpname = os.path.join(path, GIS_folder, outshape)

print '\nwriting output to {0}...'.format(shpname)
with collection(shpname, "w", "ESRI Shapefile", schema) as output:
    for row in df.index:
        try:
            # get coordinates from points tpl data using pp name
            X = points_df.ix[row]['X'] * coords_mult
            Y = points_df.ix[row]['Y'] * coords_mult
            point = Point(X, Y)
            output.write({'properties': {'parameter': row,
                                         'dir': points_df.ix[row]['dir'],
                                         'layer': points_df.ix[row]['layer'],
                                         'ident': df.ix[row]['identifiability']},
                          'geometry': mapping(point)})
        except KeyError: # skip parameters that aren't pilot points
            continue

# copy prj file to GIS folder
shutil.copyfile(prj, os.path.join(path, GIS_folder, outshape[:-4]+'.prj'))

print 'Done!'

'''
# other code that could be used for arcpy or bar charts:

# save to csv
df.to_csv('identifiabilities.csv', cols=['identifiability'], index_label='parameter')

# copy pilot points shapefile and join with identifiabilities


# sort by most identifiable (descending)
df = df.sort(columns=['identifiability'], ascending=False)

# need to come up with a way to meaningfully plot out parameters with highest identifiabilities
# this line plots 10 most identifiable parameters, using eigenvectors 1 through 10
df.ix[0:10][df.columns[1:10]].plot(kind='bar', stacked=True)
'''

j=2
