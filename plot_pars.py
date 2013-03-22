'''
parameter plotting for PEST

a m!ke@usgs joint
contact: mnfienen@usgs.gov

'''

import numpy as np
import os
import pylab as plt
from matplotlib.backends.backend_pdf import PdfPages

basecase = 'rc37u-pt'

allfiles = os.listdir(os.getcwd())
pars = dict()
for cf in allfiles:
    if ((basecase in cf) and ('par' in cf) and (cf[-4:] != '.par') and ('pdf' not in cf)):
        cind = int(cf.split('.')[-1])
        pars[cind] = cf
        
# open the initial par file to get parameter names
parnames = np.genfromtxt(pars[pars.keys()[0]],skip_header=1,usecols=[0],dtype=None)
# grab the first set of values from pars[0]
vals = np.genfromtxt(pars[pars.keys()[0]],skip_header=1,usecols=[1])
mults = np.genfromtxt(pars[pars.keys()[0]],skip_header=1,usecols=[2])
offs = np.genfromtxt(pars[pars.keys()[0]],skip_header=1,usecols=[3])
vals = (vals * mults) + offs
# now, if there are more than one 
if len(pars) > 1:
    for cf in pars:
        tmp = np.genfromtxt(pars[cf],skip_header=1,usecols=[1])
        mults = np.genfromtxt(pars[cf],skip_header=1,usecols=[2])
        offs = np.genfromtxt(pars[cf],skip_header=1,usecols=[3])
        tmp = (tmp * mults) + offs
        vals = np.vstack((vals,tmp))

# make a matrix that can be more easily manipulated
vals = vals.T
#normvals = vals/np.atleast_2d(vals[:,0]).T

# zip up and make a dictionary for the individual plots
allvals = dict(zip(parnames,vals))
        
# make a PDF with a page for each parameter, plotting all values
pp = PdfPages(basecase + '_parvalues.pdf')

for cp in sorted(allvals):
    currfig = plt.figure()
    pvs = allvals[cp]
    plt.plot(np.hstack((0,np.array(pars.keys()))),pvs,'o-')
    plt.xlabel('Iteration')
    plt.ylabel('Parameter Value')
    '''    
    try:
        plt.yscale('log')
    except:
        continue
    '''
    plt.title('Parameter Values for %s' %(cp))
    pp.savefig()
pp.close()
