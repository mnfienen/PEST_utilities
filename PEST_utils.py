
import numpy as np
import pickle
from collections import OrderedDict

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
    allsen = OrderedDict()

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


def jac_reader(jacinfile, obsnames):

    '''
    reads a jacobian file from PEST written out from JCO format to text
    format using JACWRIT utility of PEST.
    input variables:
        jacinfile, string, input file name 
        obsname, list(strings), list of all observation names
    output:
        parnames, list(strings), a list of the parameter names
        jac, a nobs by npar numpy float array, the jacobian matrix
    '''
    ######   read in the Jacobian file
    injac = open(jacinfile, 'r').readlines()
    
    # get the parameter names
    parnames = []
    while 1: 
        tmp = injac.pop(0).strip().split()
        if len(tmp) > 0:
            parnames.extend(tmp)
        else:
            break
    npar = len(parnames)
    nobs = len(obsnames)
    # now read through the rest of the file
    jac = []
    for i in range(nobs):
        hajime = 1
        crow = []
        while 1:
            try:
                tmp = injac.pop(0).strip().split()
            except:
                break
            if hajime == 1:
                cob = tmp.pop(0)
                print '\rreading obs: {0}'.format(cob),
                crow.extend(tmp)
                hajime = hajime - 1   
            elif len(tmp) > 0:
                crow.extend(tmp)      
            else:
                break
        crow = np.array(crow, dtype=float)
        jac.append(crow)
    jac = np.array(jac, dtype=float)
    ofp = open('parnames.pkl', 'wb')
    pickle.dump(parnames, ofp)
    ofp.close()
    return jac, parnames

#####  read in observations
def obs_reader(pstfile, **kwargs):
    '''
    reader for observations from the observations section of a PEST control file
    
    input:
        obsinfile, string, filename of the observations input file
    output:
        obsnames, list(strings), observation names
        obsval, numpy float array, observation values
        obswt, numpy float array, observation weights
        obsgp, list(strings), observation group names
    '''

    try:
        regul = kwargs['regularisation']
    except KeyError:
        regul = False

    obsnames =[]
    obsval = []
    obswt = []
    obsgp = []
    indat = open(pstfile, 'r').readlines()
    NOBS = int(indat[3].strip().split()[1])

    for i, line in enumerate(indat):
        if '* observation data' in line:
            obsstart = i + 1
            break

    for i in np.arange(obsstart, obsstart + NOBS):
        tmp = indat[i].strip().split()
        if not regul and 'regul' in tmp[3]:
            continue
        else:
            obsnames.append(tmp[0])
            obsval.append(tmp[1])
            obswt.append(tmp[2])
            obsgp.append(tmp[3])

    # convert the float values to numpy arrays
    obsnames = np.array(obsnames)
    obsval = np.array(obsval, dtype=float)
    obswt = np.array(obswt, dtype=float)
    obsgp = np.array(obsgp)
    return obsnames, obsval, obswt, obsgp

def lev_calc(jac, obswts):
    '''
    calculate leverage in the same way as PEST function INFSTAT
    
    input:
        jac, numpy float array (nobs x npar), Jacobian matrix
        wts, numpy float array (nobs x 1), vector of weights
    output:
        lev_vals, numpy float array (nobs x 1), vector of leverage values
    '''
    Z = np.dot(np.diag(obswts**(1./2)), jac)
    ZtZinv = np.linalg.inv(np.dot(Z.T, Z))
    Z_ZtZinv = np.dot(Z, ZtZinv)
    del ZtZinv
    H = np.dot(Z_ZtZinv, Z.T)
    lev_vals = np.diag(H) 
    return lev_vals


