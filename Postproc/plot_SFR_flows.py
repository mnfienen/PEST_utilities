# adds streamflow output from SFR package to river_explode linework
import os
import sfr_plots as SFRp

path = 'Opt3b'
MFname = 'BadRiver'
SFRoutfile = os.path.join(path,MFname+'_streamflow.dat')
SFR_gis_lines = os.path.join('shps','river_explode.shp')

# plot_streamflows arguments are (<MODFLOW DIS file>,<intersect> from SFR XML input file (or similar, <SFR package output file>)
stuff = SFRp.plot_streamflows(os.path.join(path,MFname+'.dis'), SFR_gis_lines, SFRoutfile)
stuff.join_SFR_out2streams()
# can use symbology in SFR_flow_symbology.lyr to visualize flow in in ArcMap as line thickness