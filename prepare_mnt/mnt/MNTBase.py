#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Copyright (C) CNES - All Rights Reserved
This file is subject to the terms and conditions defined in
file 'LICENSE.md', which is part of this source code package.

Author:         Peter KETTIG <peter.kettig@cnes.fr>, Pierre LASSALLE <pierre.lassalle@cnes.fr>
Project:        StartMaja, CNES
Created on:     Tue Sep 11 15:31:00 2018
"""

surface_water_url = "https://storage.googleapis.com/global-surface-water/downloads2/occurrence/occurrence_%s_v1_1.tif"


class Site:
    """
    Stores all necessary information in order to create an MNT
    """
    def __init__(self, nom, epsg, px, py, ul, lr, res_x, res_y):
        self.nom = nom
        self.epsg = epsg
        self.px = px
        self.py = py
        self.res_x = res_x
        self.res_y = res_y
        self.ul = ul
        self.lr = lr
        self.ul_latlon, self.lr_latlon = self.latlon_minmax

    @property
    def latlon_minmax(self):
        """
        Get lat and lon min and max values
        :return: latmin, latmax, lonmin, lonmax of the current sites
        """
        from Common import ImageIO
        ul_latlon = ImageIO.transform_point(self.ul, self.epsg, new_epsg=4326)
        lr_latlon = ImageIO.transform_point(self.lr, self.epsg, new_epsg=4326)
        return ul_latlon, lr_latlon

    @property
    def projwin(self):
        return " ".join([str(self.ul[1]), str(self.ul[0]), str(self.lr[1]), str(self.lr[0])])

    @property
    def te_str(self):
        x_val = list(sorted([self.lr[1], self.ul[1]]))
        y_val = list(sorted([self.lr[0], self.ul[0]]))
        return " ".join([str(x_val[0]), str(y_val[0]), str(x_val[1]), str(y_val[1])])

    @property
    def epsg_str(self):
        return "EPSG:" + str(self.epsg)

    @property
    def tr_str(self):
        return str(self.res_x) + " " + str(self.res_y)

    def to_driver(self, path, n_bands=1):
        from osgeo import osr, gdal
        # create the raster file
        dst_ds = gdal.GetDriverByName('GTiff').Create(path, self.py, self.px, n_bands, gdal.GDT_Byte)
        geotransform = (self.ul[1], self.res_x, 0, self.ul[0], 0, self.res_y)
        dst_ds.SetGeoTransform(geotransform)  # specify coords
        srs = osr.SpatialReference()  # establish encoding
        srs.ImportFromEPSG(self.epsg)  # WGS84 lat/long
        dst_ds.SetProjection(srs.ExportToWkt())  # export coords to file
        return dst_ds

    @staticmethod
    def from_raster(name, raster):
        """
        Create site from a raster on disk
        :param name: The name of the site
        :param raster: The gdal raster
        :return: A site class given the infos from the raster.
        """
        from Common import ImageIO
        raster, driver = ImageIO.tiff_to_array(raster, array_only=False)
        nx, ny = raster.shape[:2]
        epsg = ImageIO.get_epsg(driver)
        ul, lr = ImageIO.get_ul_lr(driver)
        xmin, xres, skx, ymax, sky, yres = driver.GetGeoTransform()
        return Site(name, epsg, nx, ny, ul, lr, xres, yres)


class MNT(object):
    """
    Base class to get the necessary mnt for a given site.
    """

    def __init__(self, site, dem_dir, wdir=None):
        import os
        import tempfile
        from Common import FileSystem
        self.site = site
        self.dem_dir = dem_dir
        if not os.path.isdir(self.dem_dir):
            FileSystem.create_directory(self.dem_dir)
        self.gsw_codes = self.get_gsw_codes(self.site)
        if not wdir:
            self.wdir = tempfile.mkdtemp()
        else:
            assert os.path.isdir(wdir)
            self.wdir = wdir

    def get_raw_data(self):
        """
        Get the DEM raw-data from a given directory. If not existing, an attempt will be made to download
        it automatically.
        :return:
        """
        raise NotImplementedError

    @staticmethod
    def get_gsw_codes(site):
        """
        Get the list of GSW files for a given site.
        :param site: The site class
        :return: The list of filenames of format 'XX(E/W)_YY(N/S)' needed in order to cover to whole site.
        """
        import math
        from collections import namedtuple
        if site.ul_latlon[1] > 170 and site.lr_latlon[1] < 160:
            raise ValueError("Cannot wrap around longitude change")

        grid_step = 10
        point = namedtuple("point", ("y", "x"))
        pts = []
        for pt in [site.ul_latlon, site.lr_latlon]:
            lat_dec = (math.fabs(pt[0]) / grid_step)
            lon_dec = (math.fabs(pt[1]) / grid_step)
            if pt[0] > 0:
                lat_id = int(math.ceil(lat_dec) * grid_step)
            else:
                lat_id = -1 * int(math.floor(lat_dec) * grid_step)

            if pt[1] < 0:
                lon_id = int(math.ceil(lon_dec) * grid_step)
            else:
                lon_id = -1 * int(math.floor(lon_dec) * grid_step)
            pts.append(point(lat_id, lon_id))
        gsw_granules = []
        for x in range(pts[1].x, pts[0].x + grid_step, grid_step):
            for y in range(pts[1].y, pts[0].y + grid_step, grid_step):
                code_lat = "S" if y < 0 else "N"
                code_lon = "W" if x > 0 else "E"
                gsw_granules.append("%s%s_%s%s" % (int(math.fabs(x)), code_lon, int(math.fabs(y)), code_lat))
        return gsw_granules

    @staticmethod
    def download_gsw(codes, dst):
        """
        Download the given gsw codes
        :param codes: The gsw codes of format 'XX(E/W)_YY(N/S)'
        :param dst: The destination folder
        :return: The list of filenames downloaded.
        """
        import os
        from Common import FileSystem
        import logging
        filenames = []
        for code in codes:
            # Download files one by one:
            current_url = surface_water_url % code
            filename = os.path.basename(current_url)
            filenames.append(filename)
            output_path = os.path.join(dst, filename)
            FileSystem.download_file(current_url, output_path, log_level=logging.INFO)
        return filenames

    def get_water_data(self, dst, gsw_files, threshold=100):
        """
        Prepare the water mask constituing of a set of gsw files.
        :param gsw_files: The list of gsw filenames
        :param threshold: The threshold that should be applied.
        :return:
        """
        import os
        from Common import ImageIO
        # Combine VRT of all gsw files:
        vrt_path = os.path.join(self.wdir, "occurrence.vrt")
        water_mask = os.path.join(self.wdir, "water_mask.tif")
        ImageIO.gdal_buildvrt(vrt_path, *gsw_files,
                              q=True)
        # Overlay occurrence image with same extent as the given site.
        # Should the occurrence files not be complete, this sets all areas not covered by the occurrence to 0.
        ImageIO.gdal_warp(vrt_path, water_mask,
                          te=self.site.te_str,
                          te_srs=self.site.epsg_str,
                          t_srs=self.site.epsg_str,
                          tr=self.site.tr_str,
                          dstnodata="0",
                          q=True)
        # Threshold the final image and write to destination:
        image, drv = ImageIO.tiff_to_array(water_mask, array_only=False)
        image_bin = image > threshold
        ImageIO.write_geotiff_existing(image_bin, dst, drv)

    def prepare_mnt(self):
        raise NotImplementedError


if __name__ == "__main__":
    pass
