import os
import shutil
import time
# ##############################
# START user supplied data
# ##############################
KILLOLD = False
MAKENEW = False
STARTMASTER = False
STARTWORKERS = True
bp = 'beopest64.exe'
casefile = 'run18svda.pst'
mod_dirs = ['Python27','Master']
stdir = 'Master'
mflags = ' /h /p1 '
masterip = '130.11.161.154'
portnum = 665566
wflags = ' /h '
numworkers = 8
# ##############################
# END user supplied data
# ##############################

currdir = os.getcwd() #determine the current working directory for later moving about

# kill the old run directories
if KILLOLD:
    for i in range(numworkers):
    	print 'Removing --> worker%s' %(i)
        if os.path.exists(os.path.join(currdir,'worker%s' %(i))):
            shutil.rmtree(os.path.join(currdir,'worker%s' %(i)))

# make the new directories
if MAKENEW:
    for i in range(numworkers):
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
        print 'Starting ---> worker%s' %(i)
        os.chdir(os.path.join('worker%s' %(i),stdir))
        os.system('start %s %s %s %s:%d' %(bp,casefile,wflags,masterip,portnum))
        os.chdir(currdir)