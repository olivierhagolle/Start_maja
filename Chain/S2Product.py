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

import os
import re
from datetime import datetime, timedelta
from Chain.Product import MajaProduct


class Sentinel2Natif(MajaProduct):
    """
    A Sentinel-2 natif product
    """
    def get_platform(self):
        return "sentinel2"

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

    def is_valid(self):
        if os.path.exists(self.get_metadata_file()):
            return True
        return False

    def get_site(self):
        from Common import ImageIO
        from prepare_mnt.mnt.MNTBase import Site
        try:
            band_b2 = self.get_file(filename=r"*B0?2*.tif")
        except IOError as e:
            raise e
        driver = ImageIO.open_tiff(band_b2)
        return Site.from_driver(self.get_tile(), driver)


class Sentinel2Muscate(MajaProduct):
    """
    A Sentinel-2 muscate product
    """
    def get_platform(self):
        return "sentinel2"

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

    def is_valid(self):
        from Common import FileSystem
        if self.get_level() == "l1c" and os.path.exists(self.get_metadata_file()):
            return True
        if self.get_level() == "l2a":
            try:
                jpi = FileSystem.find_single("*JPI_ALL.xml", self.fpath)
            except ValueError:
                return False
            validity_xpath = "./Processing_Flags_And_Modes_List/Processing_Flags_And_Modes/Value"
            processing_flags = FileSystem.get_xpath(jpi, validity_xpath)
            validity_flags = [flg.text for flg in processing_flags]
            if "L2VALD" in validity_flags:
                return True
        return False

    def get_site(self):
        from Common import ImageIO
        from prepare_mnt.mnt.MNTBase import Site
        try:
            band_b2 = self.get_file(filename=r"*B0?2*.tif")
        except IOError as e:
            raise e
        driver = ImageIO.open_tiff(band_b2)
        return Site.from_driver(self.get_tile(), driver)


class Sentinel2SSC(MajaProduct):
    """
    A Sentinel-2 ssc product
    """
    def get_platform(self):
        return "sentinel2"

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
        metadata_filename = "*" + self.get_tile() + "*" + self.get_date().strftime("%Y%m%d") + "*HDR"
        return self.get_file(folders="../", filename=metadata_filename)

    def get_date(self):
        str_date = self.base.split(".")[0].split("_")[-1]
        # Add a timedelta of 12hrs in order to compensate for the missing H/M/S:
        return datetime.strptime(str_date, "%Y%m%d") + timedelta(hours=12)

    def is_valid(self):
        if os.path.exists(self.get_metadata_file()):
            return True
        return False

    def get_site(self):
        from Common import ImageIO
        from prepare_mnt.mnt.MNTBase import Site
        try:
            band_r1 = self.get_file(filename=r"*R1*.DBL.TIF")
        except IOError as e:
            raise e
        driver = ImageIO.open_tiff(band_r1)
        return Site.from_driver(self.get_tile(), driver)
