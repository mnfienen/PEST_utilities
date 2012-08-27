'''
simple code to read in a file and increase or decrease weights to be two orders of magnitude
above or below starting value.
'''

infile = 'pest_pm-all.pst'
outfile = 'pest_pm-allFIXED.pst'

indat = open(infile.'r').readlines()
NPAR = int(indat[3].strip().split()][0])
for i,line in indat:
    if '* parameter data' in line:
        
    else:
        ofp.write(line)