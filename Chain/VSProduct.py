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

from datetime import datetime, timedelta
from Chain.Product import MajaProduct


class VenusNatif(MajaProduct):
    """
    A Venus natif product
    """
    def get_platform(self):
        return "venus"

    def get_type(self):
        return "natif"

    def get_level(self):
        return "l1c"

    def get_tile(self):
        return self.base.split("_")[4]

    def get_metadata_file(self):
        metadata_filename = "*" + self.get_tile() + "*" + self.get_date().strftime("%Y%m%d") + "*HDR"
        return self.get_file(folders="../", filename=metadata_filename)

    def get_date(self):
        str_date = self.base.split(".")[0].split("_")[-1]
        return datetime.strptime(str_date, "%Y%m%d") + timedelta(hours=12)


class VenusMuscate(MajaProduct):
    """
    A Venus muscate product
    """
    def get_platform(self):
        return "venus"

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
        return self.base.split("_")[3]

    def get_metadata_file(self):
        return self.get_file(filename="*MTD_ALL.xml")

    def get_date(self):
        str_date = self.base.split("_")[1]
        # Datetime has troubles parsing milliseconds, so it's removed:
        str_date_no_ms = str_date[:str_date.rfind("-")]
        return datetime.strptime(str_date_no_ms, "%Y%m%d-%H%M%S")
