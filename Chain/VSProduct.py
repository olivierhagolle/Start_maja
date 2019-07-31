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
        tile = re.search(self.reg_tile, self.base)
        if tile:
            return tile.group()[1:]
        raise ValueError("Cannot determine tile ID: %s" % self.base)

    def get_metadata_file(self):
        return self.get_file(filename="MTD_MSIL1C.xml")

    def get_date(self):
        str_date = self.base.split("_")[2]
        return datetime.strptime(str_date, "%Y%m%dT%H%M%S")


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
        elif self.base.find("_L3A_") >= 0:
            return "l3a"
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


class Landsat8SSC(MajaProduct):
    """
    A Landsat-8 ssc product
    """
    def get_platform(self):
        return "landsat8"

    def get_type(self):
        return "ssc"

    def get_level(self):
        if self.base.find("_L1VALD") >= 0:
            return "l1c"
        elif self.base.find("_L2VALD") >= 0:
            return "l2a"
        raise ValueError("Unknown product level for %s" % self.base)

    def get_tile(self):
        tile = re.search(self.reg_tile[1:], self.base)
        if tile:
            return tile.group()
        raise ValueError("Cannot determine tile ID: %s" % self.base)

    def get_metadata_file(self):
        return self.get_file(filename="TBD")

    def get_date(self):
        str_date = self.base.split(".")[0].split("_")[-1]
        # Add a timedelta of 12hrs in order to compensate for the missing H/M/S:
        return datetime.strptime(str_date, "%Y%m%d") + timedelta(hours=12)
