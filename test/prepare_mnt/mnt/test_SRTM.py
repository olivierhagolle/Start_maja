#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Copyright (C) CNES - All Rights Reserved
This file is subject to the terms and conditions defined in
file 'LICENSE.md', which is part of this source code package.

Author:         Peter KETTIG <peter.kettig@cnes.fr>
Project:        Start_maja, CNES
Created on:     Tue Dec  5 10:26:05 2018
"""

import unittest
from prepare_mnt.mnt import SRTM, MNTBase


class TestSRTM(unittest.TestCase):

    def test_get_srtm_codes_tls(self):
        resx, resy = 240, -240
        site = MNTBase.Site("T31TCJ", 32631,
                            px=400,
                            py=500,
                            ul=(300000.000, 4900020.000),
                            lr=(409800.000, 4790220.000),
                            res_x=resx,
                            res_y=resy)
        srtm_codes = SRTM.SRTM.get_srtm_codes(site)

        self.assertEqual(srtm_codes, ["srtm_37_04"])

    def test_get_srtm_codes_spain(self):
        resx, resy = 240, -240
        site = MNTBase.Site("T31TBE", 32631,
                            px=400,
                            py=500,
                            ul=(199980.000, 4500000.000),
                            lr=(309780.000, 4390200.000),
                            res_x=resx,
                            res_y=resy)

        srtm_codes = SRTM.SRTM.get_srtm_codes(site)

        self.assertEqual(srtm_codes, ['srtm_36_04', 'srtm_36_05', 'srtm_37_04', 'srtm_37_05'])

    def atest_get_raw_data(self):
        import os
        from Common import FileSystem
        resx, resy = 240, -240
        site = MNTBase.Site("T31TCJ", 32631,
                            px=400,
                            py=500,
                            ul=(300000.000, 4900020.000),
                            lr=(409800.000, 4790220.000),
                            res_x=resx,
                            res_y=resy)
        dem_dir = os.path.join(os.getcwd(), "srtm_dir")
        s = SRTM.SRTM(site, dem_dir)
        self.assertTrue(os.path.isdir(dem_dir))
        srtm_codes = SRTM.SRTM.get_srtm_codes(site)
        s.get_raw_data()
        for code in srtm_codes:
            filepath = os.path.join(s.wdir, code + ".zip")
            self.assertTrue(os.path.isfile(filepath))
        FileSystem.remove_directory(dem_dir)

    def test_srtm_prepare_mnt(self):
        import os
        from Common import FileSystem, ImageIO
        resx, resy = 10, -10
        site = MNTBase.Site("T31TCJ", 32631,
                            px=10980,
                            py=10980,
                            ul=(300000.000, 4900020.000),
                            lr=(409800.000, 4790220.000),
                            res_x=resx,
                            res_y=resy)
        dem_dir = os.path.join(os.getcwd(), "srtm_dir")
        s = SRTM.SRTM(site, dem_dir, wdir=dem_dir)
        self.assertTrue(os.path.isdir(dem_dir))
        srtm, gsw = s.prepare_mnt()
        self.assertTrue(os.path.isfile(srtm))
        self.assertTrue(os.path.isfile(gsw))
        img_read, drv = ImageIO.tiff_to_array(srtm, array_only=False)
        self.assertEqual(ImageIO.get_resolution(drv), (resx, resy))
        self.assertEqual(img_read.shape, (site.px, site.py))
        #FileSystem.remove_directory(dem_dir)


if __name__ == '__main__':
    unittest.main()
