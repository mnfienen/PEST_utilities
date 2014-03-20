import numpy as np
import matplotlib.pyplot as plt
#preliminary figure specifications
import matplotlib as mpl
from matplotlib.font_manager import FontProperties
import matplotlib.gridspec as gridspec

mpl.rcParams['font.sans-serif']          = 'Univers 57 Condensed'
mpl.rcParams['font.serif']               = 'Times'
mpl.rcParams['font.cursive']             = 'Zapf Chancery'
mpl.rcParams['font.fantasy']             = 'Comic Sans MS'
mpl.rcParams['font.monospace']           = 'Courier New'
mpl.rcParams['pdf.compression']          = 0
mpl.rcParams['pdf.fonttype']             = 42

ticksize = 12
mpl.rcParams['legend.fontsize']  = 14
mpl.rcParams['axes.labelsize']   = 16
mpl.rcParams['xtick.labelsize']  = ticksize
mpl.rcParams['ytick.labelsize']  = ticksize
import matplotlib.cm as cm

# function to plot 
numSVs = 40
basename = 'rc37u-pt14'
vecext = 'vec'
identext = 'ids'
IDthresh = 0.6
varalpha=False
indat = np.genfromtxt('%s.%s' %(basename,identext),names=True,dtype=None)

parnames = indat['parameter']
NPAR = len(parnames)

colors = cm.rainbow_r(np.linspace(0, 1, numSVs))

cumulID = np.zeros((NPAR,numSVs))

cumulID[:,0] = indat['eig1']

IDs = cumulID.copy()
for ccol in np.arange(1,numSVs):
    cumulID[:,ccol] = cumulID[:,ccol-1] + indat['eig%s' %(ccol+1)]
    IDs[:,ccol] = indat['eig%s' %(ccol+1)]
rowINDS = np.nonzero(indat['identifiability'] > IDthresh)[0]

# abbreviate to only value over a threshold
cumulIDs2plot = cumulID[rowINDS,:]
IDs2plot = IDs[rowINDS,:]
PAR2plot = parnames[rowINDS]
plt.close()
plt.figure(figsize=(8.2,5))
axmain=plt.subplot2grid((1,15),(0,0),colspan=13)


plt.hold(True)

inds = np.arange(len(PAR2plot))
curralpha=1.0
plt.bar(inds,IDs2plot[:,0],color=colors[0],alpha=curralpha)

for cSV in np.arange(1,numSVs):
    if cSV>0.8*numSVs and varalpha:
        curralpha = 0.25
    plt.bar(inds,IDs2plot[:,cSV],
            bottom=cumulIDs2plot[:,cSV-1],
            color=colors[cSV],
            alpha=curralpha)
plt.xticks(inds+0.5,PAR2plot,rotation=90)
plt.xlim([0,len(PAR2plot)])
plt.xlabel('Parameter')
plt.ylabel('Identifiability')

ax1=plt.subplot2grid((1,15),(0,13))
#ax1.axis('off')

norm = mpl.colors.Normalize(vmin=1, vmax=40)
cb_bounds = np.linspace(0,numSVs,numSVs+1).astype(int)[1:]
cb_axis = np.arange(0,numSVs+1,5)
cb_axis[0] = 1
cb1 = mpl.colorbar.ColorbarBase(ax1, cmap=cm.rainbow_r,
                                   norm=norm,
                                   boundaries=cb_bounds,
                                   orientation='vertical')
plt.tight_layout()
cb1.set_ticks(cb_axis)
cb1.set_ticklabels(cb_axis)
cb1.set_label('Number of Singular Values Considered')
plt.suptitle('Identifiability for Parameters with ID>{0:3.2f}'.format(IDthresh))
#plt.gcf().subplots_adjust(bottom=0.25)
plt.savefig('Identifiability.pdf')
