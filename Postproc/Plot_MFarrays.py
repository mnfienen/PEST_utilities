# Plot pilot point arrays
# If desired, can resave K-arrays as ascii files for easy import into ArcMap
# Can also consolidate K-arrays into single text file for easy import into Groundwater Vistas
import xml.etree.ElementTree as ET
import numpy as np
import matplotlib.pyplot as plt
import os
from matplotlib.backends.backend_pdf import PdfPages
import discomb_utilities
import sys
import mfpytools.binaryfile_recarray as bf

try:
    infile = sys.argv[1]
except:
    infile = 'Postproc_input.XML'



compile_K_for_GWV=True # consolidate K-arrays for easy import into Groundwater Vistas
plot_layer_transmissivities=True
unconf_layers=[1,2,3,4] # list of integers denoting unconfined layers (confined is default)
plot_log_T=True # plot log10 of transmissivity by layer; also plots dry cells

# ascii grid settings

create_ascii_grids=True
units_multiplier=0.3048 # e.g. if model units are ft. and GIS is m, 0.3048 (note: this is just for the ascii header)
NODATA_VALUE=-99999.000
export_vert_gradients=True # true to include arrays of vertical head gradients in ascii grid output
headsfile='BadRiver.hds'
export_water_table=True # also produces plot of flooded cells

try:
    inpardat = ET.parse(infile)
except:
    raise IOError("Cannot open {0}!".format(infile))

inpars = inpardat.getroot()

# input
path = inpars.findall('.//path')[0].text
MODFLOW_basename = inpars.findall('.//MODFLOW_basename')[0].text
gis_folder=inpars.findall('.//GIS_folder')[0].text # folder to save GIS output to
Rchfile = 'BadRiver.rch'
gridspecfile='BadRiver.spc'
disfile='BadRiver.dis'

outpdf_kp=os.path.join(path,'%s_Karrays.pdf' %(path))
outpdf_T=os.path.join(path,'%s_Tarrays.pdf' %(path))

# Functions

def readspc(gridspecfile):
    # read in grid spec file
    indata=open(gridspecfile).readlines()
    nrows,ncols=map(int,indata[0].strip().split())
    XLLCORNER,YLLCORNER=map(float,indata[1].strip().split())[0:2]
    CELLSIZE=map(float,indata[2].strip().split())[0]
    YLLCORNER=YLLCORNER-nrows*CELLSIZE
    return nrows,ncols,XLLCORNER,YLLCORNER,CELLSIZE

def read_rch(rchfile):
    indata=open(rchfile,'r').readlines()[:10]
    for line in indata:
        if 'OPEN/CLOSE' in line:
            rch_array = line.strip().split()[1].strip("'")
            rchmult = float(line.strip().split()[2])
            break
    return rch_array, rchmult
            
    
def kreader(infile):
    indat=[]
    infile_dat=open(infile,'r').readlines()
    for line in infile_dat:
        tmp=line.strip().split()
        indat.extend(tmp)
    indat=np.array(indat).astype(float)
    return indat

def save_image(pdf,array,zlabel,title,**kwargs):
    try:
        lim = kwargs['clim']
    except KeyError:
        lim = False

    fig=plt.figure()
    ax = fig.add_subplot(111)
    ax.set_axis_bgcolor('k')
    im=ax.imshow(array,interpolation='nearest')
    if lim:
        im.set_clim(lim)
    cb=fig.colorbar(im)
    cb.set_label(zlabel)
    ax.set_title(title)
    pdf.savefig(fig)
    
def np_multilayer_to_text(outmat,outfilename):
    # because it's numpy, have to iterate through slices of multi-layer array to save
    with file(outfilename, 'w') as outfile:
        for slice_2d in outmat:
            np.savetxt(outfile,slice_2d,fmt='%.4e')
        print "exporting %s for import into Groundwater Vistas" %(outfilename)

def save_ascii_grid(fname,array,path,gridspecfile,units_multiplier):
    fname=os.path.join(path,fname)
    nrows,ncols,XLLCORNER,YLLCORNER,CELLSIZE =  readspc(os.path.join(path,gridspecfile))
    ascii_header='NCOLS  %s\nNROWS  %s\nXLLCORNER  %s\nYLLCORNER  %s\nCELLSIZE  %s\nNODATA_VALUE  %s' %(ncols,
                                                                                                        nrows,
                                                                                                        XLLCORNER*units_multiplier,
                                                                                                        YLLCORNER*units_multiplier,
                                                                                                        CELLSIZE*units_multiplier,
                                                                                                        NODATA_VALUE)
    np.savetxt(fname, array, fmt='%.6e', delimiter=' ', header=ascii_header, comments='')
    print fname
    
def read_heads(path,headsfile):
    try:
        hds=bf.HeadFile(os.path.join(path,headsfile))
        heads = hds.get_data(kstp=1, kper=1)
    except:
        print "\nError: Cannot read binary head-save file! {0}".format(os.path.join(path,headsfile))
        quit()
    return heads
    
########### Main Program ######################################################

# read in model information from DIS and SPC files
DX,DY,nlay,nrows,ncols,i=discomb_utilities.read_meta_data(os.path.join(path,disfile))


# get layer tops/bottoms
layer_elevs=np.zeros((nlay+1,nrows,ncols))
for c in range(nlay+1):
    tmp,i=discomb_utilities.read_nrow_ncol_vals(os.path.join(path,disfile),nrows,ncols,'float',i)
    layer_elevs[c,:,:]=tmp

# get list of K files
Kfiles=[f for f in os.listdir(path) if '._k' in f]

# initialize output pdf for R and K arrays
pdf=PdfPages(outpdf_kp)
print '\nsaving plots to %s:' %(outpdf_kp)
print Rchfile,
for cf in sorted(Kfiles):
    print cf,
print "\n"

# first plot recharge
Recharge_array, rchmult = read_rch(os.path.join(path, Rchfile))
r=kreader(os.path.join(path,Recharge_array))
r=r.reshape((nrows,ncols))
r=r*12*365*rchmult
save_image(pdf,r,'in/yr','Recharge',clim=[0,20])


# write array to ascii file for subsequent import into Arc Map
# if an output folder for GIS files doesn't exist, make one

if not os.path.exists(os.path.join(path,gis_folder)):
    os.makedirs(os.path.join(path,gis_folder))
if create_ascii_grids:
    print 'exporting %s to ascii grid -->\t' %(cf),
    outfile=os.path.join(gis_folder,Recharge_array[:-4]+'.asc')
    save_ascii_grid(outfile,r,path,gridspecfile,units_multiplier)


# read in K for each layer and plot

counter=0
Kx_all,Kz_all=np.zeros((nlay,nrows,ncols)),np.zeros((nlay,nrows,ncols))
xcount,zcount=1,1
for cf in sorted(Kfiles):

    # read array and save to PDF
    K=kreader(os.path.join(path,cf))
    K=K.reshape((nrows,ncols))
    save_image(pdf,K,'ft/d','Layer %s' %(cf))
    
    # write array to ascii file for subsequent import into Arc Map
    if create_ascii_grids:
        print 'exporting %s to ascii grid -->\t' %(cf),
        outfile=os.path.join(gis_folder,cf.replace('.','')+'.asc')
        save_ascii_grid(outfile,K,path,gridspecfile,units_multiplier)
    
    # consolidate Kx and Kz arrays into single arrays for import into GWV
    if plot_layer_transmissivities or compile_K_for_GWV:
          
        layer_num=int([n for n in cf if n.isdigit()][0])

        # if no layers are missing, append current file to K-array
        if '._kx' in cf and xcount==layer_num:
                Kx_all[layer_num-1,:,:]=K
                xcount+=1

        elif '._kz' in cf and zcount==layer_num:
                Kz_all[layer_num-1,:,:]=K
                zcount+=1

        # otherwise, if a layer is missing, append the last layer again
        elif '._kx' in cf and xcount<layer_num:
                nmissing=layer_num-xcount
                for n in range(nmissing):
                    Kx_all[layer_num-(1+nmissing-n),:,:]=Kx_all[layer_num-(2+nmissing-n),:,:]
                Kx_all[layer_num-1,:,:]=K
                xcount+=nmissing+1

        elif '._kz' in cf and zcount<layer_num:
                for n in range(nmissing):
                    Kz_all[layer_num-(1+nmissing-n),:,:]=Kz_all[layer_num-(2+nmissing-n),:,:]
                Kz_all[layer_num-1,:,:]=K
                zcount+=nmissing+1

pdf.close()

outGWV=['Kx_all_layers.dat', 'Kz_all_layers.dat']
outmats=[Kx_all,Kz_all]

if compile_K_for_GWV:
    for i in range(2):
        np_multilayer_to_text(outmats[i],os.path.join(path,outGWV[i]))

if export_vert_gradients:
    print "\nSaving vertical head differences and gradients to ascii grids:"
    # read in heads
    heads = read_heads(path,headsfile)
    
    # calculate head differences and vert gradients
    vert_head_diffs=heads[:-1,:,:]-heads[1:,:,:]
    cell_midpoints=0.5*(layer_elevs[:-1]+layer_elevs[1:])
    elev_diffs=cell_midpoints[:-1]-cell_midpoints[1:]
    vert_gradients=vert_head_diffs/elev_diffs
    
    # include dry cells    
    bots=layer_elevs[1:,:,:]    
    drycells=np.where(heads[:-1,:,:]<bots[:-1,:,:])
    vert_head_diffs[drycells]=NODATA_VALUE
    vert_gradients[drycells]=NODATA_VALUE  
    
    for i in range(nlay-1):
        hdname=os.path.join(gis_folder,'%s%s%s_dh.asc' %(headsfile[:-4],i+1,i+2))
        save_ascii_grid(hdname,vert_head_diffs[i,:,:],path,gridspecfile,units_multiplier)
        
        vgname=os.path.join(gis_folder,'%s%s%s_dhdz.asc' %(headsfile[:-4],i+1,i+2))
        save_ascii_grid(vgname,vert_gradients[i,:,:],path,gridspecfile,units_multiplier)

if plot_layer_transmissivities:
    print "\nplotting layer transmissivities to %s..." %(outpdf_T)
    print "and exporting to ascii grids:"
    pdf=pdf=PdfPages(outpdf_T)
    # read in heads
    heads = read_heads(path,headsfile)
    
    # calculate layer transmissivities
    b=np.zeros(np.shape(heads))
    T=np.zeros(np.shape(heads))
    for i in range(nlay):
        top=layer_elevs[i,:,:]
        bot=layer_elevs[i+1,:,:]
        
        if i+1 in unconf_layers:
            wttops=np.where((heads[i,:,:]<top) & (heads[i,:,:]>bot))
            uctop=np.copy(top)
            lheads=heads[i,:,:]
            uctop[wttops]=lheads[wttops]
            
            b[i,:,:]=uctop-bot
        else:
            b[i,:,:]=top-bot
        
        # get indices for dry cells
        drycells=np.where(heads[i,:,:]<=bot)
        T=np.log10(b[i,:,:]*Kx_all[i,:,:])
        T[drycells] = NODATA_VALUE
        save_image(pdf,T,'Log Transmissivity, ft2/d','Layer %s' %(i+1))
        
        fname = os.path.join(gis_folder,'L%s_T.asc' %(i+1))
        save_ascii_grid(fname, T, path, gridspecfile, units_multiplier)

        # save dry cells as well
        active = np.zeros(np.shape(heads[0, :, :]))
        active[drycells] = 1
        fname=os.path.join(gis_folder, 'L%s_dry.asc' %(i+1))
        save_ascii_grid(fname, active, path, gridspecfile, units_multiplier)
    pdf.close()

if export_water_table:
    print "\nexporting water table and flooded cells..."
    heads = read_heads(path,headsfile)
    WT = watertable = heads[0,:,:]
    Flooded = WT - layer_elevs[0, :, :]
    Flooded[np.where(Flooded <= 0)] = NODATA_VALUE
    '''
    Flooded = flooded[flooded > 0]
    flooded = np.where(WT > layer_elevs[0, :, :])
    Flooded = np.zeros(np.shape(WT))
    Flooded[flooded] = 1
    '''
    if create_ascii_grids:
        outfile=os.path.join(gis_folder, 'water_table.asc')
        save_ascii_grid(outfile, WT, path, gridspecfile, units_multiplier)

        # save flooded cells as well
        outfile = os.path.join(gis_folder, 'flooded_cells.asc')
        save_ascii_grid(outfile, Flooded, path, gridspecfile, units_multiplier)
    
print '\nDone!'
