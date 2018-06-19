# pyRaster2GeoTiff

A piece of Python code to convert rater data such as NetCDF to GeoTIFF format.
The code was extracted from my LinkedIn article at https://www.linkedin.com/pulse/convert-netcdf4-file-geotiff-using-python-chonghua-yin/.

In addition, it is better to try the code under a **virtual environment** as many Python packages could be imcompatible. It is quite easy to create a new virtual environment using the command of **conda**.

## Example data

You vsn download mean sea level pressure (mslp) from
http://www.esrl.noaa.gov/psd/data/gridded/data.ncep.reanalysis2.surface.html

## Comment

To be honest, **GDAL** is pretty unwieldy for most scientific data formats such as NetCDF or HDF5 files. It is because these data are commonly packed using **scalor** and **add_offset**. When reading a variable, have to take these into consideration. If you know other tools such as ncdump, you can try **ncdump -h infile.nc** to check the scalor and add_offset.

Under such a condition, you can read the variable using the following code:

from osgeo import gdalnumeric

datax = gdalnumeric.LoadFile(in_filename)

datax = datax.astype(np.float32)

datax = datax*scalor + add_offset

datax = np.ma.masked_array(datax, mask=datax==NDV,fill_value=NDV) 

outfile = create_geotiff(var_name, datax, NDV, xsize, ysize, GeoT, Projection)

In the above code, the Python package of **xarray** was used to unpack the named variable (Lines 30-32) and DataType was reset accordingly (Line 40). Actually, another package of **iris** can also unpack a NetCDF file. Using these two package, no need to know too much details.
