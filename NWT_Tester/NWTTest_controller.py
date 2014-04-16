import numpy as np
import xml.etree.ElementTree as ET
import sys

#  this class hold information about parameters to be tested
class NWTtestpar:
    def __init__(self, cname, lbound, ubound, numsteps):
        self.parname = cname
        self.lbound = lbound
        self.ubound = ubound
        self.numsteps = numsteps
        self.parvals = np.linspace(lbound, ubound, numsteps)

#  Set up the default parameters for NWT --- read from a base NWT file
class NWTpar:
    def __init__(self):
        self.pars = dict()
        self.pars['HEADTOL'] = None
        self.pars['FLUXTOL'] = None
        self.pars['MAXITEROUT'] = None
        self.pars['THICKFACT'] = None
        self.pars['LINMETH'] = None
        self.pars['IPRNWT'] = None
        self.pars['IBOTAV'] = None
        self.pars['OPTIONS'] = None
        self.pars['DBDTHETA'] = None
        self.pars['DBDKAPPA'] = None
        self.pars['DBDGAMMA'] = None
        self.pars['MOMFACT'] = None
        self.pars['BACKFLAG'] = None
        self.pars['MAXBACKITER'] = None
        self.pars['BACKTOL'] = None
        self.pars['BACKREDUCE'] = None
        self.pars['MAXITINNER'] = None
        self.pars['ILUMETHOD'] = None
        self.pars['LEVFILL'] = None
        self.pars['STOPTOL'] = None
        self.pars['MSDR'] = None
        self.pars['IACL'] = None
        self.pars['NORDER'] = None
        self.pars['LEVEL'] = None
        self.pars['NORTH'] = None
        self.pars['IREDSYS'] = None
        self.pars['RRCTOLS'] = None
        self.pars['IDROPTOL'] = None
        self.pars['EPSRN'] = None
        self.pars['HCLOSEXMD'] = None
        self.pars['MXITERXMD'] = None
        self.pars['CONTINUE'] = False

#  main tester class controls the testing environment including reading all the input and writing the files for NWT
class NWTtester:
    def __init__(self, infile):
        self.infile = infile
        self.alltestpars = dict()
        self.baseNWTfile = None
        self.basepars = NWTpar()


    def read_infile(self):
        inpardat = ET.parse(self.infile)
        inpars = inpardat.getroot()


        cpars = inpars.findall('.//parameter')
        for cpar in cpars:
            self.alltestpars[cpar.text] = NWTtestpar(
                cpar.text,
                float(cpar.attrib['lbound']),
                float(cpar.attrib['ubound']),
                float(cpar.attrib['numsteps']),

            )
        self.baseNWTfile = inpars.findall('.//baseNWTfile')[0].text

    def read_base_NWTfile(self):
        indat = open(self.baseNWTfile, 'r').readlines()

        NWTdata = []
        for line in indat:
            if '#' not in line:
                NWTdata.append(line.strip().split())
        #  read first line of the NWT file
        line1 = NWTdata.pop(0)
        self.basepars.pars['HTOL'] = float(line1[0])
        self.basepars.pars['FLUXTOL'] = float(line1[1])
        self.basepars.pars['MAXITEROUT'] = int(line1[2])
        self.basepars.pars['THICKFACT'] = float(line1[3])
        self.basepars.pars['LINMETH'] = int(line1[4])
        self.basepars.pars['IPRNWT'] = int(line1[5])
        self.basepars.pars['IBOTAV'] = int(line1[6])
        self.basepars.pars['OPTIONS'] = line1[7].upper()

        #  special case to check for CONTINUE
        if len(line1) == 17:
            if line1[8].upper() == 'CONTINUE':
                junk = line1.pop(0)
                self.basepars.pars['CONTINUE'] = True

        if self.basepars.pars['OPTIONS'] == 'SPECIFIED':
            self.basepars.pars['DBDTHETA'] = float(line1[8])
            self.basepars.pars['DBDKAPPA'] = float(line1[9])
            self.basepars.pars['DBDGAMMA'] = float(line1[10])
            self.basepars.pars['MOMFACT'] = float(line1[11])
            self.basepars.pars['BACKFLAG'] = float(line1[12])
            self.basepars.pars['MAXBACKITER'] = float(line1[13])
            self.basepars.pars['BACKTOL'] = float(line1[14])
            self.basepars.pars['BACKREDUCE'] = float(line1[15])

            line2 = NWTdata.pop(0)
            if self.basepars.pars['LINMETH'] == 1:
                self.basepars.pars['MAXITINNER'] = int(line2[0])
                self.basepars.pars['ILUMETHOD'] = int(line2[1])
                self.basepars.pars['LEVFILL'] = int(line2[2])
                self.basepars.pars['STOPTOL'] = int(line2[3])
                self.basepars.pars['MSDR'] = int(line2[4])
            elif self.basepars.pars['LINMETH'] == 2:
                self.basepars.pars['IACL'] = int(line2[0])
                self.basepars.pars['NORDER'] = int(line2[1])
                self.basepars.pars['LEVEL'] = int(line2[2])
                self.basepars.pars['NORTH'] = int(line2[3])
                self.basepars.pars['IREDSYS'] = int(line2[4])
                self.basepars.pars['RRCTOLS'] = float(line2[5])
                self.basepars.pars['IDROPTOL'] = int(line2[6])
                self.basepars.pars['EPSRN'] = float(line2[7])
                self.basepars.pars['HCLOSEXMD'] = float(line2[8])
                self.basepars.pars['MXITERXMD'] = int(line2[9])



    def writeNWTfile(self, cpars, outname):
        ofp = open(outname, 'w')

        ofp.write('{0} '.format(cpars['HTOL'])) 
        ofp.write('{0} '.format(cpars['FLUXTOL'])) 
        ofp.write('{0} '.format(cpars['MAXITEROUT']))
        ofp.write('{0} '.format(cpars['THICKFACT'])) 
        ofp.write('{0} '.format(cpars['LINMETH']))
        ofp.write('{0} '.format(cpars['IPRNWT']))
        ofp.write('{0} '.format(cpars['IBOTAV']))
        ofp.write('{0} '.format(cpars['OPTIONS']))
        if cpars['CONTINUE']:
            ofp.write('CONTINUE ')
        if cpars['OPTIONS'].upper() == 'SPECIFIED':
            ofp.write('{0} '.format(cpars['DBDTHETA']))
            ofp.write('{0} '.format(cpars['DBDKAPPA']))
            ofp.write('{0} '.format(cpars['DBDGAMMA']))
            ofp.write('{0} '.format(cpars['MOMFACT']))
            ofp.write('{0} '.format(cpars['BACKFLAG']))
            ofp.write('{0} '.format(cpars['MAXBACKITER']))
            ofp.write('{0} '.format(cpars['BACKTOL']))
            ofp.write('{0}\n'.format(cpars['BACKREDUCE']))
            if cpars['LINMETH'] == 1:
                ofp.write('{0} '.format(cpars['MAXITINNER']))
                ofp.write('{0} '.format(cpars['ILUMETHOD']))
                ofp.write('{0} '.format(cpars['LEVFILL']))
                ofp.write('{0} '.format(cpars['STOPTOL']))
                ofp.write('{0} '.format(cpars['MSDR']))
            elif cpars['LINMETH'] == 2:
                ofp.write('{0} '.format(cpars['IACL']))
                ofp.write('{0} '.format(cpars['NORDER']))
                ofp.write('{0} '.format(cpars['LEVEL']))
                ofp.write('{0} '.format(cpars['NORTH']))
                ofp.write('{0} '.format(cpars['IREDSYS']))
                ofp.write('{0} '.format(cpars['RRCTOLS']))
                ofp.write('{0} '.format(cpars['IDROPTOL']))
                ofp.write('{0} '.format(cpars['EPSRN']))
                ofp.write('{0} '.format(cpars['HCLOSEXMD']))
                ofp.write('{0} '.format(cpars['MXITERXMD']))

NWT = NWTtester(sys.argv[1])

NWT.read_infile()
NWT.read_base_NWTfile()
NWT.writeNWTfile(NWT.basepars.pars, 'NWTbasecase.NWT')
i=1