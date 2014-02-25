from correlation_ripper import read_and_plot_correlations

infiles = ['arterialdisa3.rec',
           'feederfixed3.rec',
           'parkinglotfixed3.rec',
           'residentialfixed3.rec',
           'arterialfixed3.rec',
           'parkinglotdisa3.rec',
           'residentialdisa3.rec',
           'stripmallfixed3.rec']

for cf in infiles:
    read_and_plot_correlations(cf)