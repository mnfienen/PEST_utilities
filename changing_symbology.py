import arcpy

arcpy.env.workspace = "D:/"
in_table = "D://test.dbf"
filename = r"D://miketest9.shp"


### Adding shapefile to the mxd at the top of the TOC
mxd = arcpy.mapping.MapDocument(r"D:/Penokee.mxd")
df = arcpy.mapping.ListDataFrames(mxd,"*")[0]
newlayer = arcpy.mapping.Layer(filename)
arcpy.mapping.AddLayer(df, newlayer,"TOP")

### adding symbology from a layerfile
arcpy.ApplySymbologyFromLayer_management(newlayer, r"D:/head_fair_under_br_kc_rei_4.csv Events.lyr")




mxd.saveACopy(r"D:\Project2.mxd")

# Refresh things
arcpy.RefreshActiveView()
arcpy.RefreshTOC()

del mxd, df, newlayer
print "Adding shapefile to mxd.... complete"

