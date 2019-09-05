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


class Site:
    """
    Stores all necessary information in order to create an MNT
    """
    def __init__(self, nom, epsg, ul, lr, res_x, res_y):
        self.nom = nom
        self.epsg = epsg
        self.res_x = res_x
        self.res_y = res_y
        self.ul = ul
        self.lr = lr
        self.ul_latlon, self.lr_latlon = self.get_latlon_minmax()

    def get_latlon_minmax(self):
        """
        Get lat and lon min and max values
        :return: latmin, latmax, lonmin, lonmax of the current sites
        """
        from Common import ImageIO
        ul_latlon = ImageIO.transform_point(self.ul, self.epsg, new_epsg=4326)
        lr_latlon = ImageIO.transform_point(self.lr, self.epsg, new_epsg=4326)
        return ul_latlon, lr_latlon

    @staticmethod
    def from_driver(name, driver):
        """
        Create site from driver.
        :param name: The name of the site
        :param driver: The gdal driver
        :return: A site class given the infos from the driver.
        """
        from Common import ImageIO
        epsg = ImageIO.get_epsg(driver)
        ul, lr = ImageIO.get_ul_lr(driver)
        resx, resy = ImageIO.get_resolution(driver)
        return Site(name, epsg, ul, lr, resx, resy)


class MNT(object):
    """
    Base class to get the necessary mnt for a given site.
    """

    def __init__(self, site, dem_dir):
        self.site = site
        self.dem_dir = dem_dir
        self.gsw_codes = self.get_gsw_codes(self.site)

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
        Download the given gsw_codes
        :param codes: The gsw codes of format 'XX(E/W)_YY(N/S)'
        :param dst: The destination folder
        :return: The list of filenames downloaded.
        """
        import os
        from Common import FileSystem
        url_base = "https://storage.googleapis.com/global-surface-water/downloads2/occurrence/occurrence_%s_v1_1.tif"
        filenames = []
        for code in codes:
            current_url = url_base % code
            filename = os.path.basename(current_url)
            filenames.append(filename)
            output_path = os.path.join(dst, filename)
            FileSystem.download_file(current_url, output_path)
        return filenames

    def get_water_data(self):
        raise NotImplementedError

    def prepare_mnt(self):
        raise NotImplementedError


if __name__ == "__main__":
    pass
