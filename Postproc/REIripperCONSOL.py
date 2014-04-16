import os
import numpy as np
import matplotlib.pyplot as plt
from scipy.stats import shapiro
import pandas as pd
from matplotlib.backends.backend_pdf import PdfPages

def resid_proc(reis, remove_zero_wt, grpfiles, pareto, groups_rei):
    print "aggregating statistics and plotting by observation group..."
    print "PEST iteration:"
    for cf in reis:
        print '{0} '.format(cf),
        infile = reis[cf]

        # open a pointer to the output file
        rei_summary_folder='residuals_summaries'
        if not os.path.exists(rei_summary_folder):
            os.makedirs(rei_summary_folder)
            
        ofp = open(os.path.join(rei_summary_folder,infile + '_residuals_summary.dat'),'w')
        ofp.write('Residuals Summary information for -> ' + infile + '\n')

        # read in the data
        alldat = np.genfromtxt(infile,names=True,skip_header=4,dtype=None)
                # if processing PEST pareto results, read in groups from another REI
        if pareto:
            try:
                rei_groups_df = pd.read_csv(groups_rei, delim_whitespace=True, skiprows=6, index_col='Name')
                #if np.isnan(np.max(rei_groups_df.ix[:,0])):
                    #rei_groups_df = rei_groups_df[rei_groups_df.columns[1:]]
                    # for observations that were read in, reassign the entry in 'Group' column to group from other REI
                for observation in alldat:
                    observation['Group'] = rei_groups_df.ix[observation['Name'], 'Group']

            except IOError:
                print "Cannot open {0}. Please provide an non-pareto REI file so that observations can be analyzed by group."
                quit()
        # find the unique list of groups by which plots and stats will be managed
        allgrps = np.unique(alldat['Group'])
        allgrps = [g for g in allgrps if 'regul' not in g]    
        
        # loop over the groups
        for cg in allgrps:
            # identify indices of the current group
            tmpinds = np.nonzero(alldat['Group']==cg)[0]
            if remove_zero_wt:
                inds = tmpinds[np.nonzero(alldat['Weight'][tmpinds] != 0)]
                
                # not sure what the "remove_zero_weight" option is for, but for groups
                # that are zero weighted, it results in an empty "inds" array, causing python to crash
                if len(inds)==0:
                    inds = tmpinds
            else:
                inds = tmpinds
            # pull out the measured values for the group
            cmeas = alldat['Measured'][inds]
            # pull out the modeled values for the group
            cmod =  alldat['Modelled'][inds]
            
            #get some values to limit plotting areas
            try:
                cmin = np.min([cmeas,cmod])
                cmax = np.max([cmeas,cmod])
            # if the last rei is from an iteration where PEST failed, will have unreasonable values (i.e. -1e300)
            # that will cause a TypeError here
            except TypeError:
                continue


        
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

            if len(grpfiles) > 1:
            # make a plot of modeled vs. measured
                plt.figure()
                plt.hold = True

                plt.plot(cmeas,cmod,'bx')
                plt.plot([cmin,cmax],[cmin,cmax],'r')
                plt.title('Observation Group "%s", PEST iteration %s' %(cg, cf))
                plt.xlabel('Measured')
                plt.ylabel('Modeled')
                # append the histograms into the proper PDF file
                grpfiles[cg][0].savefig()
                #plt.close()

            # finally plot the histogram and save it
            fig = plt.figure()
            ax = fig.add_subplot(111)
            n, bins, patches = ax.hist(cres, 50, facecolor='blue', alpha=0.75)
            ax.set_xlabel('Residual Value')
            ax.set_ylabel('Count')
            ax.set_title(cg + ' iteration ' + str(cf))
            ax.set_xlim([cmin,cmax])
            # append the histograms into the proper PDF file
            grpfiles[cg][-1].savefig()
            #plt.close()

            # perform the Shapiro-Wilks test for normality of the residuals
            if len(cres)>2:
                W,p = shapiro(cres)
            
            if len(cres) > 2:
                W,p = shapiro(cres)
            else:
                p = -99999
                
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
            
            if p > 0.05:
                ofp.write('Residuals are not normally distributed\n')
                ofp.write('p-value = %f' %(p))
            elif p < -99:
                ofp.write('Residuals normality not calculable: Too few residuals in group\n')
            else:
                ofp.write('Residuals are normally distributed\n')
                ofp.write('p-value = %f' %(p))
    
            ofp.write(3*'\n')
        ofp.close()
    # close the PDF files
    for cg in grpfiles:
        for i in range(len(grpfiles)):
            grpfiles[cg][i].close()
            
def Best_summary_plot(reis,groups,markers,colors,sizes,title,units,number_format,Legend,outfile,obstype, pareto=False,
                      groups_rei=None):

    print "\nmaking summary plots of all {0} groups".format(obstype)
    print "PEST iteration:"
    for cf in reis:

        print '{0} '.format(cf),
        infile = reis[cf]

        # read in the data
        alldat = np.genfromtxt(infile, names=True, skip_header=4, dtype=None)

        # if processing PEST pareto results, read in groups from another REI
        if pareto:
            try:
                rei_groups_df = pd.read_csv(groups_rei, delim_whitespace=True, skiprows=6, index_col='Name')
                #if np.isnan(np.max(rei_groups_df.ix[:,0])):
                    #rei_groups_df = rei_groups_df[rei_groups_df.columns[1:]]
                    # for observations that were read in, reassign the entry in 'Group' column to group from other REI

                # update dtype of 'Group' column in alldat to accomodate longer group names
                alldat = alldat.astype([('Name', 'S20'), ('Group', 'S20'), ('Measured', '<f8'), ('Modelled', '<f8'), ('Residual', '<f8'), ('Weight', '<f8')])
                for i in range(len(alldat)):
                    alldat['Group'][i] = rei_groups_df.ix[alldat['Name'][i], 'Group']
                    #groupz.append(rei_groups_df.ix[alldat['Name'][i], 'Group'])
            except IOError:
                print "Cannot open {0}. Please provide an non-pareto REI file so that observations can be analyzed by group."
                quit()

        # find the unique list of groups by which plots and stats will be managed
        allgrps = list(np.unique(alldat['Group']))
        #allgrpz = list(np.unique(groupz))
        allgrps = [g for g in allgrps if 'regul' not in g]
        if obstype == 'flux':
            j=2
        fig=plt.figure()
        ax=fig.add_subplot(1,1,1)
        #ax=plt.subplot(1,1,1)
        #plt.hold=True
        # if no title given, base title on PEST iteration
        if len(title)==0:
            title='PEST iteration %s' %(cf)
        plt.title(title+' PEST iteration %s' %(cf))
        ax.set_xlabel('Measured %s' %(units))
        ax.set_ylabel('Modeled %s' %(units))
        
        
        # reverse everything so best plot on top
        #groups.reverse(),markers.reverse(),colors.reverse(),sizes.reverse()
        cmin,cmax=10000,0
        # loop over the groups
        for i in range(len(groups)):
            # identify indices of the current group
            inds = np.nonzero(alldat['Group']==groups[i].lower())[0]
        
            # pull out the measured values for the group
            cmeas = alldat['Measured'][inds]
            # pull out the modeled values for the group
            cmod =  alldat['Modelled'][inds]
            #get some values to limit plotting areas
            try:
                if np.min([cmeas,cmod]) < cmin:
                    cmin=np.min([cmeas,cmod])
                # if max value is > 0 but still a reasonable number (i.e. not from a failed run)
                if np.max([cmeas,cmod]) > cmax and np.max([cmeas,cmod]) < 1e100:
                    cmax=np.max([cmeas,cmod])
            # if the last rei is from an iteration where PEST failed, will have unreasonable values (i.e. -1e300)
            # that will cause a TypeError here
            except: #TypeError:
                continue
            
            ax.plot(cmeas,cmod,color=colors[i],marker=markers[i],markersize=sizes[i],linestyle='None',label=groups[i],zorder=len(groups)-i)
            
        handles,labels=ax.get_legend_handles_labels()
        ax.plot([cmin,cmax],[cmin,cmax],'r')
        ax.set_xlim([cmin,cmax])
        ax.set_ylim([cmin,cmax])
        
        if Legend:
            ax.legend(handles,labels,numpoints=1,loc=4)
        if len(number_format)>0:
            ax.ticklabel_format(style='sci',axis='x', scilimits=(-3,3))
            ax.ticklabel_format(style='sci',axis='y', scilimits=(-3,3))
            
            # kind of kludgy, but if model failed, this will skip plotting of last iteration
            # as cmax will not be a proper number
            try:
                if cmax == 0:
                    continue
                magnitude="{:,}".format(10**int(np.log10(cmax)))
            except:
                continue
                
            ax.set_xlabel('Measured %s x %s' %(units,magnitude))
            ax.set_ylabel('Modeled %s x %s' %(units,magnitude))
        outfile.savefig()
    outfile.close()
    