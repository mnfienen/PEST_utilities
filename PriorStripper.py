# prior stripper
# strips out prior information equations for all fixed parameters in a PEST control file
import numpy as np
from collections import OrderedDict

infile = 'rc_final3.pst'
outfile= 'rc_final3a.pst'
alldata = OrderedDict()
indat = open(infile,'r').readlines()

killpars = list()
# first find the divider lines in the input data

for i,line in enumerate(indat):
    if '* parameter data' in line:
        pardatSTART = i+1
    elif '* observation groups' in line:
        pardatEND = i
    elif '* prior information' in line:
        priordatSTART = i+1
    elif '* regulari' in line:
        priordatEND = i

# parse up the input into chunks for later output

# first (KEY THING!) is to pull off the counters
counters = indat[3].strip().split()
alldata['begindat'] = indat[:pardatSTART]
alldata['pardat'] = indat[pardatSTART:pardatEND]
alldata['middat'] = indat[pardatEND:priordatSTART]
alldata['priordat'] = np.array(indat[priordatSTART:priordatEND])
alldata['enddat'] = indat[priordatEND:]
ofp = open(outfile,'w')

# read in the parameter data to see what is fixed
for line in alldata['pardat']:
    if line.split()[1].lower() == 'fixed':
        killpars.append(line.split()[0].lower())

# slow loops, but quicker to code!
for cv in killpars:
    kill = list()
    print 'removing prior information for --> %s' %cv
    for i,line in enumerate(alldata['priordat']):
        if cv in line.lower():
            kill.append(i)
    alldata['priordat'] = np.delete(alldata['priordat'],kill)   


# update the counters
counters[3] = len(alldata['priordat'])

alldata['begindat'][3] = ' '.join(str(l) for l in counters)
# update the output file
print 'updating the output file --> %s' %outfile

for csec in alldata:
    for line in alldata[csec]:
        ofp.write(line.strip() + '\r\n')
ofp.close()

print '\n' + '#' * 30
print 'Adjustable parameters = %d' %(int(counters[0])-len(killpars))
print '#' * 30 + '\n'
