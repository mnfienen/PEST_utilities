import numpy as np
import os
import sys
import pandas as pd
import xml.etree.ElementTree as ET
PEST_utils_path = '..'
if PEST_utils_path not in sys.path:
    sys.path.append(PEST_utils_path)
import PEST_utils as PSTu
import csv
from shapely.geometry import Point, mapping
from fiona import collection
import shutil

# get inputs from XML input file
infile = 'Postproc_input.XML'
try:
    inpardat = ET.parse(infile)
except:
    raise IOError("Cannot open {0}!".format(infile))

inpars = inpardat.getroot()

path = inpars.findall('.//path')[0].text
basename = inpars.findall('.//pest_basename')[0].text
inpst = os.path.join(path, '{0}.pst'.format(basename))
injco = os.path.join(path, '{0}.jco'.format(basename))
injac = os.path.join(path, '{0}.jac'.format(basename))
injco_txt = os.path.join(path, '{0}_jco.dat'.format(basename))
obs_locs = inpars.findall('.//observation_locations')[0].text
GIS_folder = inpars.findall('.//GIS_folder')[0].text
outshape = '{0}_inf.shp'.format(basename)
prj = inpars.findall('.//PRJfile')[0].text

print '\nRunning JACWRIT on {0} to convert to text...'.format(injco)
if not os.path.isfile(injco_txt):
    os.system('jacwrit {0} {1}'.format(injco, injco_txt))

print 'Getting observation info from {0}...'.format(inpst)
obsnames, obsval, obswt, obsgp = PSTu.obs_reader(inpst, regul=False)

print 'Reading converted jacobian {0}...'.format(injco_txt)
jac, parnames = PSTu.jac_reader(injco_txt, obsnames)

print 'Calculating leverage...'
lev_values = PSTu.lev_calc(jac, obswt)

levs = pd.DataFrame(data=lev_values.copy(), index=obsnames, columns=['observation leverage'])

print 'Reading in observation locations from {0}'.format(obs_locs)
obs_locs = pd.read_csv(obs_locs, index_col=0, names=['X', 'Y', 'type'])
obs_locs.index = [n.lower().strip() for n in obs_locs.index] # just in case there are spaces, case diff, etc.

# join locations with leverages, dropping any observations that aren't located (i.e. regularisation) or that aren't in the model
joined = levs.join(obs_locs, how='inner')


# if you wanted to do a bar chart
# levss = levs.sort(columns='observation leverage', ascending=False)
# levss[0:50].plot(kind = 'bar')

# now writeout observation leverage to shapefiles
# stole this code from http://www.macwright.org/2012/10/31/gis-with-python-shapely-fiona.html
# names must be shorter than shapefile character limit!
schema = {'geometry': 'Point', 'properties': {'obsname': 'str', 'type': 'str', 'leverage': 'float'}}

shpname = os.path.join(path, GIS_folder, outshape)
print '\nwriting output to {0}...'.format(shpname)
with collection(shpname, "w", "ESRI Shapefile", schema) as output:
    for row in joined.index:
        try:
            # get coordinates from points tpl data using pp name
            X = joined.ix[row]['X']
            Y = joined.ix[row]['Y']
            point = Point(X, Y)
            output.write({'properties': {'obsname': joined.ix[row].name,
                                         'type': joined.ix[row]['type'],
                                         'leverage': joined.ix[row]['observation leverage']},
                          'geometry': mapping(point)})
        except KeyError: # skip parameters that aren't pilot points
            continue

# copy over projection file
shutil.copyfile(prj, os.path.join(path, GIS_folder, outshape[:-4]+'.prj'))