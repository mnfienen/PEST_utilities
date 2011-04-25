#recRipper.py
#
# a m!ke@usgs joint --> mnfienen@usgs.gov
# reads a PEST REC file and parses out the data for plotting
#

######
# get the file name for the .rec file from the .par file
######
def read_par_file():
    import string
    infile=open("recRipper.par","r")
    tmp=string.split(infile.next())
    parname=tmp[0]
    tmp=string.split(infile.next())
    regFLAG=bool(string.lower(tmp[0])=='true')
    
    print "\n Reading PEST run information from:-> ",parname,"\n"
    infile.close()
    return parname, regFLAG


######
#  function to parse the observation groups from the observations list
######
def parse_obs(infile,i):
    import string, sets

    outty=[]
    # skip two lines and get into the meat of the list
    infile.next()
    i=i+1
    infile.next()
    i=i+1

    outty=[]
    while 1:
        i=i+1
        line=string.split(infile.next())
        if len(line)==0:
            break
        else:
            outty.append(line[3])
    return outty, i
######
# function to parse the phi part only
######
def parse_phi_groups(infile,i,recData,num_gps,hajime):
    import numpy as num
    TPV=num.zeros((num_gps,1))
    for k in range(num_gps):
        cline = infile.next()
        i=i+1
        for j in range(num_gps):
            if cline.find(recData.phi_grps[j])>-1:
                spline = cline.split()
                TPV[j,0] =  float(spline[len(spline)-1])                
    if hajime:
        recData.phi_vals =  TPV
    else:
        recData.phi_vals = num.concatenate([recData.phi_vals,TPV],axis=1)
        
######
#   Function to parse the components of uber phi for regularizaiton
######
def parse_phi_regul(infile,i,recData,hajime):
    cline=infile.next()
    i=i+1
    if cline.find("Current regularisation weight factor") > -1:
        spline=cline.split()
        if hajime:
            recData.reg_wt[0]=float(spline[len(spline)-1])
        else:
            recData.reg_wt.append(float(spline[len(spline)-1]))
    cline=infile.next()
    i=i+1
    if cline.find("measurement objective function") > -1:
        spline=cline.split()
        if hajime:
            recData.phim[0]=float(spline[len(spline)-1])
        else:
            recData.reg_wt.append(float(spline[len(spline)-1]))
    cline=infile.next()
    i=i+1
    if cline.find("regularisation objective function") > -1:
        spline=cline.split()
        if hajime:
            recData.phir[0]=float(spline[len(spline)-1])
        else:            
            recData.phir.append(float(spline[len(spline)-1]))
    
######
#   Function to parse the initial conditions out 
######
def parse_init_phi(infile,i,recData):
    num_gps = len(recData.phi_grps)
    while True:
        cline=infile.next()
        i=i+1    
        if cline.find("Sum of squared weighted residuals (ie phi)")>-1:
            spline = cline.split()
            recData.total_phi[0]=(float(spline[len(spline)-1]))
            break
    parse_phi_groups(infile,i,recData,num_gps,True)

######
#   Function to parse the incremental iteration information
######
def parse_iteration_phi(infile,i,recData,regFLAG):
    import numpy as num
    num_gps = len(recData.phi_grps)
    cline=infile.next()
    i=i+1
    if cline.find("Model calls so far")>-1:
        spline = cline.split()
        recData.mod_calls.append(int(spline[len(spline)-1]))
        if regFLAG:
            while True:
                cline=infile.next()
                i=i+1
                if cline.find("Re-calculated regularisation weight factor")>-1:
                    spline=cline.split()    
                    recData.reg_wt.append(float(spline[len(spline)-1]))
                    recData.curr_iter.append\
                    (recData.curr_iter[len(recData.curr_iter)-1]+0.1)
                    cline=infile.next()
                    i=i+1
                    # handle the special case of isntability which means multiple
                    # lines will have "Re-calculated" in the line text
                    if cline.find("Instability")>-1:
                        recData.reg_wt.pop()
                        recData.curr_iter.pop()
                    elif cline.find("New starting objective function for this")>-1:
                        spline = cline.split()
                        recData.total_phi.append(float(spline[len(spline)-1]))   
                        break
                elif cline.find("New starting objective function for this")>-1:
                    spline = cline.split()
                    recData.total_phi.append(float(spline[len(spline)-1]))   
                    break
        else:
            cline=infile.next()
            i=i+1
            if cline.find("Starting phi for this iteration")>-1:
                spline = cline.split()
                recData.total_phi.append(float(spline[len(spline)-1]))   
    parse_phi_groups(infile,i,recData,num_gps,False)
    
######
# Set up a class for the data to live in
######
class runStats:
    def __init__(self,num_grps,grp_nms,regFLAG):
        import numpy as num, array as ar
        self.phi_grps   = grp_nms
        self.phi_vals   = num.zeros((num_grps,1))
        self.mod_calls  = [0]
        self.total_phi  = ar.array('f',[0])
        self.curr_iter  = [0]
        if regFLAG==True:
            self.phim       = ar.array('f',[0])
            self.phir       = ar.array('f',[0])
            self.reg_wt     = ar.array('f',[0])
            
    

######
# Uber control for reading in the REC file
######
def read_rec_file(fn,regFLAG):
    import string, sets
    import numpy as num
# open the file    
    infile =open(fn,"r")
    chkobs = i = 0;
    priorGrps=[]
    while True:
        try:
            cline=infile.next()
            i=i+1
            if not chkobs and cline.find("Prior Info Name") > -1:
                while 1:
                    i=i+1
                    line=string.split(infile.next())
                    if len(line)==0:
                        break
                    else:
                        priorGrps.append(line[1])
                priorGrps=list(sets.Set(priorGrps))
                
            if not chkobs and cline.find("Observations:-") > -1:
                # parse out only the observation names
                obsGrps,i=parse_obs(infile,i)
                # make a UNIQUE list of obsGrps
                obsGrps=list(sets.Set(obsGrps))
                if priorGrps:
                    obsGrps.extend(priorGrps)
                chkobs = 1
                recData = runStats(len(obsGrps),obsGrps,regFLAG)
                recData.phi_grps=obsGrps
                num_grps = len(recData.phi_grps)
            elif cline.find("INITIAL CONDITIONS") > -1:
                hajime=True
                if regFLAG:
                    parse_phi_regul(infile,i,recData,hajime)
                parse_init_phi(infile,i,recData)
                hajime=False
            elif cline.find("OPTIMISATION ITERATION") > -1:
                spline=cline.split()
                recData.curr_iter.append(int(spline[len(spline)-1]))
                parse_iteration_phi(infile,i,recData,regFLAG)
        except StopIteration:
            print i
            print "\nReached the end of the file.\n"
            break
            infile.close()
# Call output writer
    write_output(fn,recData,regFLAG)

######
# Control for writing the output file
######
def write_output(fn,recData,regFLAG):
    import string as str,numpy as num
    ofn=fn.replace(".rec",".recout")        # file for Google Motion Charts Input
    ofp=open(ofn,'w')
    if regFLAG:
        ofp.write\
        ("Phi_Component\tIteration\tComponent_Value\tTotal_Phi\tModel_Calls" + \
         "\tReg_Weight\tPhi_Component\n")
        for cl in range(len(recData.mod_calls)):
            for cp in range(len(recData.phi_grps)):
                ofp.write(recData.phi_grps[cp] + '\t' + repr(cl+1900) +'\t' + \
                repr(recData.phi_vals[cp,cl]) + '\t' + \
                repr(recData.total_phi[cl]) + '\t' + \
                repr(recData.mod_calls[cl]) + '\t' + repr(recData.reg_wt[cl]) + \
                '\t' + recData.phi_grps[cp] + '\n' )
    else:
        ofp.write("Phi_Component\tIteration\tComponent_Value\tTotal_Phi" + \
        "\tModel_Calls\tPhi_Component\n")
        for cl in range(len(recData.mod_calls)):
            for cp in range(len(recData.phi_grps)):
                ofp.write(recData.phi_grps[cp] + '\t' + repr(cl+1900) +'\t' + \
                repr(recData.phi_vals[cp,cl]) + '\t' + \
                repr(recData.total_phi[cl]) + '\t' + \
                repr(recData.mod_calls[cl]) + \
                '\t' + recData.phi_grps[cp] + '\n' )
    ofp.close()

    ofntp=fn.replace(".rec",".rec_tphi")    # file only reporting total phi over iterations
    ofp2=open(ofntp,'w')
    ofp2.write("Iteration\tTotal_Phi\n")  
    for cl in range(len(recData.mod_calls)):
        ofp2.write(repr(cl) + '\t' + repr(recData.total_phi[cl]) + '\n')
    ofp2.close()
    
##############################
#   M A I N  F U N C T I O N #
##############################
# open up the rec file and start reading and parsing
#

#
# get parameter file name
(parname, regFLAG) = read_par_file()
#
# perform the main reading function
read_rec_file(parname,regFLAG)

