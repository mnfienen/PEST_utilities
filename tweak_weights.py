'''
simple code to read in a file and increase or decrease weights to be two orders of magnitude
above or below starting value.
'''

infile = 'pest_pm-all.pst'
outfile = 'pest_pm-allFIXED.pst'
windows_flag = True

'''
if windows_flag:
    lineend = '\r\n'
else:
    lineend = '\n'
'''

ofp = open(outfile,'w')

indat = open(infile,'r').readlines()
NPAR = int(indat[3].strip().split()[0])

cpar = 0
parflag = False
for i,line in enumerate(indat):
    if parflag == False:
        if '* parameter data' in line:
            parflag = True
        ofp.write(line)
    else:
        cpar+=1
        cline = line.strip().split()
        cv = float(cline[3])
        lb = float(cline[4])
        ub = float(cline[5])
        if cv - lb < 0:
            lb /= 100
        if ub - cv < 0:
            ub *= 100
        cline[4] = '%f' %(lb)
        cline[5] = '%f' %(ub)
        outline = ''
        for k in cline:
            outline += '%s ' %(k)
        outline += '\n'
        ofp.write(outline)
        if cpar == NPAR:
            parflag = False
ofp.close()