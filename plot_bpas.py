'''
parameter plotting for PEST

a m!ke@usgs joint
contact: mnfienen@usgs.gov

'''

import numpy as np
import os
import pylab as plt
from matplotlib.backends.backend_pdf import PdfPages

basecase = 'assp3tr'

allfiles = os.listdir(os.getcwd())
bpas = dict()
for cf in allfiles:
    if ((basecase in cf) and ('bpa' in cf) and (cf[-4:] != '.bpa')):
        cind = int(cf.split('.')[-1])
        bpas[cind] = cf
        
# open the initial bpa file to get parameter names
parnames = np.genfromtxt(bpas[0],skip_header=1,usecols=[0],dtype=None)
# grab the first set of values from bpas[0]
vals = np.genfromtxt(bpas[0],skip_header=1,usecols=[1])

# now, if there are more than one 
if len(bpas) > 1:
    for cf in np.arange(1,len(bpas)):
        tmp = np.genfromtxt(bpas[cf],skip_header=1,usecols=[1])
        vals = np.vstack((vals,tmp))
# make a matrix that can be more easily manipulated
vals = vals.T
normvals = vals/np.atleast_2d(vals[:,0]).T

# zip up and make a dictionary for the individual plots
allvals = dict(zip(parnames,vals))
        
# make a PDF with a page for each parameter, plotting all values
pp = PdfPages(basecase + '_parvalues.pdf')

for cp in sorted(allvals):
    currfig = plt.figure()
    pvs = allvals[cp]
    plt.plot(np.arange(len(pvs))+1,pvs,'o-')
    plt.xlabel('Iteration')
    plt.ylabel('Parameter Value')
    plt.title('Parameter Values for %s' %(cp))
    pp.savefig()
pp.close()