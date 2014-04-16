import numpy as np
import sys





# class to hold stress period information
class SP:
    def __init__(self, line):
        self.sp = int(line[0])
        self.length = float(line[1])
        self.numtsteps = int(line[2])
        if line[-1].lower() == 'ss':
            self.transflag = False
        else:
            self.transflag = True


def output_echo(line, ofp):
    print line
    ofp.write(line + '\n')

try:
    LSTfilename = sys.argv[1]
except:
    sys.exit('User needs to specify an input LST filename on the command line')


AllSPs = dict()


LST = open(LSTfilename, 'r').readlines()
# first get the time information
for i, line in enumerate(LST):
    if 'STRESS PERIOD(S)' in line:
        numSPs = [int(s) for s in line.split() if s.isdigit()][0]
    elif 'STRESS PERIOD' in line and 'MULTIPLIER' in line:
        for j in np.arange(i+2, i+2+numSPs):
            cline = LST[j].strip().split()
            AllSPs[int(cline[0])] = SP(cline)



ofp = open('{0}_NWT_SUMMARY.dat'.format(sys.argv[1]), 'w')



Residuals = False
discrep = False
heads = False
maxheadres = 0
allMBerror=list()
allMBerror_rate = list()
output_echo("NWT Summary: --> {0}".format(sys.argv[1]), ofp)
for i in range(len(LST)):
    if 'STRESS PERIOD' in LST[i] and 'LENGTH' in LST[i] and 'MULTIPLIER' not in LST[i]:
        output_echo(LST[i].strip(), ofp)
    if not Residuals and "NWT REQUIRED" in LST[i]:
#        Residuals = True
        dhMax = LST[i-3].strip().split()[6]
        dhInd = ' '.join(LST[i-3].strip().split()[3:6])
        dQMax = LST[i-3].strip().split()[10]
        dQInd = ' '.join(LST[i-3].strip().split()[7:10])
        L2new = LST[i-3].strip().split()[11]
        Solver_dhMax = LST[i-3].strip().split()[-1]
        output_echo("Max. Head Change: {0}  ({1})".format(dhMax,dhInd), ofp)
        output_echo("Max.-Flux-Residual: {0}  ({1})".format(dQMax,dQInd), ofp)
        output_echo("L2-New: {0}".format(L2new), ofp)
        output_echo("Solver-Max-Delh: {0}".format(Solver_dhMax), ofp)

        outer = int(''.join([s for s in LST[i] if s.isdigit()]))
        inner = int(''.join([s for s in LST[i+1] if s.isdigit()]))
        output_echo("Total outer: {0}\nTotal inner: {1}".format(outer, inner), ofp)
    if not discrep and "PERCENT DISCREPANCY" in LST[i]:
        MassBal_Error = LST[i].strip().split()[3]
        MassBal_Error_Rate = LST[i].strip().split()[-1]
        output_echo("Percent discrepancy: {0}".format(MassBal_Error), ofp)
        output_echo("Percent discrepancy Rate: {0}".format(MassBal_Error_Rate), ofp)
        if MassBal_Error.lower()=='NaN':
            allMBerror.append(np.nan)
        else:
            allMBerror.append(float(MassBal_Error))
        if MassBal_Error_Rate.lower()=='NaN':
            allMBerror_rate.append(np.nan)
        else:
            allMBerror_rate.append(float(MassBal_Error_Rate))
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
        output_echo("Max. head residual: {0:.2f}\n".format(maxheadres), ofp)

    if "ELAPSED RUN TIME" in LST[i].upper():
        output_echo('\n\n##########\n' + LST[i].strip() + '\n##########', ofp)
maxMBError = np.max(np.abs(allMBerror))
maxMBError_rate = np.max(np.abs(allMBerror_rate))
output_echo('Absolute Value of Maximum Mass Balance Percent Discrepancy: {0}'.format(maxMBError), ofp)
output_echo('Absolute Value of Maximum Mass Balance Percent Discrepancy Rate: {0}'.format(maxMBError_rate), ofp)

ofp.close()