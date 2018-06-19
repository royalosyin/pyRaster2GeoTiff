from osgeo import gdal, osr, gdal_array
import xarray as xr
import numpy as np

def GetnetCDFInfobyName(in_filename, var_name):
    """    
    Function to read the original file's projection    
    """
    # Open netCDF file
    src_ds = gdal.Open(in_filename) 
    if src_ds is None:
        print "Open failed"
        sys.exit()     
       
    if src_ds.GetSubDatasets() > 1:        
        # If exists more than one var in the NetCDF...        
        subdataset = 'NETCDF:"'+ in_filename + '":' + var_name
        src_ds_sd = gdal.Open(subdataset)
        # begin to read info of the named variable (i.e.,subdataset)
        NDV   = src_ds_sd.GetRasterBand(1).GetNoDataValue()
        xsize = src_ds_sd.RasterXSize
        ysize = src_ds_sd.RasterYSize
        GeoT  = src_ds_sd.GetGeoTransform()        
        Projection = osr.SpatialReference()
        Projection.ImportFromWkt(src_ds_sd.GetProjectionRef())     
        # Close the subdataset and the whole dataset
        src_ds_sd = None  
        src_ds    = None  
        # read data using xrray
        xr_ensemble = xr.open_dataset(in_filename)
        data = xr_ensemble[var_name]
        data = np.ma.masked_array(data, mask=data==NDV,fill_value=NDV) 
        
        return NDV, xsize, ysize, GeoT, Projection, data     

def create_geotiff(suffix, Array, NDV, xsize, ysize, GeoT, Projection):
    '''
    Creates new GeoTiff from array
    '''
    DataType = gdal_array.NumericTypeCodeToGDALTypeCode(Array.dtype)

    if type(DataType)!=np.int:
        if DataType.startswith('gdal.GDT_')==False:
            DataType=eval('gdal.GDT_'+DataType)
    
    NewFileName = suffix +'.tif'
    zsize       = Array.shape[0]
    
    # create a driver
    driver = gdal.GetDriverByName('GTiff')
    # Set nans to the original No Data Value
    Array[np.isnan(Array)] = NDV
    # Set up the dataset with zsize bands
    DataSet = driver.Create( NewFileName, xsize, ysize, zsize, DataType)   
    DataSet.SetGeoTransform(GeoT)
    DataSet.SetProjection( Projection.ExportToWkt() )
    # Write each slice of the array along the zsize
    for i in xrange(0, zsize):
        DataSet.GetRasterBand(i+1).WriteArray( Array[i] )
        DataSet.GetRasterBand(i+1).SetNoDataValue(NDV)

    DataSet.FlushCache() 
    return NewFileName

if __name__ == "__main__":
    infile   = 'mslp.mon.mean.nc'
    var_name = 'mslp'    
    NDV, xsize, ysize, GeoT, Projection, data = GetnetCDFInfobyName(infile, var_name)   
    outfile = create_geotiff(var_name, data, NDV, xsize, ysize, GeoT, Projection)

    #plot the first frame
    import rasterio
    import matplotlib.pyplot as plt
    src = rasterio.open(outfile)

    fig = plt.figure(figsize=(12,8))
    im =plt.imshow(src.read(1)/100.0, cmap='gist_rainbow')
    plt.title('Monthly mean sea level pressure (hPa) - Frame 1')

    from mpl_toolkits.axes_grid1 import make_axes_locatable
    divider = make_axes_locatable(plt.gca())
    cax = divider.append_axes("right", "5%", pad="3%")
    plt.colorbar(im, cax=cax)
    plt.tight_layout()
    plt.show()