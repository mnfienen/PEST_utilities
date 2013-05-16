import numpy as np
import matplotlib.pyplot as plt

infile = 'arterialdisa3.rec'
def read_and_plot_correlations(infile):
    # read in the entier REC file
    indat = open(infile,'r').readlines()
    
    # find 'Parameter correlation coefficient matrix ----->'
    k=-1
    for line in indat:
        k+=1
        if 'number of parameters' in line.lower():
            NPAR = int(line.strip().split()[-1])
        if 'correlation coefficient matrix' in line:
            corr_start = k
        elif 'eigenvectors of parameter covariance matrix' in line:
            corr_end = k
            break
    corr_mat = indat[corr_start+1:corr_end]
    allpars = corr_mat.pop(0).strip().split()
    r_mat = list()
    r_mat.append('garbage')
    for line in corr_mat:
        tmp = line.strip().split()
        if len(tmp)>0:
            r_mat.extend(tmp)
    r_mat = np.array(r_mat).reshape(NPAR+1,NPAR+1)
    
    parcheck1 = r_mat[:,0]
    parcheck2 = r_mat[0,:]
    r_mat = np.atleast_2d(r_mat[1:,1:].astype(float))
    fig1 = plt.figure(figsize=(9,8))
    ax = fig1.add_subplot(111)
    plt.imshow(r_mat,interpolation='nearest',clim=[-1.0,1.0])
    plt.colorbar()
    plt.xticks(np.arange(NPAR),rotation='vertical')
    plt.yticks(np.arange(NPAR))
    ax.set_xticklabels(parcheck1[1:])
    ax.set_yticklabels(parcheck2[1:])
    
    # find the maximum correlation coefficient
    allabs = np.unique(np.abs(r_mat))
    allabs[allabs == 1.0] = 0.0
    
    
    plt.title(infile[:-4] + ' Max corr = %f' %(np.max(allabs)))
    
    #plt.show()
    plt.savefig(infile[:-4] + '.pdf')
            
