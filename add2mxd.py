import arcpy
import os

rootname = 'br_kc_rei_3'


print 'set the workspace location...'
arcpy.env.workspace = os.getcwd()
fileroot = os.getcwd()

#if os.path.exists(os.path.join(os.getcwd(),"bad_river2.mxd")):
#	os.remove(os.path.join(os.getcwd(),"bad_river2.mxd"))

print 'open the mxd file'
### Adding shapefile to the mxd at the top of the TOC
mxd = arcpy.mapping.MapDocument(r"Y:/Documents/MODELING_CENTER/PENOKEE_MINING/GFLOW_OPT_RESULTS/test/bad_river.mxd")
df = arcpy.mapping.ListDataFrames(mxd,"*")[0]
print 'Add all the layers---->'

infiles = open('arcfiles_' + rootname + '.dat','r').readlines()
for line in infiles:	
	filename = os.path.join(os.getcwd(),line.strip())
	print 'adding %s' %(filename)
	newlayer = arcpy.mapping.Layer(filename)
	arcpy.mapping.AddLayer(df, newlayer,"TOP")


print 'saving down a copy to ->\n%s' %(os.path.join(os.getcwd(),"bad_river2.mxd"))
mxd.saveACopy("bad_river2.mxd")

# Refresh things
arcpy.RefreshActiveView()
arcpy.RefreshTOC()

print "Adding shapefile to mxd.... complete"

