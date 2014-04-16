'''
Program to match residuals from REI file (from PEST) with a testpoint (TP) file from GFLOW for plotting purposes.
Also computes percent difference and percent error for plotting.
Note: may need to export a composite TP file from GFLOW if imported TPs via multi files, and may also need to 
edit the composite TP file to ensure names match (GFLOW clips long names).
'''
import sys
import xml.etree.ElementTree as ET
import numpy as np
import re
import shapefile as sf
import shutil
import os
# use pandas package to organize additional data (screen top/bot, etc.) about the targets
try:
    import pandas as pd
except:
    pd = False


try:
    infile = sys.argv[1]
except:
    infile = 'Postproc_input.XML'

# observation locations file settings
x_column = 'X' # column with x coordinates (0=column 1)
y_column = 'Y' # column with y coordinates
names_column = 'Name' # column with observation names
type_column = 'Type' # column containing target types; currently "gage" or "piezometer"
sctop_column = 'Screen_top' # column with screen top elevation
scbot_column = 'Screen_bot' # column with screen bot elevation
row_column = 'row' # column with row location
col_column = 'column' # column with column location
toplay_column = 'toplayer' # column with observation top layer
botlay_column = 'botlayer' # column with observation bottom layer


# settings
IgnoreObs = ['regul','error']
head_scale = 10
stream_scale = 200000
csv_or_shp_flag = 'shp' # flag for output of files either 'csv' or 'shp'
overunder = False # True = write 3 files: abs(all), abs(over), abs(under)
#                   False = write 1 file: all raw residuals (plus scaled and RPD & RPE)

try:
    inpardat = ET.parse(infile)
except:
    raise IOError("Cannot open {0}!".format(infile))

inpars = inpardat.getroot()

# input
pest_path = inpars.findall('.//path')[0].text
reiname = inpars.findall('.//rei_name')[0].text
gis_folder = inpars.findall('.//GIS_folder')[0].text
obs_locations_file = inpars.findall('.//observation_locations')[0].text
base_PRJ = inpars.findall('.//PRJfile')[0].text
pareto = inpars.findall('.//pareto')[0].text
groups_rei = inpars.findall('.//rei_w_groups')[0].text

if pareto.lower() == 'true':
    pareto = True
    groups_rei = inpars.findall('.//rei_w_groups')[0].text
else:
    pareto = False
    
#junk = 1
#
# ##################
# ## ERROR CLASSES #
# ##################

# -- no comments allowed in table blocks
class MissingName(Exception):
    def __init__(self,cname):
        self.cname = cname
    def __str__(self):
        return('\n\nParameter named "' + self.cname + '" not in file: ' + obs_locations_file)
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
        rpd = 2*np.abs(a-b)/(a+b)
    return rpd

def rpe(a,b):
    # calcualte relative percent error for a and b. Measured = a.
    a = float(a)
    b = float(b)
    if a==b:
        rpe = 0
    # kludge to handle observations of 0 value
    elif a==0:
        rpe=0
    else:
        rpe = 100*((a-b)/a)
    return rpe

def sqwr(a,b):
    # calcualte weighted residual for a and b.
    a = float(a)
    b = float(b)
    sqwr = (a*b)*(a*b)
    return sqwr

# function to write out results to csv file
def writeout_shp(cshp,X,Y,cname,res,absres,resplot,meas,mod,c_rpe,weight,
                 sctop=None,scbot=None,row=None,column=None,top_layer=None,bot_layer=None): # use **kwargs to incorporate optional fields
    cshp.point(X,Y)
    cshp.record(cname,res,absres,resplot,meas,mod,c_rpe,weight,sctop,scbot,row,column,top_layer,bot_layer)
    return cshp
'''
def writeout_shp(cshp,X,Y,cname,res,resplot,meas,mod,c_rpd):
    cshp.point(X,Y)
    cshp.record(name=cname,residual=res,plot_res=resplot,meas=meas,modeled=mod,rpd=c_rpd)
    return cshp
'''
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

# ###############
# Start of Main #
# ###############


# First read in the TP information
tpdata = np.genfromtxt(obs_locations_file,delimiter=',',dtype=None, names=True)

tpNames =tpdata[names_column]
tpX = tpdata[x_column]
tpY = tpdata[y_column]
tpTarget_type = tpdata[type_column]
del tpdata

# read in other target information from observations file
if pd:
    obsdata = pd.read_csv(obs_locations_file)
    obsdata.index = obsdata[names_column].str.lower()

# force the names to lower case for later comparisons with PEST output
for i in np.arange(len(tpNames)):
    tpNames[i] = tpNames[i].lower()
    tpTarget_type[i] = tpTarget_type[i].lower()
    # remove spaces too!
    tpNames[i] = re.sub('\s+','',tpNames[i])
    tpTarget_type[i] = re.sub('\s+','',tpTarget_type[i])
    
# now read in the REI file
reidata = np.genfromtxt(os.path.join(pest_path,reiname),skiprows=4,names=True,dtype=None)

# if run was done in pareto mode, reassign obs group names from another rei provided in the XML input
if pareto:
    try:
        rei_groups_df = pd.read_csv(groups_rei, delim_whitespace=True, skiprows=6, index_col='Name')
        #if np.isnan(np.max(rei_groups_df.ix[:,0])):
            #rei_groups_df = rei_groups_df[rei_groups_df.columns[1:]]
            # for observations that were read in, reassign the entry in 'Group' column to group from other REI
        reidata = reidata.astype([('Name', 'S20'), 
        ('Group', 'S20'), 
        ('Measured', '<f8'), 
        ('Modelled', '<f8'), 
        ('Residual', '<f8'), 
        ('Weight', '<f8')])
        for observation in reidata:
            observation['Group'] = rei_groups_df.ix[observation['Name'], 'Group']

    except IOError:
        print "Cannot open {0}. Please provide a non-pareto REI file so that observations can be analyzed by group."
        quit()

# Remove obs from unwanted groups (regularization parameters, MB reporting)
# Assumes that these groups are at the end of the REI (& PST) file.
npars = 0
for cgroup in IgnoreObs:
    for x in range(len(reidata['Group'])):
        if reidata['Group'][x][0:5]==cgroup:
            npars = npars+1
        else: 
            npars = npars    
reidata = reidata[0:len(reidata['Group'])-npars]

# make a dictionary of output files - one per unique group name
grpnames = np.unique(reidata['Group'])

# replace '.' with '_' in reiname
reiname = re.sub('\.','_',reiname)

# if an output folder for GIS files doesn't exist, make one
if not os.path.exists(os.path.join(pest_path,gis_folder)):
    os.makedirs(os.path.join(pest_path,gis_folder))
ofp_file_list = open(os.path.join(pest_path,gis_folder,'arcfiles_' + reiname + '.dat'),'w')

# write out the summary file that lists all the files that were generated (used by arc2mxd.py)
# and initiate the output files (csv or shp).  We'll populate them below.
if csv_or_shp_flag == 'csv':
    ofps = dict()
    ofps_under = dict()
    ofps_over = dict()    
    for cname in grpnames:
        fname = cname + '_' + reiname + '.csv'
        ofps[cname] = open(os.path.join(pest_path,gis_folder,fname),'w')
        ofp_file_list.write('%s\n' %(fname))
        # write out the header while we're at it.
        if overunder:
            ofps[cname].write('X,Y,Name,Residual,plot_res\n')
        else:
            ofps[cname].write('X,Y,Name,Residual,percent_error\n')            
        # generate the over/under files
        if overunder:
            fname = cname + '_under_' + reiname + '.csv'
            ofps_under[cname] = open(os.path.join(pest_path,gis_folder,fname),'w')
            ofp_file_list.write('%s\n' %(fname))    
            fname = cname + '_over_' + reiname + '.csv'
            ofps_over[cname]  = open(os.path.join(pest_path,gis_folder,fname),'w')
            ofp_file_list.write('%s\n' %(fname))    
            # write out the header while we're at it.
            ofps_under[cname].write('X,Y,Name,Residual,plot_res\n')
            ofps_over[cname].write('X,Y,Name,Residual,plot_res\n')
    ofp_file_list.close()
elif csv_or_shp_flag == 'shp':
    ofps_shp = dict()
    ofps_under_shp = dict()
    ofps_over_shp = dict()    
    if overunder:
        shp_fields = ['name', 'residual', 'plot_res', 'meas', 'modeled', 'rpd', 'junk']
    else:
        shp_fields = ['name', 'residual', 'abs_resid', 'SQ_wt_res', 'meas', 'modeled', 'pct_error', 'weight',
                      'sctop', 'scbot', 'row', 'column', 'top_layer', 'bot_layer']
    for cname in grpnames:
        fname = cname + '_' + reiname + '.shp'
        ofps_shp[cname] = [sf.Writer(sf.POINT), os.path.join(pest_path, gis_folder, fname)] # generates a shapefile
        ofps_shp[cname][0] = init_shp(ofps_shp[cname][0], shp_fields) # Initializes fields for the shapefile
        shutil.copyfile(base_PRJ, os.path.join(pest_path, gis_folder,fname[:-4] + '.prj')) # assigns a projection to the shapefile
        ofp_file_list.write('%s\n' %(fname)) # adds the name of the shape file to the summary file
        if overunder:
            fname = cname + '_under_' + reiname + '.shp'
            shutil.copyfile(base_PRJ,os.path.join(pest_path,gis_folder,fname[:-4] + '.prj'))
            ofps_under_shp[cname] = [sf.Writer(sf.POINT),os.path.join(pest_path,gis_folder,fname)]
            ofps_under_shp[cname][0]=init_shp(ofps_under_shp[cname][0],shp_fields)
            ofp_file_list.write('%s\n' %(fname))    
            fname = cname + '_over_' + reiname + '.shp'
            shutil.copyfile(base_PRJ,os.path.join(pest_path,gis_folder,fname[:-4] + '.prj'))
            ofps_over_shp[cname]  = [sf.Writer(sf.POINT),os.path.join(pest_path,gis_folder,fname)]
            ofps_over_shp[cname][0]=init_shp(ofps_over_shp[cname][0],shp_fields)
            ofp_file_list.write('%s\n' %(fname))    
    ofp_file_list.close()
else:
    raise(BadFlag(csv_or_shp_flag))

# now loop over the data and get X, Y, and make plotting symbol size correction
for crow in reidata:
    cname = crow['Name'].lower()
    tpInds = np.where(tpNames==cname) #matches the TP names for the REI file with those in the TP file
    if len(tpInds[0]) == 0:
        raise(MissingName(cname))  
    else:
        tpInds = tpInds[0][0]
    if tpTarget_type[tpInds] == 'gage':
        res_plot_factor = stream_scale
    elif tpTarget_type[tpInds] == 'piezometer':
        res_plot_factor = head_scale
    # write the all residuals file 
    if overunder:
        if csv_or_shp_flag == 'shp':
            writeout_shp(ofps_shp[crow['Group']][0],tpX[tpInds],tpY[tpInds],cname, 
                 np.abs(crow['Residual']), np.abs(crow['Residual'])/res_plot_factor,
                 crow['Measured'],crow['Modelled'], rpd(crow['Measured'], crow['Modelled']), junk)
        elif csv_or_shp_flag == 'csv':    
            writeout_csv(ofps[crow['Group']],tpX[tpInds],tpY[tpInds],cname, 
                 np.abs(crow['Residual']),np.abs(crow['Residual'])/res_plot_factor)   
        else:
            raise(BadFlag(csv_or_shp_flag))
    else:
        if csv_or_shp_flag == 'shp':
            sqrwghtres = sqwr(crow['Residual'], crow['Weight'])
            if not pd or not obs_locations_file:
                writeout_shp(ofps_shp[crow['Group']][0], tpX[tpInds], tpY[tpInds], cname,
                     crow['Residual'], np.abs(crow['Residual']), sqrwghtres,
                     crow['Measured'], crow['Modelled'], rpe(crow['Measured'], crow['Modelled']), crow['Weight'])
            else:
                writeout_shp(ofps_shp[crow['Group']][0],
                             tpX[tpInds], tpY[tpInds], cname,
                             crow['Residual'], np.abs(crow['Residual']), sqrwghtres,
                             crow['Measured'], crow['Modelled'],
                             rpe(crow['Measured'], crow['Modelled']),
                             crow['Weight'],
                             obsdata.ix[cname][sctop_column],
                             obsdata.ix[cname][scbot_column],
                             obsdata.ix[cname][row_column],
                             obsdata.ix[cname][col_column],
                             obsdata.ix[cname][toplay_column],
                             obsdata.ix[cname][botlay_column])

        elif csv_or_shp_flag == 'csv':    
            writeout_csv(ofps[crow['Group']],tpX[tpInds],tpY[tpInds], cname,
                 crow['Residual'],rpe(crow['Measured'],crow['Modelled']))   
        else:
            raise(BadFlag(csv_or_shp_flag))    
        
    # write the over and under files
    if overunder:
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
                     cres,cresplot)       
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
    # close all the output shp files to clean up
    
    for cf in ofps_shp:
        #if cf != 'bad_odanah': #mike's kludge to fix script by removing the bad odanah group
        ofps_shp[cf][0].save(ofps_shp[cf][1])

    for cf in ofps_over_shp:
        if cf != 'bad_odanah':
            ofps_over_shp[cf][0].save(ofps_over_shp[cf][1])
    for cf in ofps_under_shp:
        if cf != 'bad_odanah':
            ofps_under_shp[cf][0].save(ofps_under_shp[cf][1])


