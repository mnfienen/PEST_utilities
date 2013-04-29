# Prints list of all machines with associated Condor nodes
# also lists machines with failed runs (and failed nodes)
# reads from BeoPEST rmr file

# Input PEST basename
basename='bro03'

import os
from collections import Counter
from collections import defaultdict

basepath=os.path.join('cal_slave','')+basename

rmrdata=open(basepath+'.rmr').readlines()

workers=defaultdict()
failures=[]

for line in rmrdata:
    if "assigned to node at working directory" in line:
        node=line.split()[5]
        worker=line.split()[-1][:15]
        if worker[-1]=='\\':
            worker=worker[1:-1]
        else:
            worker=worker[1:]
        try:
            workers[worker].append(node)
        except KeyError:
            workers.setdefault(worker, []).append(node)
    if "model run failure" in line:
        node=line.split()[8][:-1]
        failures.append(node)
        
problem_workers=defaultdict()

for f in failures:
    for worker in workers:
        if f in workers[worker]:
            try:
                problem_workers[worker].append(f)
            except KeyError:
                problem_workers.setdefault(worker, []).append(f)
        
print "Worker \t\t\tcondor indices"
for worker in sorted(workers.items()):
    print str(worker[0]) + "\t\t" + str(worker[1])
    
print "\r\n"
print "\r\n"

print "Failures"
for p in problem_workers:
    print str(p) + '\t\t\t' + str(problem_workers[p])
