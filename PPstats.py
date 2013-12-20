# -*- coding: utf-8 -*-
"""
Created on Wed Dec 04 13:42:14 2013

@author: aleaf

reports summary statistics for pilot points

Requirements:
pilot point parameter names should contain two unique strings:
    - one identifying the parameter as a pilot point (e.g. "kp")
    - the other identifying the zone (or layer) to which it belongs (e.g. "ww")

These unique strings are supplied as input (see below)

Plotting TGUESS results:
assumes that the TGUESS files are all at the given path, one file per zone (corresponding to Pilot Point zones)
TGUESS files must be comma delimited with one header (names) line; 
with the K-estimates in a column with the given headername (below)
"""


import os
import numpy as np
from collections import defaultdict
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages

path='SVDA_opt5b' # folder with par file
parfile='columbia.bpa.2' # PEST parameter file
PP_designator='kpx' # string to identify pilot point parameters (e.g. "kp")
zones=['tc','ww','ec','ms'] # list of strings, one for each zone (to identify which zone pilot point belongs to)
zone_names=['Tunnel City','Wonewoc','Eau Claire','Mount Simon'] # list of names for zones/layers, for plot titles
units='ft/d'
plot_TGUESS=True # plots TGUESS distributions with pilot points
TGUESS_path='D:\\ATLData\\Columbia\\K\\pilot_points_setup\\byLayer' # path to folder with TGUESS files
TGUESS_files=['L3.txt','L4.txt','L5.txt','L6.txt'] # list of TGUESS files, one per zone, in same order as pilot point zones list above
TGUESS_values_col_name='Target' # Name of column in TGUESS file containing estimated K-values

'''
code to find parfile with highest iteration number
if SVDA:
    parfiles=[f for f in os.listdir(path) if '.bpa.' in f]
    inum=0
    for f in parfiles:
        inumf=int(f.split('.')[-1])
        if inumf>inum:
            inum=inumf
    parfile=[f for f in parfiles if str(inum) in f][0]
else:
    parfile=[f for f in os.listdir(path) if f.endswith('.par')][0]
'''

# read in parameter and TGUESS
pardata=np.genfromtxt(os.path.join(path,parfile),dtype=None,skiprows=1)

if plot_TGUESS:
    TG_vals_by_zone=defaultdict(list)
    for i in range(len(TGUESS_files)):
        indata=np.genfromtxt(os.path.join(TGUESS_path,TGUESS_files[i]),delimiter=',',names=True,dtype=None)
        TG_vals_by_zone[zones[i]]=indata[TGUESS_values_col_name]

# go through parameters and append pilot point values by zone to dictionary
pp_vals_by_zone=defaultdict(list)
for line in pardata:

    if PP_designator not in line[0]:
        continue
    else:
        for z in zones:
            #if z in line[0].split('_')[1]:
                #pp_vals_by_zone[z].append(line[1])
            if z in line[0]:
                pp_vals_by_zone[z].append(line[1])

# calculate summary stats and save to pdf

def plot_khist(values,title,outpdf):
    logvalues=np.log10(values)
    
    # make a histogram
    hist,bins=np.histogram(logvalues, bins=len(values)/5.0)
    #widths=1*(bins[1]-bins[0])
    center=(bins[:-1]+bins[1:])/2
    fig, (ax1) = plt.subplots()
    nbins=int(len(values)/5.0)
    ax1.hist(logvalues,nbins, normed=0, histtype='bar')
    # why does plotting a bar chart with np histogram results not work?
    # who knows.
    #ax1.bar(center,hist/len(logvalues),width=widths,align='center')
    ax1.set_xlim([-4,4])
    ax1.set_title(title)
    ax1.set_xlabel('Log K (%s)' %(units))
    ax1.set_ylabel('Number of points')


    # add in summary stats
    geomean=10**np.mean(logvalues)
    log_mean,log_std=np.mean(logvalues),np.std(logvalues)
    mx,mn=np.max(values),np.min(values)
    m2,m1,p1,p2=10**(log_mean+log_std*np.array([2,1,-1,-2]))
    summary='Summary Statistics:\ngeomean K:\t%.2f (ft/d)\nlog mean:\t\t%.2f\nlog stdev:\t\t%.2f\nMax:\t\t\t\t\t\t%.2f\n+2 stdev:\t\t%.2f\n+1 stdev:\t\t%.2f\n-1 stdev:\t\t\t%.2f\n-2 stdev:\t\t\t%.2f\nMin:\t\t\t\t\t\t\t%.2f' %(geomean,log_mean,log_std,mx,m2,m1,p1,p2,mn)
    ax1.text(0.95,.95,summary,verticalalignment='top',horizontalalignment='right',fontsize='10',multialignment='left',transform=ax1.transAxes,bbox={'facecolor':'white','pad':10})
    
    
    outpdf.savefig()
        
outpdf=PdfPages('%s_PPstats.pdf' %(path))
for i in range(len(zones)):
    
    values=pp_vals_by_zone[zones[i]]
    title='%s Pilot Points' %(zone_names[i])
    plot_khist(values,title,outpdf)

    if plot_TGUESS:
        values=TG_vals_by_zone[zones[i]]
        title='%s TGUESS' %(zone_names[i])
        plot_khist(values,title,outpdf)
outpdf.close() 