#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Wed Nov 22 15:03:42 2017

@author: Peter Kettig
"""


def open_tiff(tiff_file):
    """
    @brief: Opens a tiff file
    @param tiff_file The filepath of the .tiff
    @return A Gdal format file
    """
    from osgeo import gdal
    import os
    if os.path.exists(tiff_file):
        return gdal.Open(tiff_file)
    else:
        raise NameError("GDAL could not open file {0}".format(tiff_file))


def tiff_to_array(tiff_file, lon_offset_px=0, lat_offset_px=0, array_only=True):
    """
    Transforms tiff file into an array.
    Note: Bands index starts at 1, not at 0
    :param tiff_file: The File path
    :param lon_offset_px: Offset for image in x-Direction
    :param lat_offset_px: Offset for image in y-Direction
    :param array_only: Numpy.array with shape (Bands,y-Index,x-Index)
    :return:
    """
    gdo = open_tiff(tiff_file)
    tiff_array = gdo.ReadAsArray(lon_offset_px, lat_offset_px)
    if array_only:
        gdo = None
    return tiff_array, gdo


def write_geotiff(img, dst, projection, coordinates, dtype=None):
    """
    Writes a GeoTiff file created from an existing coordinate-system
    :param img: The numpy array to write
    :param dst: The destination path
    :param projection: The gdal projection
    :param coordinates: The geotransform [Top-Left X, W-E Resolution, 0, Top Left Y, 0, N-S Resolution]
    :param dtype: The desired gdal dtype
    :return: Writes image to given path.
    """
    from osgeo import gdal, gdal_array
    import numpy as np
    driver = gdal.GetDriverByName('GTiff')
    # Add dimension for a single band-image
    if img.ndim is 2:
        img = img[..., np.newaxis]
    # Set output dtype if not specified. GDAL cannot write GTiff as binary files, so convert to uint8:
    if img.dtype == np.bool:
        dtype = gdal_array.NumericTypeCodeToGDALTypeCode(np.uint8)
    if not dtype:
        dtype = gdal_array.NumericTypeCodeToGDALTypeCode(img.dtype)
    dataset = driver.Create(dst, img.shape[1], img.shape[0], img.shape[2], dtype)
    if not dataset:
        raise OSError("GDAL Could not create file {0}".format(dst))
    if not coordinates or len(coordinates) != 6:
        raise ValueError("Geotransform empty or unknown: {0}".format(coordinates))
    dataset.SetGeoTransform(coordinates)  
    if not projection:
        raise ValueError("Projection empty or unknown: {0}".format(projection))
    dataset.SetProjection(projection)
    for index in range(img.shape[2]):
        dataset.GetRasterBand(index+1).WriteArray(img[:, :, index])
    dataset.FlushCache()  # Write to disk.


def write_geotiff_existing(img, dst, driver, dtype=None):
    """
    Create a GeoTiff image with an existing driver
    """
    geotransform = driver.GetGeoTransform()
    projection = driver.GetProjection()
    # Write the new array
    return write_geotiff(img, dst, projection, geotransform, dtype)


def get_epsg(driver):
    """
    Get the EPSG code from a given driver using gdal
    :param driver: The gdal driver
    :return: The EPSG code if existing.
    """
    from osgeo import gdal
    return int(gdal.Info(driver, format='json')['coordinateSystem']['wkt'].rsplit('"EPSG","', 1)[-1].split('"')[0])


def get_nodata_value(driver):
    """
    Get the NoDataValue (if existing) from a given driver using gdal
    :param driver: The gdal driver
    :return: The NoDataValue if existing. None if not.
    """
    from osgeo import gdal
    try:
        nodata = float(gdal.Info(driver, format='json')["bands"][0]["noDataValue"])
    except KeyError:
        nodata = None
    return nodata


def get_utm_description(driver):
    """
    Get the UTM Description of a given driver using gdal
    :param driver: The gdal driver
    :return: The UTM Description as string.
    """
    from osgeo import gdal
    return gdal.Info(driver, format='json')['coordinateSystem']['wkt'].rsplit('PROJCS["', 1)[-1].split('"')[0]


def get_ul_lr(driver):
    """
    Get the coordinates of the upper left and lower right as tuples
    :param driver: The gdal driver
    :return: The ul and lr- coordinates in the projected coordinate system.
    """
    ulx, xres, xskew, uly, yskew, yres = driver.GetGeoTransform()
    lrx = ulx + (driver.RasterXSize * xres)
    lry = uly + (driver.RasterYSize * yres)
    return (ulx, uly), (lrx, lry)


def get_resolution(driver):
    """
    Get the resolution of a given driver in x and y
    :param driver: The gdal driver
    :return: The x- and y-resolution in meters
    """
    _, xres, _, _, _, yres = driver.GetGeoTransform()
    return xres, yres


def transform_point(point, old_epsg, new_epsg=4326):
    """
    Transform a tuple (x,y) into lat lon using EPSG 4326
    :param point: The point as tuple (x,y)
    :param old_epsg: The EPSG code of the old coordinate system
    :param new_epsg: The EPSG code of the new coordinate system to transfer to. Default is 4326 (WGS84).
    :return: The point's location in the new epsg as (x, y) - z is omitted due to it being 0 most of the time
    """
    from osgeo import osr
    source = osr.SpatialReference()
    source.ImportFromEPSG(old_epsg)

    # The target projection
    target = osr.SpatialReference()
    target.ImportFromEPSG(new_epsg)
    transform = osr.CoordinateTransformation(source, target)
    new_pt = transform.TransformPoint(point[0], point[1])
    return new_pt[1], new_pt[0]


def gdal_buildvrt(vrtpath, *inputs, **options):
    """
    Build a gdalvrt using a subprocess.
    :param vrtpath: The path to build the vrt to.
    :param inputs: The list of inputs + other options if needed.
    :return: Builds vrt at the given path.
    """
    import os
    from Common import FileSystem
    if os.path.exists(vrtpath):
        FileSystem.remove_file(vrtpath)
    file_list = [vrtpath]
    options_list = []
    [options_list.extend(["-" + k, v])
     if type(v) is not bool else
     options_list.extend(["-" + k])
     for k, v in options.items()]
    # Append overwrite by default in order to avoid writing errors:
    options_list += ["-overwrite"]
    return FileSystem.run_external_app("gdalbuildvrt", file_list + list(inputs) + options_list)


def gdal_merge(dst, *src, **options):
    """
    Merge a set of gdal rasters
    :param src: The source filename
    :param dst: The destination filename
    :param options: Optional arguments such as 'init' or 'createonly'
    :return: A merged raster is written to the destination filename
    """
    import os
    from Common import FileSystem
    if os.path.exists(dst):
        FileSystem.remove_file(dst)
    file_list = ["-o", dst] + list(src)
    options_list = []
    [options_list.extend(["-" + k, v])
     if type(v) is not bool else
     options_list.extend(["-" + k])
     for k, v in options.items()]
    return FileSystem.run_external_app("gdal_merge.py", file_list + options_list)


def gdal_translate(dst, src, **options):
    """
    Merge a set of gdal rasters
    :param src: The source filename
    :param dst: The destination filename
    :param options: Optional arguments such as 'scale' or 'projwin'
    :return: A raster is written to the destination filename
    """
    import os
    from Common import FileSystem
    if os.path.exists(dst):
        FileSystem.remove_file(dst)
    file_list = [src, dst]
    options_list = []
    [options_list.extend(["-" + k, v])
     if type(v) is not bool else
     options_list.extend(["-" + k])
     for k, v in options.items()]
    return FileSystem.run_external_app("gdal_translate", options_list + file_list)


def gdal_warp(dst, src, **options):
    """
    Warp a set of gdal rasters
    :param src: The source filename
    :param dst: The destination filename
    :param options: Optional arguments such as 't_srs' or 'crop_to_cutline'
    :return: A raster is written to the destination filename
    """
    import os
    from Common import FileSystem
    if os.path.exists(dst):
        FileSystem.remove_file(dst)

    file_list = [src, dst]
    options_list = []
    [options_list.extend(["-" + k, v])
     if type(v) is not bool else
     options_list.extend(["-" + k])
     for k, v in options.items()]
    # Append overwrite by default in order to avoid writing errors:
    options_list += ["-overwrite"]
    return FileSystem.run_external_app("gdalwarp", options_list + file_list)


def gdal_calc(dst, calc, *src, **options):
    """
    Warp a set of gdal rasters
    :param src: The source filename
    :param calc: The expression to calculate
    :param dst: The destination filename
    :param options: Optional arguments such as 't_srs' or 'crop_to_cutline'
    :return: A raster is written to the destination filename
    """
    import os
    import string
    from Common import FileSystem
    if os.path.exists(dst):
        FileSystem.remove_file(dst)

    file_list = ["--outfile", dst] + ["-" + letter + " " + inp
                                      for inp, letter in zip(list(src), string.ascii_uppercase)]
    options_list = ["--calc='%s'" % calc, "--NoDataValue=0"]
    [options_list.extend(["-" + k, v])
     if type(v) is not bool else
     options_list.extend(["-" + k])
     for k, v in options.items()]

    # Append overwrite by default in order to avoid writing errors:
    options_list += ["--overwrite"]
    return FileSystem.run_external_app("gdal_calc.py", options_list + file_list)
