# adds streamflow output from SFR package to river_explode linework
import xml.etree.ElementTree as ET
import os
import sys
import shutil

try:
    infile = sys.argv[1]
except:
    infile = 'Postproc_input.XML'

try:
    inpardat = ET.parse(infile)
except:
    raise IOError("Cannot open {0}!".format(infile))

inpars = inpardat.getroot()

# bring in SFR plotting utility
sfr_utils_path = inpars.findall('.//SFR_utilities_path')[0].text
if sfr_utils_path not in sys.path:
    sys.path.append(sfr_utils_path)
import sfr_plots as SFRp

path = inpars.findall('.//path')[0].text
GIS_folder = inpars.findall('.//GIS_folder')[0].text
MFname = inpars.findall('.//MODFLOW_basename')[0].text
SFR_gis_lines = inpars.findall('.//SFR_gis_lines')[0].text
SFRoutfile = inpars.findall('.//SFRoutfile_name')[0].text
shutil.copy(os.path.join(path, SFRoutfile), os.path.join(path, GIS_folder, SFRoutfile))

# plot_streamflows arguments are (<MODFLOW DIS file>,<intersect> from SFR XML input file (or similar, <SFR package output file>)
stuff = SFRp.plot_streamflows(os.path.join(path,MFname+'.dis'), SFR_gis_lines, os.path.join(path, GIS_folder, SFRoutfile))
stuff.join_SFR_out2streams()
# can use symbology in SFR_flow_symbology.lyr to visualize flow in in ArcMap as line thickness