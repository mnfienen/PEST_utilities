import numpy as np
import re

# ####
# user-assigned variables
reiname = 'br_kc.rei.3'
tpname = 'Test_points.tp'
head_scale = 10
stream_scale = 20000
#
# ####


# function to write out results

def writeout(cofp,X,Y,cname,res,resplot):
    cofp.write('%f,%f,%s,%f,%f\n' %(X,Y,cname,res,resplot))

# First read in the TP information
tpdata = np.genfromtxt(tpname,delimiter=',',dtype=None)

tpNames =tpdata['f5']
tpX=tpdata['f0']
tpY=tpdata['f1']
tpTarget_type = tpdata['f4']
del tpdata

# force the names to lower case for later comparisons with PEST output
for i in np.arange(len(tpNames)):
    tpNames[i] = tpNames[i].lower()
    tpTarget_type[i] = tpTarget_type[i].lower()
    # remove spaces too!
    tpNames[i] = re.sub('\s+','',tpNames[i])
    tpTarget_type[i] = re.sub('\s+','',tpTarget_type[i])
# now read in the REI file
reidata = np.genfromtxt(reiname,skiprows=4,names=True,dtype=None)

# make a dictionary of output files - one per unique group name
grpnames = np.unique(reidata['Group'])
ofps = dict()
ofps_under = dict()
ofps_over = dict()

for cname in grpnames:
    reiname = re.sub('\.','_',reiname)
    ofps[cname] = open(cname + '_' + reiname + '.csv','w')
    ofps_under[cname] = open(cname + '_under_' + reiname + '.csv','w')
    ofps_over[cname]  = open(cname + '_over_' + reiname + '.csv','w')
    # write out the header while we're at it.
    ofps[cname].write('X,Y,Name,Residual,Res_to_plot\n')
    ofps_under[cname].write('X,Y,Name,Residual,Res_to_plot\n')
    ofps_over[cname].write('X,Y,Name,Residual,Res_to_plot\n')

# now loop over the data and get X, Y, and make plotting  symbol size correction
for crow in reidata:
    cname = crow['Name'].lower()
    tpInds = np.where(tpNames==cname)
    if len(tpInds) == 0:
        raise(MissingName(cname))  
    else:
        tpInds = tpInds[0][0]
    if tpTarget_type[tpInds] == 'gage':
        res_plot_factor = stream_scale
    elif tpTarget_type[tpInds] == 'piezometer':
        res_plot_factor = head_scale
    # write the all residuals file 
    writeout(ofps[crow['Group']],tpX[tpInds],tpY[tpInds],cname, 
             np.abs(crow['Residual']),np.abs(crow['Residual'])/res_plot_factor)
    # write the over and under files
    if crow['Residual'] >=0:
        cofps = ofps_under[crow['Group']]
        cres = np.abs(crow['Residual'])
        cresplot=np.abs(crow['Residual']/res_plot_factor)
    elif crow['Residual'] < 0:
        cofps = ofps_over[crow['Group']]
        cres = crow['Residual']
        cresplot=crow['Residual']/res_plot_factor
    writeout(cofps,tpX[tpInds],tpY[tpInds],cname, 
                 cres,cresplot)        

                                    
    
    
    
# close all the output files to clean up
for cf in ofps:
    ofps[cf].close()
    
#    
# ## ERROR CLASSES
#

# -- no comments allowed in table blocks
class MissingName(Exception):
    def __init__(self,cname):
        self.cname = cname
    def __str__(self):
        return('\n\nParameter named "' + self.cname + '" not in file: ' + tpname)
    