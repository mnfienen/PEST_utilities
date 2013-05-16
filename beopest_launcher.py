# modified original code by MNF by PFJ to include ability to start additional slaves
# after estimation has already commenced.
# For initial start (including master), set "workerstartN" to zero.
# For starting additional slaves after this launcher has already run once,
# set "workerstartN" equal to the first available "worker#" that is available.

import os
import shutil
import time
import xml.etree.ElementTree as ET
import sys

def tf2flag(intxt):
    # converts text written in XML file to True or Fale flag
    if intxt.lower()=='true':
        return True
    else:
        return False


# ##############################
# FIRST read in the parameter file from the XML
# ##############################
parfilename = sys.argv[1]
inpardat = ET.parse(parfilename)
inpars = inpardat.getroot()    

KILLOLD = tf2flag(inpardat.findall('.//KILLOLD')[0].text)
MAKENEW = tf2flag(inpardat.findall('.//MAKENEW')[0].text)
STARTMASTER = tf2flag(inpardat.findall('.//STARTMASTER')[0].text)
STARTWORKERS = tf2flag(inpardat.findall('.//STARTWORKERS')[0].text)
bp = inpardat.findall('.//bp')[0].text
casefile = inpardat.findall('.//casefile')[0].text
mod_dirs = []
tmp = inpardat.findall('.//mod_dir')
for el in tmp:
    mod_dirs.append(el.text)
stdir = inpardat.findall('.//stdir')[0].text
mflags = inpardat.findall('.//mflags')[0].text
masterip = inpardat.findall('.//masterip')[0].text
portnum = inpardat.findall('.//portnum')[0].text
wflags = inpardat.findall('.//wflags')[0].text
numworkers = int(inpardat.findall('.//numworkers')[0].text)
workerstartnum =  int(inpardat.findall('.//workerstartnum')[0].text)
# zero for first launch; first worker# available if previously launched workers
# ##############################
# END user supplied data
# ##############################

currdir = os.getcwd() #determine the current working directory for later moving about

# kill the old run directories
if KILLOLD:
    for i in range(numworkers):
        i = i + workerstartnum
        print 'Removing --> worker%s' %(i)
        if os.path.exists(os.path.join(currdir,'worker%s' %(i))):
            shutil.rmtree(os.path.join(currdir,'worker%s' %(i)))

# make the new directories
if MAKENEW:
    for i in range(numworkers):
        i = i + workerstartnum		
        print 'Making directory ---> worker%s' %(i)
        os.mkdir('worker%s' %(i))
        for cfold in mod_dirs:
            print '     copying %s' %(cfold)
            shutil.copytree(cfold,os.path.join(currdir,'worker%s' %(i),cfold))

# launch the master
if STARTMASTER:
    os.chdir(os.path.join(currdir,stdir))
    os.system('start %s %s %s :%d' %(bp,casefile,mflags,portnum))
    os.chdir(currdir)

if STARTWORKERS:
    print 'pausing 10 seconds to let the master get rolling'
    for csec in range(10): # wait 10 seconds to be sure the master started up correctly
        print '. '*(csec+1)
        time.sleep(1)
    for i in range(numworkers):
        i = i + workerstartnum		
        print 'Starting ---> worker%s' %(i)
        os.chdir(os.path.join('worker%s' %(i),stdir))
        os.system('start %s %s %s %s:%d' %(bp,casefile,wflags,masterip,portnum))
        os.chdir(currdir)