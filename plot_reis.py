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
import pylab as plt
from REIripper import resid_proc


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

# doing this second loop is overkill, but consistent with the plot_bpas.py logic
# and doesn't waste too much time   
for cf in np.arange(len(reis)):
    resid_proc(reis[cf],remove_zero_wt)
