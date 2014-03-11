__author__ = 'aleaf'

import xml.etree.ElementTree as ET
import os
import re
import pandas as pd
from collections import OrderedDict
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages

infile = 'Postproc_input.XML'
try:
    inpardat = ET.parse(infile)
except:
    raise IOError("Cannot open {0}!".format(infile))

inpars = inpardat.getroot()

# input
path = inpars.findall('.//path')[0].text
basename = inpars.findall('.//pest_basename')[0].text
outpdf = os.path.join(path,'{0}_rec.pdf'.format(basename))

# open rec file
indat = open(os.path.join(path, '{0}.rec'.format(basename))).readlines()

read_itr_info = False
phi_r = False
print "\nReading {0}.rec...".format(os.path.join(path,basename))
for i in range(len(indat)):

    if "optimisation iteration no." in indat[i].lower():
        read_itr_info = True
        itr = int(indat[i].strip().split()[-1])
    if read_itr_info:
        if "Current regularisation weight factor" in indat[i]:
            reg_wf = float(indat[i].strip().split()[-1])
            phi_m = float(indat[i+1].strip().split()[-1])
            phi_r = float(indat[i+2].strip().split()[-1])

        if "Starting phi for this iteration" in indat[i]:
            if not phi_r:
                phi_m = float(indat[i].strip().split()[-1])
            itr_info = OrderedDict()
            itr_info['phi_m'] = phi_m

        if "New starting objective function" in indat[i]:
            phi_t = float(indat[i].strip().split()[-1])
            itr_info = OrderedDict()
            itr_info['phi_t'] = phi_t
            itr_info['phi_m'] = phi_m
            itr_info['phi_r'] = phi_r
            itr_info['reg_wf'] = reg_wf

        if "Contribution to phi from observation group" in indat[i]:
            # note: if regularisation is being used, the group values will be rewritten with updated weight factor
            group = re.findall('"([^"]*)"', indat[i])[0]
            phi = float(indat[i].strip().split()[-1])
            itr_info[group] = phi

        if "Lambda" in indat[i]:
            read_itr_info = False
            df = pd.DataFrame(itr_info, index=[itr])
            if itr == 1:
                df_all = df.copy()
                continue
            else:
                df_all = df_all.append(df)

# save results to table
print "Saving results to {0}".format(os.path.join(path, basename+'_rec.csv'))
df_all.index.name = "PEST_iteration"
df_all.to_csv(os.path.join(path, basename+'_rec.csv'))

# plot results to pdf
print "Saving plots to {0}".format(os.path.join(path, outpdf))
pdf = PdfPages(os.path.join(path,outpdf))
phis = [n for n in df_all.columns if 'phi' in n]
params = {'legend.fontsize': 12}
plt.rcParams.update(params)
df_all[phis].plot()
pdf.savefig()
groups = [n for n in df_all.columns if 'phi' not in n and 'regul' not in n and 'reg_wf' not in n]
ax = df_all[groups].plot()
ax.set_ylabel('Phi contribution')

pdf.savefig()
pdf.close()









