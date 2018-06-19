from osgeo import gdal, osr, gdalnumeric, gdal_array
import xarray as xr
import numpy as np
import georasters as gr

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
        #DataType = src_ds_sd.GetRasterBand(1).DataType
        #DataType = gdal.GetDataTypeName(DataType)

        # Close the subdataset
        src_ds_sd = None    

        # Close the whole dataset
        src_ds = None       

        # read data
        xr_ensemble = xr.open_dataset(in_filename)
        data = xr_ensemble[var_name]
        data = np.ma.masked_array(data, mask=data==NDV,fill_value=NDV) 
        
        return NDV, xsize, ysize, GeoT, Projection, data        
                  
# Function to write a new file.
def create_geotiff(Name, Array, NDV, xsize, ysize, GeoT, Projection, DataType):
    '''
    Creates new GeoTiff from array
    '''
    if type(DataType)!=np.int:
        if DataType.startswith('gdal.GDT_')==False:
            DataType=eval('gdal.GDT_'+DataType)
    
    NewFileName = Name+'.tif'
    zsize = Array.shape[0]
    # create a driver
    driver = gdal.GetDriverByName('GTiff')
    # Set nans to the original No Data Value
    Array[np.isnan(Array)] = NDV
    # Set up the dataset
    DataSet = driver.Create( NewFileName, xsize, ysize, zsize, DataType)
    # the '1' is for band 1.
    DataSet.SetGeoTransform(GeoT)
    DataSet.SetProjection( Projection.ExportToWkt() )
    # Write the array
    for i in xrange(0, zsize):
        DataSet.GetRasterBand(i+1).WriteArray( Array[i] )
        DataSet.GetRasterBand(i+1).SetNoDataValue(NDV)

    DataSet.FlushCache() 
    return NewFileName


if __name__ == "__main__":
    in_filename = 'F:\Private\Codesources\OpenSource\GitHub\Python\Medinageoportal\data_tools\mslp.mon.mean.nc'
    var_name = 'mslp'
    #in_filename = 'F:\uData\SeaIce\NSIDC\NSIDC_Data_6.25km_Native_NC\Sea_Ice_Concentrations_from_Nimbus-7_SMMR_and_DMSP_SSM_I-SSMIS_Passive_Microwave\NSIDC-0051_1115.reproj.nc'
    #var_name = 'Average_Sea_Ice_Concentration_with_Final_Version'
    NDV, xsize, ysize, GeoT, Projection, data = GetnetCDFInfobyName(in_filename, var_name)
    yy1 = data[1]
    """"
    DataType = gdal.GDT_Float32
    datax = gdalnumeric.LoadFile(in_filename)
    datax = datax.astype(np.float32)
    datax = datax + 109766;    
    datax = np.ma.masked_array(datax, mask=datax==NDV,fill_value=NDV) 
    
    xx1 = datax[1]
    xx  = gr.GeoRaster(xx1,GeoT, nodata_value=NDV, projection=Projection, datatype=DataType)        
    xx.to_tiff('gdal')       
        
    yy = gr.GeoRaster(yy1,GeoT, nodata_value=NDV, projection=Projection, datatype=DataType)        
    yy.to_tiff('xrray')  
    """
    DataType = gdal_array.NumericTypeCodeToGDALTypeCode(data.dtype)
    outfile = create_geotiff('selfinone', data, NDV, xsize, ysize, GeoT, Projection, DataType)

    
