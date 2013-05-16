import numpy as np
import re
import shapefile as sf
import shutil

# ####
# user-assigned variables
reiname = 'br_kc.rei.3'
tpname = 'Test_points.tp'

base_PRJ = 'base_NAD27_15N.prj'
head_scale = 10
stream_scale = 200000
csv_or_shp_flag = 'shp' # flag for output of files either 'csv' or 'shp'
#
# ####
#    
# ## ERROR CLASSES
#

# -- no comments allowed in table blocks
class MissingName(Exception):
    def __init__(self,cname):
        self.cname = cname
    def __str__(self):
        return('\n\nParameter named "' + self.cname + '" not in file: ' + tpname)
# -- bad choice for csv_shp_flag
class BadFlag(Exception):
    def __init__(self,csv_or_shp_flag):
        self.csv_or_shp_flag = csv_or_shp_flag
    def __str__(self):
        return('\n\nBad value "' + self.csv_or_shp_flag + '" for csv_or_shp_flag.\nMust be "csv" or "shp"')


# function to write out results to csv file
def writeout_csv(cofp,X,Y,cname,res,resplot):
    cofp.write('%f,%f,%s,%f,%f\n' %(X,Y,cname,res,resplot))

def rpd(a,b):
    # calcualte relative percent difference between a and b          
    a = float(a)
    b = float(b)
    if a==b:
        rpd = 0
    else:
        rpd = 2.0*(np.abs(a-b)/(a+b))


    return rpd

# function to write out results to csv file
def writeout_shp(cshp,X,Y,cname,res,resplot,meas,mod,c_rpd):
    cshp.point(X,Y)
    cshp.record(name=cname,residual=res,plot_res=resplot,meas=meas,modeled=mod,rpd=c_rpd)
    return cshp

# initialize the shapefile object with fields
def init_shp(cshp,fields):
    for cf in fields:
        # make the name field of character type
        if 'name' in cf.lower():
            cshp.field(cf)
        # the other fields should be numeric
        else:
            cshp.field(cf,fieldType='N',size='50',decimal=8)
        
    return cshp

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
npars = 0
for x in range(len(reidata['Group'])):
    if reidata['Group'][x][0:5]=='regul':
        npars = npars+1
    else: 
        npars = npars    
reidata = reidata[0:len(reidata['Group'])-npars] # remove any regularization parameters


# make a dictionary of output files - one per unique group name
grpnames = np.unique(reidata['Group'])

# replace '.' with '_' in reiname
reiname = re.sub('\.','_',reiname)
ofp_file_list = open('arcfiles_' + reiname + '.dat','w')
if csv_or_shp_flag == 'csv':
    ofps = dict()
    ofps_under = dict()
    ofps_over = dict()    
    for cname in grpnames:
        fname = cname + '_' + reiname + '.csv'
        ofps[cname] = open(fname,'w')
        ofp_file_list.write('%s\n' %(fname))
        fname = cname + '_under_' + reiname + '.csv'
        ofps_under[cname] = open(fname,'w')
        ofp_file_list.write('%s\n' %(fname))    
        fname = cname + '_over_' + reiname + '.csv'
        ofps_over[cname]  = open(fname,'w')
        ofp_file_list.write('%s\n' %(fname))    
        # write out the header while we're at it.
        ofps[cname].write('X,Y,Name,Residual,plot_res\n')
        ofps_under[cname].write('X,Y,Name,Residual,plot_res\n')
        ofps_over[cname].write('X,Y,Name,Residual,plot_res\n')
    ofp_file_list.close()
elif csv_or_shp_flag == 'shp':
    ofps_shp = dict()
    ofps_under_shp = dict()
    ofps_over_shp = dict()    
    shp_fields = ['name','residual','plot_res','meas','modeled','rpd']
    for cname in grpnames:
        fname = cname + '_' + reiname + '.shp'
        ofps_shp[cname] = [sf.Writer(sf.POINT),fname]
        ofps_shp[cname][0]=init_shp(ofps_shp[cname][0],shp_fields)
        shutil.copyfile(base_PRJ,fname[:-4] + '.prj')
        ofp_file_list.write('%s\n' %(fname))
        fname = cname + '_under_' + reiname + '.shp'
        shutil.copyfile(base_PRJ,fname[:-4] + '.prj')
        ofps_under_shp[cname] = [sf.Writer(sf.POINT),fname]
        ofps_under_shp[cname][0]=init_shp(ofps_under_shp[cname][0],shp_fields)
        ofp_file_list.write('%s\n' %(fname))    
        fname = cname + '_over_' + reiname + '.shp'
        shutil.copyfile(base_PRJ,fname[:-4] + '.prj')
        ofps_over_shp[cname]  = [sf.Writer(sf.POINT),fname]
        ofps_over_shp[cname][0]=init_shp(ofps_over_shp[cname][0],shp_fields)

        ofp_file_list.write('%s\n' %(fname))    
    ofp_file_list.close()
    
else:
    raise(BadFlag(csv_or_shp_flag))

# now loop over the data and get X, Y, and make plotting  symbol size correction
for crow in reidata:
    cname = crow['Name'].lower()
    tpInds = np.where(tpNames==cname)
    if len(tpInds[0]) == 0:
        raise(MissingName(cname))  
    else:
        tpInds = tpInds[0][0]
    if tpTarget_type[tpInds] == 'gage':
        res_plot_factor = stream_scale
    elif tpTarget_type[tpInds] == 'piezometer':
        res_plot_factor = head_scale
    # write the all residuals file 
    if csv_or_shp_flag == 'shp':
        writeout_shp(ofps_shp[crow['Group']][0],tpX[tpInds],tpY[tpInds],cname, 
             np.abs(crow['Residual']),np.abs(crow['Residual'])/res_plot_factor,
             crow['Measured'],crow['Modelled'],rpd(crow['Measured'],crow['Modelled']))    
    elif csv_or_shp_flag == 'csv':    
        writeout_csv(ofps[crow['Group']],tpX[tpInds],tpY[tpInds],cname, 
             np.abs(crow['Residual']),np.abs(crow['Residual'])/res_plot_factor,
             crow['Measured'],crow['Modelled'],rpd(crow['Measured'],crow['Modelled']))   
    else:
        raise(BadFlag(csv_or_shp_flag))    
    # write the over and under files
    if crow['Residual'] >=0:
        if csv_or_shp_flag == 'csv':
            cofps = ofps_under[crow['Group']]
        else:
            cshp = ofps_under_shp[crow['Group']][0]
        cres = crow['Residual']
        cresplot=crow['Residual']/res_plot_factor
    elif crow['Residual'] < 0:
        if csv_or_shp_flag == 'csv':
            cofps = ofps_over[crow['Group']]
        else:
            cshp = ofps_over_shp[crow['Group']][0]
        cres = np.abs(crow['Residual'])
        cresplot=np.abs(crow['Residual']/res_plot_factor)

    if csv_or_shp_flag == 'csv':
        writeout_csv(cofps,tpX[tpInds],tpY[tpInds],cname, 
                 cres,cresplot,
             crow['Measured'],crow['Modelled'],rpd(crow['Measured'],crow['Modelled']))       
    else:
        writeout_shp(cshp,tpX[tpInds],tpY[tpInds],cname, 
                 cres,cresplot,
             crow['Measured'],crow['Modelled'],rpd(crow['Measured'],crow['Modelled']))                              
    
    
if csv_or_shp_flag == 'csv':
    # close all the output csv files to clean up
    for cf in ofps:
        ofps[cf].close()
    for cf in ofps_under:
        ofps_under[cf].close()            
    for cf in ofps_over:
        ofps_over[cf].close()
elif csv_or_shp_flag == 'shp':
    # close all the output csv files to clean up
    for cf in ofps_shp:
        if cf != 'bad_odanah': #mike's kludge to fix script by removing the bad odanah group
            ofps_shp[cf][0].save(ofps_shp[cf][1])
    for cf in ofps_over_shp:
        if cf != 'bad_odanah':
            ofps_over_shp[cf][0].save(ofps_over_shp[cf][1])
    for cf in ofps_under_shp:
        if cf != 'bad_odanah':
            ofps_under_shp[cf][0].save(ofps_under_shp[cf][1])
