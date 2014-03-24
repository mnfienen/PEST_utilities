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
        self.HEADTOL = None
        self.FLUXTOL = None
        self.MAXITEROUT = None
        self.THICKFACT = None
        self.LINMETH = None
        self.IPRNWT = None
        self.IBOTAV = None
        self.OPTIONS = None
        self.DBDTHETA = None
        self.DBDKAPPA = None
        self.DBDGAMMA = None
        self.MOMFACT = None
        self.BACKFLAG = None
        self.MAXBACKITER = None
        self.BACKTOL = None
        self.BACKREDUCE = None
        self.MAXITINNER = None
        self.ILUMETHOD = None
        self.LEVFILL = None
        self.STOPTOL = None
        self.MSDR = None
        self.IACL = None
        self.NORDER = None
        self.LEVEL = None
        self.NORTH = None
        self.IREDSYS = None
        self.RRCTOLS = None
        self.IDROPTOL = None
        self.EPSRN = None
        self.HCLOSEXMD = None
        self.MXITERXMD = None
        self.CONTINUE = False

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
        self.basepars.HTOL = float(line1[0])
        self.basepars.FLUXTOL = float(line1[1])
        self.basepars.MAXITEROUT = int(line1[2])
        self.basepars.THICKFACT = float(line1[3])
        self.basepars.LINMETH = int(line1[4])
        self.basepars.IPRNWT = int(line1[5])
        self.basepars.IBOTAV = int(line1[6])
        self.basepars.OPTIONS = line1[7].upper()

        #  special case to check for CONTINUE
        if len(line1) == 17:
            if line1[8].upper() == 'CONTINUE':
                junk = line1.pop(0)
                self.basepars.CONTINUE = True

        if self.basepars.OPTIONS == 'SPECIFIED':
            self.basepars.DBDTHETA = float(line1[8])
            self.basepars.DBDKAPPA = float(line1[9])
            self.basepars.DBDGAMMA = float(line1[10])
            self.basepars.MOMFACT = float(line1[11])
            self.basepars.BACKFLAG = float(line1[12])
            self.basepars.MAXBACKITER = float(line1[13])
            self.basepars.BACKTOL = float(line1[14])
            self.basepars.BACKREDUCE = float(line1[15])

            line2 = NWTdata.pop(0)
            if self.basepars.LINMETH == 1:
                self.basepars.MAXITINNER = int(line2[0])
                self.basepars.ILUMETHOD = int(line2[1])
                self.basepars.LEVFILL = int(line2[2])
                self.basepars.STOPTOL = int(line2[3])
                self.basepars.MSDR = int(line2[4])
            elif self.basepars.LINMETH == 2:
                self.basepars.IACL = int(line2[0])
                self.basepars.NORDER = int(line2[1])
                self.basepars.LEVEL = int(line2[2])
                self.basepars.NORTH = int(line2[3])
                self.basepars.IREDSYS = int(line2[4])
                self.basepars.RRCTOLS = float(line2[5])
                self.basepars.IDROPTOL = int(line2[6])
                self.basepars.EPSRN = float(line2[7])
                self.basepars.HCLOSEXMD = float(line2[8])
                self.basepars.MXITERXMD = int(line2[9])




        i=1
    def writeNWTfiles(self, allpars):
        i = 1

NWT = NWTtester(sys.argv[1])

NWT.read_infile()
NWT.read_base_NWTfile()

i=1