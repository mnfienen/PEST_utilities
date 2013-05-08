# Prints list of all machines with associated Condor nodes
# also lists machines with failed runs (and machines with both failed and completed runs)
# reads from BeoPEST rmr file

# Right now the code is kind of ugly but it works. Feel free to clean it up and make improvements!

import os
from collections import defaultdict

# Input PEST basename
basename='bro03'

basepath=os.path.join('cal_slave',basename)

rmrdata=open(basepath+'.rmr').readlines()

nodesbyIP=defaultdict()
IPsbynode=defaultdict()
runsbynode=defaultdict()
nodesbyrun=defaultdict()
failures=[]
finishes=[]
runs_with_failures=[]
completed_runs=[]
completedrunsbyIP=defaultdict()

for line in rmrdata:
    if "assigned to node at working directory" in line:
        node=line.split()[5]
        IP=line.split()[-1][:15]
        if IP[-1]=='\\':
            IP=IP[1:-1]
        else:
            IP=IP[1:]
        try:
            nodesbyIP[IP].append(node)
        except KeyError:
            nodesbyIP.setdefault(IP, []).append(node)
        try:
            IPsbynode[node].append(IP)
        except KeyError:
            IPsbynode.setdefault(node, []).append(IP)
    if "commencing on node" in line:
        run=line.split()[5]
        node=line.split()[9][:-1]
        try:
            runsbynode[node].append(run)
        except KeyError:
            runsbynode.setdefault(node, []).append(run)
        try:
            nodesbyrun[run].append(node)
        except KeyError:
            nodesbyrun.setdefault(run, []).append(node)
    if "model run failure" in line:
        node=line.split()[8][:-1]
        run=line.split()[13]
        failures.append(node)
        runs_with_failures.append(run)
    if "completed on node" in line:
        run=line.split()[5]
        node=line.split()[9][:-1]
        IP=IPsbynode[node][0]
        completed_runs.append(run)
        try:
            completedrunsbyIP[IP].append(run)
        except KeyError:
            completedrunsbyIP.setdefault(IP, []).append(run)

# Need to get indices of intersections between failed and completed runs,
# and use those to reference the worker IP

problem_workers=defaultdict()

for f in failures:
    for worker in nodesbyIP:
        if f in nodesbyIP[worker]:
            try:
                problem_workers[worker].append(f)
            except KeyError:
                problem_workers.setdefault(worker, []).append(f)

# runs that failed and then were successfully completed

#failedthencompleted=defaultdict()
failedcomp=set(runs_with_failures).intersection(set(completed_runs))

'''
for fc in failedcomp:
    for node in runsbynode:
        if fc in runsbynode[node]:
            try:
                failedthencompleted[node].append(fc)
            except KeyError:
                failedthencompleted.setdefault(node, []).append(fc) '''    
                
# workers/nodes that had a failure and a successful run
failedcomp_nodes=defaultdict()
for IP in completedrunsbyIP:
    if IP in problem_workers.iterkeys():
        try:
            failedcomp_nodes[IP].append(problem_workers[IP])
        except KeyError:
            failedcomp_nodes.setdefault(IP, []).append(problem_workers[IP])

print "Worker \t\t BeoPEST nodes"
for worker in sorted(nodesbyIP.items()):
    print worker[0] + "\t\t" + ','.join(worker[1])

print "\n"
print "\n"

print "Completed Runs"
print "Worker IP" + '\t\t' + "BeoPEST Runs"
for c in completedrunsbyIP:
    print str(c) + '\t\t' + ','.join(completedrunsbyIP[c])

print "\n"
print "\n"

print "Failures"
print "Worker IP" + '\t\t' + "BeoPEST Nodes"
for p in problem_workers:
    print str(p) + '\t\t' + ','.join(problem_workers[p])

print "\n"
print "\n"

print "Workers/nodes with both failed and completed runs"
print "Worker IP" + '\t\t' + "BeoPEST Node" + '\t\t' + "Failed Runs"
for IP in failedcomp_nodes.iterkeys():
    for node in failedcomp_nodes[IP][0]:
        for run in list(set(runs_with_failures).intersection(set(runsbynode[node]))):
            print IP + '\t\t' + node + '\t\t\t' + run
print "\n"
print "Worker IP" + '\t\t' + "BeoPEST Node" + '\t\t' + "Completed Runs"
for IP in failedcomp_nodes.iterkeys():
    for node in completedrunsbyIP[IP]:
        for run in list(set(completed_runs).intersection(set(runsbynode[node]))):
            print IP + '\t\t' + node + '\t\t\t' + run

print "\n"
print "\n"


print "Failures that finished successfully on second try"
print "Worker IP" + '\t\t' + "BeoPEST Node" + '\t\t' + "BeoPEST Runs"

for fc in list(failedcomp):
    runs=[]
    for node in nodesbyrun[fc]:
        if fc in runs:
            print IPsbynode[node][0] + '\t\t' + node + '\t\t' + fc + ' 2nd try'
        else:
            print IPsbynode[node][0] + '\t\t' + node + '\t\t' + fc
            runs.append(fc)
    
