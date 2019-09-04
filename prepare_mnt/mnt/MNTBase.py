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
        :return: The list of filenames needed in order to cover to whole site.
        """
        import math
        num_x = [math.ceil(math.fabs(site.ul_latlon[0]) / 10) * 10, math.ceil(math.fabs(site.ul_latlon[1]) / 10) * 10]
        if site.ul_latlon[0] > 0:
            code_x1 = "N"
        else:
            code_x1 = "S"
        if site.ul_latlon[1] < 0:
            code_x2 = "W"
        else:
            code_x2 = "E"
            num_x[1] -= 10

        num_y = [math.ceil(math.fabs(site.lr_latlon[0]) / 10) * 10, math.ceil(math.fabs(site.lr_latlon[1]) / 10) * 10]
        if site.lr_latlon[0] > 0:
            code_y1 = "N"
        else:
            code_y1 = "S"
        if site.lr_latlon[1] < 0:
            code_y2 = "W"
        else:
            code_y2 = "E"
            num_y[1] -= 10
        return num_x, code_x1, code_x2, num_y, code_y1, code_y2

    def get_water_data(self):
        raise NotImplementedError

    def prepare_mnt(self):
        raise NotImplementedError


if __name__ == "__main__":
    pass
