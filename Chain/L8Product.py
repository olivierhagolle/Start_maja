#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Copyright (C) CNES - All Rights Reserved
This file is subject to the terms and conditions defined in
file 'LICENSE.md', which is part of this source code package.

Author:         Peter KETTIG <peter.kettig@cnes.fr>
Project:        Start_maja, CNES
Created on:     Sun Feb  3 17:15:00 2019
"""

import re
from datetime import datetime, timedelta
from Chain.Product import MajaProduct


class Landsat8Natif(MajaProduct):
    """
    A Landsat-8 natif product
    """
    def get_platform(self):
        return "landsat8"

    def get_type(self):
        return "natif"

    def get_level(self):
        return "l1c"

    def get_tile(self):
        import re
        site = self.base.split("_")[4]
        tile = re.search(self.reg_tile, site)
        if tile:
            return tile.group()[1:]
        return site

    def get_metadata_file(self):
        metadata_filename = "*" + self.get_tile() + "*" + self.get_date().strftime("%Y%m%d") + "*HDR"
        return self.get_file(folders="..", filename=metadata_filename)

    def get_date(self):
        str_date = self.base.split(".")[0].split("_")[-1]
        # Add a timedelta of 12hrs in order to compensate for the missing H/M/S:
        return datetime.strptime(str_date, "%Y%m%d") + timedelta(hours=12)


class Landsat8Muscate(MajaProduct):
    """
    A Landsat-8 muscate product
    """
    def get_platform(self):
        return "landsat8"

    def get_type(self):
        return "muscate"

    def get_level(self):
        if self.base.find("_L1C_") >= 0:
            return "l1c"
        elif self.base.find("_L2A_") >= 0:
            return "l2a"
        raise ValueError("Unknown product level for %s" % self.base)

    def get_tile(self):
        tile = re.search(self.reg_tile, self.base)
        if tile:
            return tile.group()[1:]
        raise ValueError("Cannot determine tile ID: %s" % self.base)

    def get_metadata_file(self):
        return self.get_file(filename="*MTD_ALL.xml")

    def get_date(self):
        str_date = self.base.split("_")[1]
        # Datetime has troubles parsing milliseconds, so it's removed:
        str_date_no_ms = str_date[:str_date.rfind("-")]
        return datetime.strptime(str_date_no_ms, "%Y%m%d-%H%M%S")


class Landsat8LC1(MajaProduct):
    """
    A Landsat-8 ssc product
    """
    def get_platform(self):
        return "landsat8"

    def get_type(self):
        return "lc1"

    def get_level(self):
        return "l1c"

    def get_tile(self):
        return self.base[3:9]

    def get_metadata_file(self):
        return self.get_file(filename="*_MTL.txt")

    def get_date(self):
        year_doy = self.base[9:15]
        # Add a timedelta of 12hrs in order to compensate for the missing H/M/S:
        return datetime.strptime(year_doy, "%Y%j") + timedelta(hours=12)


class Landsat8LC2(MajaProduct):
    """
    A Landsat-8 ssc product
    """
    def get_platform(self):
        return "landsat8"

    def get_type(self):
        return "lc2"

    def get_level(self):
        return "l1c"

    def get_tile(self):
        return self.base.split("_")[2]

    def get_metadata_file(self):
        return self.get_file(filename="*_MTL.txt")

    def get_date(self):
        str_date = self.base.split("_")[3]
        # Add a timedelta of 12hrs in order to compensate for the missing H/M/S:
        return datetime.strptime(str_date, "%Y%m%d") + timedelta(hours=12)
