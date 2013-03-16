import arcpy
import os

rootname = 'br_kc_rei_10'
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
	
	#	
	# now add only the OVER and UNDER layers and tweak the layer symbology
	#
	if '0_over' in filename or 'd_over' in filename or 'r_over' in filename or 't_over' in filename or 'o_over' in filename:
		print 'adding %s' %(filename)
		newlayer = arcpy.mapping.Layer(filename)
		arcpy.mapping.AddLayer(df, newlayer,"TOP")		
		arcpy.ApplySymbologyFromLayer_management(newlayer, 
		        os.path.join(os.getcwd(),'over.lyr'))
	elif '0_under' in filename or 'd_under' in filename or 'r_under' in filename or 't_under' in filename or 'o_under' in filename:
		print 'adding %s' %(filename)
		newlayer = arcpy.mapping.Layer(filename)
		arcpy.mapping.AddLayer(df, newlayer,"TOP")				
		arcpy.ApplySymbologyFromLayer_management(newlayer, 
		        os.path.join(os.getcwd(),'under.lyr'))
	elif 'g_streams_under' in filename or 'd_streams_under' in filename or 'm_streams_under' in filename:
		print 'adding %s' %(filename)
		newlayer = arcpy.mapping.Layer(filename)
		arcpy.mapping.AddLayer(df, newlayer,"TOP")				
		arcpy.ApplySymbologyFromLayer_management(newlayer, 
		        os.path.join(os.getcwd(),'under_s.lyr'))
	elif 'g_streams_over' in filename or 'd_streams_over' in filename or 'm_streams_over' in filename:
		print 'adding %s' %(filename)
		newlayer = arcpy.mapping.Layer(filename)
		arcpy.mapping.AddLayer(df, newlayer,"TOP")				
		arcpy.ApplySymbologyFromLayer_management(newlayer, 
		        os.path.join(os.getcwd(),'over_s.lyr'))					

print 'saving down a copy to ->\n%s' %(os.path.join(os.getcwd(),rootname + ".mxd"))
mxd.saveACopy(rootname + ".mxd")

# Refresh things
arcpy.RefreshActiveView()
arcpy.RefreshTOC()

print "Files added ... done for now!"
