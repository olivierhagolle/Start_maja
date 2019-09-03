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


class SRTM(object):
    """
    Base class to get the necessary mnt for a given site.
    """

    def __init__(self, site, dem_dir):
        super(SRTM, self).__init__(site, dem_dir)
        if (self.site.ul[0]) > 60 or (self.site.lr[0] > 60):
            raise ValueError("Latitude over +-60deg - No SRTM data available!")

    def get_raw_data(self):
        """
        Get the DEM raw-data from a given directory. If not existing, an attempt will be made to download
        it automatically.
        :return:
        """
        raise NotImplementedError

    def prepare_mnt(self):
        raise NotImplementedError

    def get_srtm_codes(self):
        """
        Get the list of SRTM files for a given site.
        :return: The list of filenames needed in order to cover to whole site.
        """
        ul_latlon_srtm = [int(self.site.ul[0] + 180) / 5 + 1, int(60 - self.site.ul[1]) / 5 + 1]
        lr_latlon_srtm = [int(self.site.lr[0] + 180) / 5 + 1, int(60 - self.site.lr[1]) / 5 + 1]

        srtm_files = []
        for x in range(ul_latlon_srtm[0], lr_latlon_srtm[0] + 1):
            for y in range(ul_latlon_srtm[1], lr_latlon_srtm[1] + 1):
                srtm_files.append("srtm_%02d_%02d" % (x, y))
        return srtm_files


if __name__ == "__main__":
    pass
