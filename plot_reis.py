'''
residuals plotting for PEST

This depends on resid_proc which lives in REIripper

a m!ke@usgs joint
contact: mnfienen@usgs.gov

This script goes through all REI.# files in the current folder with the basecase name
in the filename and saves a separate set of files for each iteration.
'''

import numpy as np
import os
import sys
import pylab as plt
from REIripperCONSOL import resid_proc
from matplotlib.backends.backend_pdf import PdfPages


# set flag for handling weights
remove_zero_wt = True
# set the base case - all <basecase>.rei.# files will be processed.
basecase = 'assp3tr_sv28'
# troll through the current directory and return a dictionary of all REI Files
allfiles = os.listdir(os.getcwd())
reis = dict()
for cf in allfiles:
    if ((basecase in cf) and ('rei' in cf[-5:]) and (cf[-4:] != '.rei')):
        cind = int(cf.split('.')[-1])
        reis[cind] = cf

# need to get group names for the consolidated files
alldat = np.genfromtxt(reis[0],names=True,skip_header=6,dtype=None)
# find the unique list of groups by which plots and stats will be managed
allgrps = np.unique(alldat['Group'])

# make a dictionary to contain a PDF output file handle for each group
grpfiles = dict()
for cg in allgrps:
    grpfiles[cg] = [PdfPages(basecase + "_" + cg + "_one2one.pdf"),
                    PdfPages(basecase + "_" + cg + "_histogram.pdf")]
  
# doing this second loop is overkill, but consistent with the plot_bpas.py logic
# and doesn't waste too much time   
resid_proc(reis,remove_zero_wt,grpfiles)

