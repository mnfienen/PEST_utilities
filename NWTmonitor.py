__author__ = 'aleaf'

import numpy as np
import sys
import os
from collections import defaultdict

# set mode (master or slave)
try:
    if sys.argv[1].lower() == 'master':
        Master = True
except:
    Master = False

def runtime_min(line):
    time = line.strip().split(':')[1]
    if 'Hour' in line:
        hrs = float(time.split(',')[0].split()[0])
        min = float(time.split(',')[1].split()[0])
        sec = float(time.split(',')[2].split()[0])
    elif 'Minute' in line:
        hrs = 0
        min = float(time.split(',')[0].split()[0])
        sec = float(time.split(',')[1].split()[0])
    else:
        hrs = 0
        min = 0
        sec = float(time.split()[0])
    time = hrs*60.0 + min + sec/60.0
    return time

def return_NWT_summary(line):
    try:
        item = line.strip().split(':')[1].split()[0]
        float(item)
    except:
        item = 999999
    return item


if Master:
    start_dir = os.getcwd()
    path = 'Z:\\aleaf\\BR\\log' #os.path.join('..','log')
    logfiles = [f for f in os.listdir(path) if f.endswith('.out')]
    os.chdir(path)

    Times = []
    Runtimes = defaultdict(lambda: defaultdict(list))
    MaxHeadChanges = defaultdict(lambda: defaultdict(list))
    MaxFluxResids = defaultdict(lambda: defaultdict(list))
    L2New = defaultdict(lambda: defaultdict(list))
    TotalOuters = defaultdict(lambda: defaultdict(list))
    PercentDis = defaultdict(lambda: defaultdict(list))
    MaxHeadObsRes = defaultdict(lambda: defaultdict(list))
    print "scraping *.out files in {0}...\n".format(path)
    knt = 0

    ofp = open(os.path.join(start_dir,'Condor_NWT_summary.csv'),'w')
    ofp.write('logfile,datetime,IP,scratchdir,run_number,elapsed_time_min,max_dh,maxFluxResid,L2new,OuterItrs,MassBalDiscrep,MaxHeadObsResid\n')
    for f in logfiles:
        knt += 1
        print "\r{0} ({1} of {2})".format(f, knt, len(logfiles)),
        indata = open(f).readlines()

        times =[]
        runtimes = []
        maxheadchanges = []
        maxfluxresiduals = []
        l2new =[]
        totalouters = []
        percentdis = []
        maxhobsresids = []
        maxheadchange = np.NaN
        maxfluxresidual = np.NaN
        l2nw = np.NaN
        pctd = np.NaN
        mhobs = np.NaN
        totalouter = np.NaN
        run_number = 0

        for i in range(len(indata)):
            if "IPv4 Address" in indata[i]:
                IP = indata[i].strip().split(':')[-1]
            if "BeoPEST Version 13.0." in indata[i]:
                scratchdir = indata[i-2].strip().split('\\')[-1]
            if "Running model ...." in indata[i]:
                run_number += 1
                elapsedtime = np.NaN
            if "Run start date and time" in indata[i]:
                datetime = indata[i].strip().split('):')[-1]
            if "Elapsed run time" in indata[i]:
                elapsedtime = float(runtime_min(indata[i]))
                runtimes.append(elapsedtime)
            if "Run end date and time" in indata[i]:
                datetime = indata[i].strip().split('):')[-1]
            if "NWT Summary" in indata[i]:
                if len(indata[i+1])>1:
                    maxheadchange = float(return_NWT_summary(indata[i+1]))
                    maxfluxresidual = float(return_NWT_summary(indata[i+2]))
                    l2nw = float(return_NWT_summary(indata[i+3]))
                    totalouter = int(return_NWT_summary(indata[i+5]))
                    pctd = float(return_NWT_summary(indata[i+7]))
                    mhobs = float(return_NWT_summary(indata[i+8]))
                else:
                    maxheadchange, maxfluxresidual, l2nw, totalouter, pctd, mhobs = np.NaN, np.NaN, np.NaN, np.NaN, \
                                                                                    np.NaN, np.NaN
                maxheadchanges.append(maxheadchange)
                maxfluxresiduals.append(maxfluxresidual)
                l2new.append(l2nw)
                totalouters.append(totalouter)
                percentdis.append(pctd)
                maxhobsresids.append(mhobs)
                '''
                try:
                    pctd = float(return_NWT_summary(indata[i+7]))
                except:
                    pctd = np.NaN
                percentdis.append(pctd)
                try:
                    mhobs = float(return_NWT_summary(indata[i+8]))

                except:
                    mhobs = np.NaN
                maxhobsresids.append(mhobs)
                '''
                try:
                    IP
                except:
                    IP = 'Not_specified'
                #if "Model run complete." in indata[i]:
                ofp.write('{0},{1},{2},{3},{4},{5:.2f},{6:.10e},{7:.10e},{8:.10e},{9},{10:.2f},{11:.2f}\n'.format(f,datetime,IP,
                          scratchdir,run_number,elapsedtime,maxheadchange,maxfluxresidual,l2nw,totalouter,pctd,mhobs))

        Runtimes[IP][scratchdir].append(runtimes)
        MaxHeadChanges[IP][scratchdir].append(maxheadchanges)
        MaxFluxResids[IP][scratchdir].append(maxfluxresiduals)
        L2New[IP][scratchdir].append(l2new)
        TotalOuters[IP][scratchdir].append(totalouters)
        PercentDis[IP][scratchdir].append(percentdis)
        MaxHeadObsRes[IP][scratchdir].append(maxhobsresids)
    ofp.close()
    print '\nsee summary in Condor_NWT_summary.csv.'


if not Master:
    basename = [f[:-4] for f in os.listdir(os.getcwd()) if f.endswith('.nam')]
    if len(basename) > 1:
        "print warning! multiple NAM files found, clean up run folder."
    basename = basename[0]
    try:
        LST = open(basename+'.lst').readlines()
    except:
        raise IOError("No MODFLOW LST file found!")
        quit()

    Residuals = False
    discrep = False
    heads = False
    maxheadres = 0
    print "\nNWT Summary:"
    for i in range(len(LST)):
        if not Residuals and "NWT REQUIRED" in LST[i]:
            Residuals = True
            dhMax = LST[i-3].strip().split()[6]
            dhInd = ' '.join(LST[i-3].strip().split()[3:6])
            dQMax = LST[i-3].strip().split()[10]
            dQInd = ' '.join(LST[i-3].strip().split()[7:10])
            L2new = LST[i-3].strip().split()[11]
            Solver_dhMax = LST[i-3].strip().split()[-1]
            print "Max.-Head-Change: {0}  ({1})".format(dhMax,dhInd)
            print "Max.-Flux-Residual: {0}  ({1})".format(dQMax,dQInd)
            print "L2-New: {0}".format(L2new)
            print "Solver-Max-Delh: {0}".format(Solver_dhMax)

            outer = int(''.join([s for s in LST[i] if s.isdigit()]))
            inner = int(''.join([s for s in LST[i+1] if s.isdigit()]))
            print "Total outer: {0}\nTotal inner: {1}".format(outer, inner)
        if not discrep and "PERCENT DISCREPANCY" in LST[i]:
            discrep = True
            MassBal_Error = LST[i].strip().split()[3]
            print "Percent discrepancy: {0}".format(MassBal_Error)
        if not heads and "HEAD AND DRAWDOWN OBSERVATIONS" in LST[i-4]:
            heads = True
        if heads:
            try:
                headres = float(LST[i].strip().split()[-1])
                if np.abs(headres) > np.abs(maxheadres):
                    maxheadres = headres
            except IndexError:
                heads = False
        if "SUM OF SQUARED DIFFERENCE:" in LST[i]:
            diff = LST[i].strip().split()[-1]
            if diff == "NaN":
                maxheadres = 'NaN'
            print "Max. head residual: {0:.2f}\n".format(maxheadres)




