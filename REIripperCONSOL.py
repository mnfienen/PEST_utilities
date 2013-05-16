import numpy as np
import matplotlib.pyplot as plt
from scipy.stats import shapiro
from matplotlib.backends.backend_pdf import PdfPages

def resid_proc(reis,remove_zero_wt,grpfiles):
    for cf in reis:
        infile = reis[cf]
        # open a pointer to the output file
        ofp = open(infile + '_residuals_summary.dat','w')
        ofp.write('Residuals Summary information for -> ' + infile + '\n')
        # read in the data
        alldat = np.genfromtxt(infile,names=True,skip_header=6,dtype=None)
        
        # find the unique list of groups by which plots and stats will be managed
        allgrps = np.unique(alldat['Group'])
        
        # loop over the groups
        for cg in allgrps:
            # identify indices of the current group
            tmpinds = np.nonzero(alldat['Group']==cg)[0]
            if remove_zero_wt:
                inds = tmpinds[np.nonzero(alldat['Weight'][tmpinds] != 0)]
            else:
                inds = tmpinds
            # pull out the measured values for the group
            cmeas = alldat['Measured'][inds]
            # pull out the modeled values for the group
            cmod =  alldat['Modelled'][inds]
            
            #get some values to limit plotting areas
            cmin = np.min([cmeas,cmod])
            cmax = np.max([cmeas,cmod])
            
            # make a plot of modeled vs. measured
            plt.figure()
            plt.hold = True
            
            plt.plot(cmeas,cmod,'bx')
            plt.plot([cmin,cmax],[cmin,cmax],'r')
            plt.title(cg + ' iteration ' + str(cf))
            # append the histograms into the proper PDF file
            grpfiles[cg][0].savefig()
        
            # now calculate statistics on the residuals
            
            # first grab the residuals
            cres = alldat['Residual'][inds]
            
            # next calculate the relevant statistics and write to the output file
            cmean = np.mean(cres)
            cstd  = np.std(cres)
            cvar  = np.var(cres)
            cmed  = np.median(cres)
            cmin  = np.min(cres)
            camin = np.min(np.abs(cres))
            cmax  = np.max(cres)
            camax = np.max(np.abs(cres))
            plt.close('all')
            # finally plot the histogram and save it
            fig = plt.figure()
            ax = fig.add_subplot(111)
            n, bins, patches = ax.hist(cres, 50, facecolor='blue', alpha=0.75)
            ax.set_xlabel('Residual Value')
            ax.set_ylabel('Count')
            ax.set_title(cg + ' iteration ' + str(cf))
            ax.set_xlim([cmin,cmax])
            # append the histograms into the proper PDF file
            grpfiles[cg][1].savefig()
            plt.close('all')
            # perform the Shapiro-Wilks test for normality of the residuals
            W,p = shapiro(cres)
            
            # write to the summary output file
            ofp.write(25*'#' + '\n')
            ofp.write('Summary Statistics for Residuals: -> group ' + cg +'\n')
            ofp.write('%14s : %f\n' %('mean',cmean))
            ofp.write('%14s : %f\n' %('median',cmed))
            ofp.write('%14s : %f\n' %('std deviation',cstd))
            ofp.write('%14s : %f\n' %('variance',cvar))
            ofp.write('%14s : %f\n' %('min',cmin))
            ofp.write('%14s : %f\n' %('max',cmax))
            ofp.write('%14s : %f\n' %('min (absolute)',camin))
            ofp.write('%14s : %f\n' %('max (absolute)',camax))
            if p > 0.05:
                ofp.write('Residuals are not normally distributed\n')
            else:
                ofp.write('Residuals are normally distributed\n')
            ofp.write('p-value = %f' %(p))
            ofp.write(3*'\n')
        ofp.close()
# close the PDF files
    for cg in grpfiles:
        for i in range(2):
            grpfiles[cg][i].close()