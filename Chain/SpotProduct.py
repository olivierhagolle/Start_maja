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
from datetime import datetime, timedelta
from Chain.Product import MajaProduct


class Spot5Muscate(MajaProduct):
    """
    A Spot 5 muscate product
    """
    def get_platform(self):
        return "spot5"

    def get_type(self):
        return "muscate"

    def get_level(self):
        return "l1c"

    def get_tile(self):
        import re
        site = self.base.split("_")[-3]
        tile = re.search(self.reg_tile, site)
        if tile:
            return tile.group()[1:]
        return site

    def get_metadata_file(self):
        return self.get_file(filename="*MTD_ALL.xml")

    def get_date(self):
        str_date = self.base.split("_")[1]
        # Datetime has troubles parsing milliseconds, so it's removed:
        str_date_no_ms = str_date[:str_date.rfind("-")]
        return datetime.strptime(str_date_no_ms, "%Y%m%d-%H%M%S")

    def is_valid(self):
        if os.path.exists(self.get_metadata_file()):
            return True
        return False

    def get_site(self):
        from Common import ImageIO
        from prepare_mnt.mnt.SiteInfo import Site
        try:
            band_bx = self.get_file(filename=r"*_B0?1*.tif")
        except IOError as e:
            raise e
        driver = ImageIO.open_tiff(band_bx)
        return Site.from_driver(self.get_tile(), driver)


class Spot4Muscate(MajaProduct):
    """
    A Spot 4 muscate product
    """
    def get_platform(self):
        return "spot4"

    def get_type(self):
        return "muscate"

    def get_level(self):
        return "l1c"

    def get_tile(self):
        import re
        site = self.base.split("_")[-3]
        tile = re.search(self.reg_tile, site)
        if tile:
            return tile.group()[1:]
        return site

    def get_metadata_file(self):
        return self.get_file(filename="*MTD_ALL.xml")

    def get_date(self):
        str_date = self.base.split("_")[1]
        # Datetime has troubles parsing milliseconds, so it's removed:
        str_date_no_ms = str_date[:str_date.rfind("-")]
        return datetime.strptime(str_date_no_ms, "%Y%m%d-%H%M%S")

    def is_valid(self):
        if os.path.exists(self.get_metadata_file()):
            return True
        return False

    def get_site(self):
        from Common import ImageIO
        from prepare_mnt.mnt.SiteInfo import Site
        try:
            band_bx = self.get_file(filename=r"*_B0?1*.tif")
        except IOError as e:
            raise e
        driver = ImageIO.open_tiff(band_bx)
        return Site.from_driver(self.get_tile(), driver)
