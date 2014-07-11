

import pandas as pd
from matplotlib.backends.backend_pdf import PdfPages
import matplotlib.pyplot as plt
import numpy as np
import matplotlib as mpl
import os

mpl.rcParams['font.sans-serif']          = 'Univers 57 Condensed'
mpl.rcParams['font.serif']               = 'Times'
mpl.rcParams['pdf.compression']          = 0
mpl.rcParams['pdf.fonttype']             = 42
#--figure text sizes
mpl.rcParams['legend.fontsize']  = 12
mpl.rcParams['axes.labelsize']   = 14
mpl.rcParams['xtick.labelsize']  = 12
mpl.rcParams['ytick.labelsize']  = 12


def SEN_reader(insenfile):
    # function to read in a SEN file (insenfile) and return a two-level dictionary
    # that includes first level keys as obsgroups and second level keys as parameters with composite sensitivities

    # read in the entire SEN file first
    parsfound = False
    parnames = list()
    obsgroupnames = list()
    obsinds = dict()
    insen = open(insenfile, 'r').readlines()
    infilelen = len(insen)
    allsen = dict()

    # find where the parameter names are
    for i, line in enumerate(insen):
        if 'parameter name' in line.lower():
            startpars = i + 1
            parsfound = True
        if parsfound:
            tmp = line.strip()
            if len(tmp) == 0:
                endpars = i
                break
    # read in the parameter names
    for i in np.arange(startpars, endpars):
        parnames.append(insen[i].strip().split()[0])
    NPAR = len(parnames)
    # now find the sensitivities at the end of optimization
    for i, line in enumerate(insen):
        if 'COMPLETION OF OPTIMISATION PROCESS' in line.upper():
            completion_line = i + 1
            break

    # now go through the file and read in the parameter
    for i in np.arange(completion_line, len(insen)):
        if 'composite sensitivities' in insen[i].lower() and 'prior' not in insen[i].lower():
            tmpobsgrpname = insen[i].strip().split()[-2].replace('"', '')
            if 'regul' not in tmpobsgrpname.lower():
                obsgroupnames.append(tmpobsgrpname)
                obsinds[obsgroupnames[-1]] = [i+3, i+3+NPAR]

    for cobgrp in obsgroupnames:
        strow = obsinds[cobgrp][0] + 1
        endrow = obsinds[cobgrp][1] + 1
        pars = []
        sens = []
        for i in np.arange(strow,endrow):
            tmp = insen[i].strip().split()
            pars.append(tmp[0])
            sens.append(tmp[-1])
        allsen[cobgrp] = dict(zip(pars,sens))

    return allsen


###################################
######## MAIN STARTS HERE #########
###################################

#workingpath = '/Users/mnfienen/Documents/MODELING_CENTER/NACP/NACP15_ss_SENSITIVITY/'
workingpath = os.getcwd()
insenfile = os.path.join(workingpath, 'nacp15_ss_reg.sen')

sendict = SEN_reader(insenfile)
numpars_plot = 15

allsenplot = PdfPages(os.path.join(workingpath,'nacp15_ss_SENSITIVITIY.pdf'))
groupkeyfile = os.path.join(workingpath, 'GroupKeyNACP.txt')

groupkeydata = np.genfromtxt(groupkeyfile,  dtype=None, names=True, delimiter=',')

groupkeys = dict(zip(groupkeydata['group'],groupkeydata['name']))
SENdf = pd.DataFrame(sendict)

for c in SENdf.columns:
    print 'plotting sensitivity for group --> {0}'.format(c)
    s = SENdf.ix[:,c].astype(float)
    s.sort(ascending = False)
    s_plot = s[0:numpars_plot]
    s_plot /= max(s_plot)
    fig = s_plot.plot(kind='bar', rot = 45)
    fig.set_title('{0}: {1}'.format(c, groupkeys[c]))
    plt.xlabel('Parameter')
    plt.ylabel('Normalized Composite Sensitivity')
    plt.tight_layout()
    allsenplot.savefig()
    plt.close()
allsenplot.close()