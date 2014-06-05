
# Script to plot PEST target residuals in ArcMap, with symbology according to size and type (head vs. stream)
# Inputs: 
# shp files containing the character string "rootname"
# a list of the shp files to process named 'arcfiles_rootname.dat'
# a pre-configured base mxd file
# pre-configured lyr files with symbology for stream and head residuals that are over and under

import sys
import xml.etree.ElementTree as ET
import arcpy
import os
import shutil

try:
    infile = sys.argv[1]
except:
    infile = 'Postproc_input_BRbase.XML'


rch_lyr='Rch.lyr'
contours_lyr = 'contours.lyr'
add_ascii_grids=True
recharge_id='rch' # string that identifies the recharge raster in the group of ascii grid files
k_fields_lyr='K_rasters.lyr'
plot_logK=True
plot_vertical_anisotropy=True
plot_vertical_head_differences=True
plot_vertical_head_gradients=False
plot_log_vertical_gradients=False
plot_heads=True
head_cont_interval = 20
vert_heads_lyr='vert_head_gradients.lyr'
plot_SFR = True


sfr_shpname = 'BadRiver_streamflow.shp' # include extension

try:
    inpardat = ET.parse(infile)
except:
    raise IOError("Cannot open {0}!".format(infile))

inpars = inpardat.getroot()


# input
pest_path = inpars.findall('.//path')[0].text
rootname = inpars.findall('.//rei_name')[0].text.replace('.', '_')
#rootname = reiname.replace('.', '_')
gis_folder = inpars.findall('.//GIS_folder')[0].text
base_mxd = inpars.findall('.//base_mxd')[0].text
prjfile = inpars.findall('.//PRJfile')[0].text

# Arc symbology layers
streams_lyr = inpars.findall('.//flux_residuals/lyr')[0].text
apply_streams_lyr_to = [k.text.lower() for k in inpars.findall('.//flux_residuals/keyword')]
heads_lyr = inpars.findall('.//head_residuals/lyr')[0].text
apply_heads_lyr_to = [k.text.lower() for k in inpars.findall('.//head_residuals/keyword')]
sfr_flow_lyr = inpars.findall('.//SFR_flow_symbology')[0].text
sfr_interactions_lyr = inpars.findall('.//SFR_interactions_symbology')[0].text
flooded_cells_lyr = inpars.findall('.//flooded_cells_symbology')[0].text
dry_cells_lyr = inpars.findall('.//dry_cells_symbology')[0].text

# Assign symbology to filenames using identifier strings from XML file
symbology = dict(zip(apply_streams_lyr_to, len(apply_streams_lyr_to)*[streams_lyr]))
symbology = dict(symbology.items() + dict(zip(apply_heads_lyr_to, len(apply_heads_lyr_to)*[heads_lyr])).items())

# functions
def add_feature(df, filename, symbology, TOCposition):
    # make a layer
    newlayer = arcpy.mapping.Layer(filename)
    print 'adding {0}'.format(filename)
    if symbology:
        # apply the symbology
        arcpy.ApplySymbologyFromLayer_management(newlayer, symbology)
    else:
        print "No symbology specified for {0}!".format(filename)
    # add new layer to current dataframe, at the top of the table of contents 
    arcpy.mapping.AddLayer(df, newlayer, "TOP")
        
def make_lograster(rastername,pest_path):
    # creates a log10 version of a raster
    lograster=arcpy.sa.Log10(pest_path+'\\'+rastername)
    lograstername='%slog_%s' %(rastername[0:3],rastername[3:])
    lograster.save(pest_path+'\\'+lograstername)
    lograster_layername="%s_log%s" %(rastername[0],rastername[1:])
    # return path to file instead of raster object
    return pest_path+'\\'+lograstername,lograster_layername
    
def add_raster(dataframe,raster,layername,path,symbology_layer):
    # add raster to a mxd file
    print 'adding {0}'.format(raster)
    # create pointer to raster layer objects
    # input to layer pointer needs to be path to raster, not raster object
    layer_pointer=arcpy.mapping.Layer(raster)
    # set symbology from a pre-existing lyr file
    arcpy.ApplySymbologyFromLayer_management(layer_pointer,symbology_layer)
    # add to mxd
    arcpy.mapping.AddLayer(dataframe,layer_pointer,"BOTTOM")


print 'set the workspace location...'
mxd_path = pest_path
pest_path=os.path.join(pest_path,gis_folder)
arcpy.env.workspace = pest_path
arcpy.env.overwriteOutput = True
arcpy.CheckOutExtension("Spatial")


print 'open the mxd file'
mxd = arcpy.mapping.MapDocument(r"%s" %(base_mxd))
df = arcpy.mapping.ListDataFrames(mxd,"*")[0] # create a variable for the dataframe we want to use, which is simply the first (zeroth) item on the complete list of dataframes in the mxd

# copy over lyr files to PEST folder
if pest_path<>os.getcwd():
    for cf in [heads_lyr,streams_lyr]:
        shutil.copyfile(cf,os.path.join(pest_path,os.path.split(cf)[-1]))



# plot dry cells
os.chdir(os.path.join(pest_path))
ascii_dry_files = [f for f in os.listdir(os.getcwd()) if 'dry' in f and '.asc' in f]
if len(ascii_dry_files )== 0:
    print "no ascii grids of dry cells found!"

for f in ascii_dry_files:
    print 'converting %s to raster...' %(f)
    rastername = f[:-4]
    arcpy.ASCIIToRaster_conversion(pest_path+'\\'+f, pest_path+'\\'+rastername, "FLOAT")
    arcpy.DefineProjection_management(pest_path+'\\'+rastername, prjfile)
    add_raster(df, pest_path+'\\'+rastername, rastername, pest_path, os.path.join(os.getcwd(), dry_cells_lyr))
        
# convert ascii grids (e.g. of K and R), and add them to the mxd also
# I think this could alternatively be done directly with the K-arrays using the numpy-array-to-raster command
if add_ascii_grids:
    os.chdir(os.path.join(pest_path))
    ascii_Kfiles=[f for f in os.listdir(os.getcwd()) if '_k' in f and '.asc' in f]
    
    # add recharge array
    arcpy.env.workspace = os.getcwd()
    rch_file=[f for f in os.listdir(os.getcwd()) if recharge_id in f and '.asc' in f][0]
    rastername=rch_file.split('.')[0][-4:]
    arcpy.ASCIIToRaster_conversion(pest_path+'\\'+rch_file,pest_path+'\\'+rastername,"FLOAT")
    arcpy.DefineProjection_management(pest_path+'\\'+rastername,prjfile)
    add_raster(df,pest_path+'\\'+rastername,rastername,pest_path,os.path.join(os.getcwd(),rch_lyr))
    
    # add K arrays
    if len(ascii_Kfiles)==0:
        print "no ascii grids of K found!"
    for f in ascii_Kfiles:
        print 'converting %s to raster...' %(f)
        arcpy.env.workspace = pest_path
        rastername="L"+f.split('.')[0][-4:]
        #convert ascii grid file to arc raster
        arcpy.ASCIIToRaster_conversion(pest_path+'\\'+f, pest_path+'\\'+rastername, "FLOAT")
        
        # define a projection for the raster
        # somehow this works here, at this point, and not in the arcpy window after the raster has been made
        arcpy.DefineProjection_management(pest_path+'\\'+rastername,prjfile)

        # need the path for raster below because it references a raster object
        add_raster(df,pest_path+'\\'+rastername,rastername,pest_path,os.path.join(os.getcwd(),k_fields_lyr))

        if plot_logK:

            lograster,lograster_layername=make_lograster(rastername,pest_path)
            add_raster(df,lograster,lograster_layername,pest_path,os.path.join(os.getcwd(),k_fields_lyr))
            
        if plot_vertical_anisotropy:
            if '_kz' in f:
                basename=f.split('_')[0]
                try:
                    kx_raster=[fi for fi in ascii_Kfiles if basename in fi and '_kx' in fi][0]
                    Kx_name="L"+kx_raster.split('.')[0][-4:]
                except:
                    print "no kx raster found for %s" %(rastername)
                    continue
                # Divide kz raster by kx raster; then follow same steps as above
                anisotropy_raster=arcpy.sa.Raster(pest_path+'\\'+rastername)/arcpy.sa.Raster(pest_path+'\\'+Kx_name)
                anisotropy_raster=arcpy.sa.Log10(anisotropy_raster)
                anisotropy_raster_path = os.path.join(pest_path,"%s_log_va" %(rastername[0:2]))
                anisotropy_raster.save(anisotropy_raster_path)
                
                add_raster(df,anisotropy_raster_path,"%s_log_va" %(rastername[0:2]),pest_path,os.path.join(os.getcwd(),k_fields_lyr))    

    # add vertical head differences/gradients
    if plot_vertical_head_differences:
        os.chdir(os.path.join(pest_path))
        ascii_hfiles=[f for f in os.listdir(os.getcwd()) if '_dh' in f and '.asc' in f]
        if len(ascii_hfiles)==0:
            print "no vertical head gradient ascii grids found!"
            
        for f in ascii_hfiles:
            print 'converting %s to raster...' %(f)
            arcpy.env.workspace = os.getcwd()
            if 'dhdz' in f:
                rastername="L%sto%s" %(f.split('.')[0][-7:][0],f.split('.')[0][-7:][1:])
            else:
                rastername="L%sto%s" %(f.split('.')[0][-5:][0],f.split('.')[0][-5:][1:])
            
            # convert,project,add to mxd
            arcpy.ASCIIToRaster_conversion(pest_path+'\\'+f,pest_path+'\\'+rastername,"FLOAT")
            arcpy.DefineProjection_management(pest_path+'\\'+rastername,prjfile)
            if plot_log_vertical_gradients:
                if 'dhdz' in f:
                    lograster,lograster_layername=make_lograster(rastername,pest_path)
                    add_raster(df,lograster,lograster_layername,pest_path,os.path.join(os.getcwd(),vert_heads_lyr))
                    continue
                    
            add_raster(df,pest_path+'\\'+rastername,rastername,pest_path,os.path.join(os.getcwd(),vert_heads_lyr))

# add water table and flooded cells
# convert to raster
rastername = 'watertabl'
arcpy.ASCIIToRaster_conversion(pest_path+'\\'+'water_table.asc',pest_path+'\\'+rastername,"FLOAT")
arcpy.DefineProjection_management(pest_path+'\\'+rastername,prjfile)
add_raster(df, pest_path+'\\'+rastername, 'water table', pest_path, os.path.join(os.getcwd(), k_fields_lyr))

# get max,min values
WTmin = float(arcpy.GetRasterProperties_management(pest_path+'\\'+rastername,"MINIMUM").getOutput(0))

# contour
base = WTmin + head_cont_interval - WTmin%head_cont_interval
arcpy.sa.Contour(pest_path+'\\'+rastername,pest_path+'\\'+"WTcontours.shp",head_cont_interval,base)
contours = arcpy.mapping.Layer(pest_path+'\\'+"WTcontours.shp")
arcpy.ApplySymbologyFromLayer_management(contours, os.path.join(os.getcwd(),contours_lyr))
arcpy.mapping.AddLayer(df, contours,"TOP")

# add flooded cells
rastername = 'flooded'
arcpy.ASCIIToRaster_conversion(pest_path+'\\'+'flooded_cells.asc', pest_path+'\\'+rastername, "FLOAT")
arcpy.DefineProjection_management(pest_path+'\\'+rastername, prjfile)
add_raster(df, pest_path+'\\'+rastername, 'water table', pest_path, os.path.join(os.getcwd(), flooded_cells_lyr))

# add SFR results
if plot_SFR:
    shpfile = os.path.join(pest_path, sfr_shpname)
    try:
        add_feature(df, shpfile, sfr_flow_lyr, "TOP")
        add_feature(df, shpfile, sfr_interactions_lyr, "Top")
    except ValueError:
        print "\nSkipping SFR, couldn't find SFR shapefile: {0}\n".format(shpfile)
            
os.chdir(pest_path)
print 'Add all the layers---->'
infiles = open('arcfiles_' + rootname + '.dat','r').readlines() #opens a text file that contains all of the shp files to process

# iterate through all of the shp files listed in infiles to add them to the mxd
for line in infiles:    
    filename = os.path.join(os.getcwd(),line.strip()) # generates filename path from the current working dir and the working line in infiles
    
    # assign layer file based on identifier string in filename
    lyr = None
    for identifier in symbology.keys():
        if identifier in line:
            lyr = symbology[identifier]
    try:
        add_feature(df, filename, lyr, "TOP")
    except ValueError:
        print 'skipping {0}, not a valid datasource for layer.'.format(filename)
        
# set all layers to be initially "off"
for lyr in arcpy.mapping.ListLayers(mxd):
    lyr.visible=False
    arcpy.RefreshTOC()


print 'saving down a copy to ->\n%s_%s.mxd' %(pest_path.split('\\')[-1],rootname)

mxd.saveACopy(os.path.join(mxd_path, '%s_%s.mxd' %(pest_path.split('\\')[-1],rootname))) # saves new mxd using the specifed root name
# Refresh things (not sure if these lines are necessary if you are using ArcPy in script run outside of ArcMap)
arcpy.RefreshActiveView()
arcpy.RefreshTOC()

print "Files added ... done for now!"
