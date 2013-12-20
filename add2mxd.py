'''
def tf2flag(intxt):    
# converts text written in XML file to True or False flag    
if intxt.lower()=='true':        
    return True    
else:        
    return False
'''

# Script to plot PEST target residuals in ArcMap, with symbology according to size and type (head vs. stream)
# Inputs: 
# shp files containing the character string "rootname"
# a list of the shp files to process named 'arcfiles_rootname.dat'
# a pre-configured base mxd file
# pre-configured lyr files with symbology for stream and head residuals that are over and under



import arcpy
import os

rootname = 'menom8_040313_rei' # this specifies the PEST iteration to use in case there are shapefiles from multiple iterations in the same directory
base_mxd = "Menominee_Calibration" # name of the pre-existing mxd to add the shapefiles to

print 'set the workspace location...'
arcpy.env.workspace = os.getcwd()
fileroot = os.getcwd()

#if os.path.exists(os.path.join(os.getcwd(),"bad_river2.mxd")):
#	os.remove(os.path.join(os.getcwd(),"bad_river2.mxd"))

print 'open the mxd file'
mxd = arcpy.mapping.MapDocument(r"%s.mxd" %(base_mxd))
df = arcpy.mapping.ListDataFrames(mxd,"*")[0] # create a variable for the dataframe we want to use, which is simply the first (zeroth) item on the complete list of dataframes in the mxd

print 'Add all the layers---->'
infiles = open('arcfiles_' + rootname + '.dat','r').readlines() #opens a text file that contains all of the shp files to process

# iterate through all of the shp files listed in infiles to add them to the mxd
for line in infiles:	
	filename = os.path.join(os.getcwd(),line.strip()) # generates filename path from the current working dir and the working line in infiles
	
	#	
	#These clunky lines apply formatting from different lyr files based on the filename path generated above
	#
	if 'head' in filename:
		print 'adding %s' %(filename)
		newlayer = arcpy.mapping.Layer(filename) # Create a variable that will point Arc to the new layer
		arcpy.mapping.AddLayer(df, newlayer,"TOP") #Adds new layer to current dataframe, putting it at the top of the visible list
		arcpy.ApplySymbologyFromLayer_management(newlayer, 
		        os.path.join(os.getcwd(),'head_Wght_publish.lyr')) #Applies symbology to the new layer from a pre-configured lyr file
	elif 'obs_network' in filename:
		print 'adding %s' %(filename)
		newlayer = arcpy.mapping.Layer(filename) # Create a variable that will point Arc to the new layer
		arcpy.mapping.AddLayer(df, newlayer,"TOP") #Adds new layer to current dataframe, putting it at the top of the visible list
		arcpy.ApplySymbologyFromLayer_management(newlayer, 
	                os.path.join(os.getcwd(),'head_Wght_publish.lyr')) #Applies symbology to the new layer from a pre-configured lyr file	
	elif 'obs_wells' in filename:
		print 'adding %s' %(filename)
		newlayer = arcpy.mapping.Layer(filename) # Create a variable that will point Arc to the new layer
		arcpy.mapping.AddLayer(df, newlayer,"TOP") #Adds new layer to current dataframe, putting it at the top of the visible list
		arcpy.ApplySymbologyFromLayer_management(newlayer, 
	                os.path.join(os.getcwd(),'head_Wght_publish.lyr')) #Applies symbology to the new layer from a pre-configured lyr file	
	elif 'wcrs' in filename:
		print 'adding %s' %(filename)
		newlayer = arcpy.mapping.Layer(filename) # Create a variable that will point Arc to the new layer
		arcpy.mapping.AddLayer(df, newlayer,"TOP") #Adds new layer to current dataframe, putting it at the top of the visible list
		arcpy.ApplySymbologyFromLayer_management(newlayer, 
	                os.path.join(os.getcwd(),'head_Wght_publish.lyr')) #Applies symbology to the new layer from a pre-configured lyr file	
	elif 'lakes' in filename:
		print 'adding %s' %(filename)
		newlayer = arcpy.mapping.Layer(filename) # Create a variable that will point Arc to the new layer
		arcpy.mapping.AddLayer(df, newlayer,"TOP") #Adds new layer to current dataframe, putting it at the top of the visible list
		arcpy.ApplySymbologyFromLayer_management(newlayer, 
	                os.path.join(os.getcwd(),'head_Wght_publish.lyr')) #Applies symbology to the new layer from a pre-configured lyr file	
	elif 'streamflow' in filename:
		print 'adding %s' %(filename)
		newlayer = arcpy.mapping.Layer(filename)
		arcpy.mapping.AddLayer(df, newlayer,"TOP")				
		arcpy.ApplySymbologyFromLayer_management(newlayer, 
		        os.path.join(os.getcwd(),'Streamflow_Wght_publish.lyr'))
	elif 'gain' in filename:
		print 'adding %s' %(filename)
		newlayer = arcpy.mapping.Layer(filename)
		arcpy.mapping.AddLayer(df, newlayer,"TOP")				
		arcpy.ApplySymbologyFromLayer_management(newlayer, 
		        os.path.join(os.getcwd(),'FlowGain_Wght_publish.lyr'))					

print 'saving down a copy to ->\n%s' %(os.path.join(os.getcwd(),rootname + ".mxd"))
mxd.saveACopy(rootname + ".mxd") # saves new mxd using the specifed root name

# Refresh things (not sure if these lines are necessary if you are using ArcPy in script run outside of ArcMap)
arcpy.RefreshActiveView()
arcpy.RefreshTOC()

print "Files added ... done for now!"
