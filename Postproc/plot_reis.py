'''
residuals plotting for PEST

This depends on resid_proc which lives in REIripper

a m!ke@usgs joint
contact: mnfienen@usgs.gov

This script goes through all REI.# files in the current folder with the basecase name
in the filename and saves a separate set of files for each iteration.
'''
import xml.etree.ElementTree as ET
import numpy as np
import os
import sys
import pylab as plt
import REIripperCONSOL
from matplotlib.backends.backend_pdf import PdfPages

try:
    infile = sys.argv[1]
except:
    infile = 'Postproc_input.XML'

try:
    inpardat = ET.parse(infile)
except:
    raise IOError("Cannot open {0}!".format(infile))

inpars = inpardat.getroot()

# input
path = inpars.findall('.//path')[0].text
basecase = inpars.findall('.//pest_basename')[0].text
h_groups = [k.text for k in inpars.findall('.//head_residuals/keyword')]
f_groups = [k.text for k in inpars.findall('.//flux_residuals/keyword')]
pareto = inpars.findall('.//pareto')[0].text
groups_rei = inpars.findall('.//rei_w_groups')[0].text

if pareto.lower() == 'true':
    pareto = True
    groups_rei = inpars.findall('.//rei_w_groups')[0].text
else:
    pareto = False

# set flag for handling weights
remove_zero_wt = False
# set the base case - all <basecase>.rei.# files will be processed.

#basecase='badriver_svda'
#path=os.path.join('Opt3b')

# troll through the current directory and return a dictionary of all REI Files
os.chdir(path)
allfiles = os.listdir(os.getcwd())
reis = dict()
for cf in allfiles:
    if ((basecase in cf) and ('rei' in cf[-6:]) and (cf[-4:] != '.rei')):
        cind = int(cf.split('.')[-1])
        reis[cind] = cf

# if no numbered reis were found (from PEST iterations), plot base rei
if len(reis)==0:
    try:
        reis[0]='%s.rei' %(basecase)
    except IndexError:
        print "No REI files found in folder!"
        quit()
        
# need to get group names for the consolidated files
if not pareto:
    alldat = np.genfromtxt(reis[reis.keys()[0]],names=True,skip_header=4,dtype=None)
else:
    alldat = np.genfromtxt(groups_rei,names=True,skip_header=4,dtype=None)
# find the unique list of groups by which plots and stats will be managed
allgrps = np.unique(alldat['Group'])
# discard regularisation observations
allgrps = [g for g in allgrps if 'regul' not in g]
# make a dictionary to contain a PDF output file handle for each group
grpfiles = dict()

# setup subfolders for histogram and one2one plots if they don't already exist
hist_folder='histograms'
one2one_folder='one2one_plots'
for dir in [hist_folder,one2one_folder]:
    if not os.path.exists(dir):
        os.makedirs(dir)

for cg in allgrps:
    grpfiles[cg] = [PdfPages(os.path.join(one2one_folder, basecase + "_" + cg + "_one2one.pdf")),
                    PdfPages(os.path.join(hist_folder, basecase + "_" + cg + "_histogram.pdf"))]

  
# doing this second loop is overkill, but consistent with the plot_bpas.py logic
# and doesn't waste too much time
#REIripperCONSOL.resid_proc(reis,remove_zero_wt,grpfiles)

outfile=PdfPages('all_heads_one2one.pdf')
#groups=['head_best','head_good','head_fair','wcrs1','head_poor','wcrs2']
markers=['^','s','o','+','o','+','+']
colors=['r','b','0.75','k','0.95','k','k']
title='Observed vs. simulated heads' # '' to use PEST iteration
units='ft'
sizes=[10,8,7,5,5,5,5]
Legend=True
number_format='' # '' for default
obstype = 'head' # head or flux
REIripperCONSOL.Best_summary_plot(reis, h_groups, markers, colors, sizes, title, units, number_format, Legend, outfile,
                                  obstype, pareto, groups_rei)

outfile=PdfPages('streams_one2one.pdf')
#groups=['bad_odanah','lrg_streams','streams']
markers=['o','o','o','o']
colors=['r','b','c','g']
title='Observed vs. simulated stream baseflows' # '' to use PEST iteration
units='ft3/d'
sizes=[8,8,8,8]
Legend=True
number_format='sci'
obstype = 'flux'
REIripperCONSOL.Best_summary_plot(reis, f_groups, markers, colors, sizes, title, units, number_format, Legend, outfile,
                                  obstype, pareto, groups_rei)
