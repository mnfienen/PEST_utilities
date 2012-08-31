import arcpy
import os

rootname = 'br_kc_rei_3'
base_mxd = "bad_river"

print 'set the workspace location...'
arcpy.env.workspace = os.getcwd()
fileroot = os.getcwd()

#if os.path.exists(os.path.join(os.getcwd(),"bad_river2.mxd")):
#	os.remove(os.path.join(os.getcwd(),"bad_river2.mxd"))

print 'open the mxd file'
### Adding shapefile to the mxd at the top of the TOC
mxd = arcpy.mapping.MapDocument(r"%s.mxd" %(base_mxd))
df = arcpy.mapping.ListDataFrames(mxd,"*")[0]
print 'Add all the layers---->'

infiles = open('arcfiles_' + rootname + '.dat','r').readlines()
for line in infiles:	
	filename = os.path.join(os.getcwd(),line.strip())
	print 'adding %s' %(filename)
	newlayer = arcpy.mapping.Layer(filename)
	arcpy.mapping.AddLayer(df, newlayer,"TOP")
	#	
	# now set the layer symbology
	#
	if 'over' in filename:
		arcpy.ApplySymbologyFromLayer_management(newlayer, 
		        os.path.join(os.getcwd(),'over.lyr'))
	elif 'under' in filename:
		arcpy.ApplySymbologyFromLayer_management(newlayer, 
		        os.path.join(os.getcwd(),'under.lyr'))
	

print 'saving down a copy to ->\n%s' %(os.path.join(os.getcwd(),rootname + ".mxd"))
mxd.saveACopy(rootname + ".mxd")

# Refresh things
arcpy.RefreshActiveView()
arcpy.RefreshTOC()

print "Files added ... done for now!"
