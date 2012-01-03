
import numpy as np
import pickle

def jac_reader(jacinfile,obsnames):

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
    injac = open(jacinfile,'r').readlines()
    
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
        hajime=1
        crow = []
        while 1:
            try:
                tmp = injac.pop(0).strip().split()
            except:
                break
            if hajime == 1:
                cob = tmp.pop(0)
                print 'reading obs: ' + cob 
                crow.extend(tmp)
                hajime = hajime - 1   
            elif len(tmp) > 0:
                crow.extend(tmp)      
            else:
                break
        crow = np.array(crow,dtype=float)
        jac.append(crow)
    jac=np.array(jac,dtype=float)
    ofp = open('parnames.pkl','wb')
    pickle.dump(parnames,ofp)
    ofp.close()
    return jac,parnames

#####  read in observations
def obs_reader(obsinfile):
    '''
    reader for observations from the observations section of a PEST control file
    N.B.-> this file assumes that the observations, values, weights and groups are
    all present and have already been extracted from the control file.
    
    input:
        obsinfile, string, filename of the observations input file
    output:
        obsnames, list(strings), observation names
        obsval, numpy float array, observation values
        obswt, numpy float array, observation weights
        obsgp, list(strings), observation group names
    '''
    obsnames =[]
    obsval = []
    obswt = []
    obsgp = []
    indat = open(obsinfile,'r').readlines()
    for line in indat:
        tmp = line.strip().split()
        obsnames.append(tmp[0])
        obsval.append(tmp[1])
        obswt.append(tmp[2])
        obsgp.append(tmp[3])
    # convert the float values to numpy arrays
    obsnames = np.array(obsnames)
    obsval = np.array(obsval,dtype=float)
    obswt = np.array(obswt,dtype=float)
    obsgp = np.array(obsgp)
    return obsnames,obsval,obswt,obsgp

def lev_calc(jac,obswts):
    '''
    calculate leverage in the same way as PEST function INFSTAT
    
    input:
        jac, numpy float array (nobs x npar), Jacobian matrix
        wts, numpy float array (nobs x 1), vector of weights
    output:
        lev_vals, numpy float array (nobs x 1), vector of leverage values
    '''
    Z = np.dot(np.diag(obswts**(1./2)),jac)
    ZtZinv = np.linalg.inv(np.dot(Z.T,Z))
    Z_ZtZinv = np.dot(Z,ZtZinv)
    del ZtZinv
    H = np.dot(Z_ZtZinv,Z.T)
    lev_vals = np.diag(H) 
    return lev_vals