# modified original code by MNF by PFJ to include ability to start additional slaves
# after estimation has already commenced.
# For initial start (including master), set "workerstartN" to zero.
# For starting additional slaves after this launcher has already run once,
# set "workerstartN" equal to the first available "worker#" that is available.

import os
import shutil
import time
# ##############################
# START user supplied data
# ##############################
KILLOLD = True
MAKENEW = True
STARTMASTER = True
STARTWORKERS = True
bp = 'c:\\Downloaded_software\\PEST\\beopest64.exe'
casefile = 'menom7f.pst'
mod_dirs = ['latestrun']
stdir = 'latestrun'
mflags = ' /h /p1 '
masterip = 'localhost'
portnum = 623623
wflags = ' /h '
numworkers = 6
workerstartnum = 0 # zero for first launch; first worker# available if previously launched workers
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