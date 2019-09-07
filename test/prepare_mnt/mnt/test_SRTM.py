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
        s = SRTM.SRTM(site, dem_dir, raw_dem=dem_dir, raw_gsw=dem_dir)
        self.assertTrue(os.path.isdir(dem_dir))
        srtm_codes = SRTM.SRTM.get_srtm_codes(site)
        s.get_raw_data()
        for code in srtm_codes:
            filepath = os.path.join(s.wdir, code + ".zip")
            self.assertTrue(os.path.isfile(filepath))
        FileSystem.remove_directory(dem_dir)

    def atest_srtm_prepare_mnt_s2_tls(self):
        import os
        import numpy as np
        from Common import FileSystem, ImageIO
        resx, resy = 10000, -10000
        site = MNTBase.Site("T31TCJ", 32631,
                            px=11,
                            py=11,
                            ul=(300000.000, 4900020.000),
                            lr=(409800.000, 4790220.000),
                            res_x=resx,
                            res_y=resy)
        dem_dir = os.path.join(os.getcwd(), "test_srtm_prepare_mnt_s2_tls")
        s = SRTM.SRTM(site, dem_dir, raw_dem=dem_dir, raw_gsw=dem_dir, wdir=dem_dir)
        self.assertTrue(os.path.isdir(dem_dir))
        srtm = s.prepare_mnt()
        self.assertTrue(os.path.isfile(srtm))
        img_read, drv = ImageIO.tiff_to_array(srtm, array_only=False)
        expected_img = [[85, 85, 115, 142, 138, 147, 151, 163, 162, 258, 282],
                        [136, 98, 96, 90, 101, 91, 120, 118, 121, 243, 302],
                        [137, 133, 135, 137, 101, 89, 92, 131, 162, 246, 294],
                        [139, 144, 170, 184, 157, 115, 108, 132, 176, 210, 212],
                        [148, 140, 161, 162, 206, 138, 133, 134, 150, 164, 160],
                        [169, 173, 168, 171, 222, 168, 128, 158, 162, 151, 164],
                        [193, 199, 181, 186, 186, 193, 158, 147, 189, 204, 199],
                        [209, 223, 207, 195, 215, 215, 166, 161, 187, 214, 228],
                        [240, 247, 225, 206, 268, 211, 172, 203, 195, 213, 242],
                        [281, 268, 246, 272, 282, 216, 216, 208, 231, 211, 220],
                        [335, 302, 319, 311, 265, 234, 262, 251, 236, 259, 250]]
        self.assertEqual(ImageIO.get_resolution(drv), (resx, resy))
        self.assertEqual(img_read.shape, (site.py, site.px))
        np.testing.assert_equal(expected_img, img_read)
        FileSystem.remove_directory(dem_dir)

    def test_srtm_prepare_mnt_vns_maccanw2(self):
        import os
        import numpy as np
        from Common import FileSystem, ImageIO
        resx, resy = 5000, -5000
        px, py = 11, 14
        site = MNTBase.Site("MACCANW2", 32633,
                            px=px,
                            py=py,
                            ul=(246439.500, 4672656.500),
                            lr=(299769.500, 4604231.500),
                            res_x=resx,
                            res_y=resy)
        dem_dir = os.path.join(os.getcwd(), "test_srtm_prepare_mnt_vns_maccanw2")
        s = SRTM.SRTM(site, dem_dir, raw_dem=dem_dir, raw_gsw=dem_dir, wdir=dem_dir)
        self.assertTrue(os.path.isdir(dem_dir))
        srtm = s.prepare_mnt()
        self.assertTrue(os.path.isfile(srtm))
        img_read, drv = ImageIO.tiff_to_array(srtm, array_only=False)
        expected_img = [[293, 210, 337, 390, 238, 218, 237, 245, 270, 208, 132]
                        , [303, 293, 277, 302, 182, 172, 237, 270, 262, 171, 60]
                        , [156, 242, 239, 231, 238, 199, 164, 173, 137, 85, 33]
                        , [4,  27,  96, 138, 150, 131, 116, 117, 72, 37, 73]
                        , [-2, -1, 17, 69, 82, 79, 84, 117, 72, 36, 59]
                        , [-1, -1, 1, 9, 38, 58, 68, 87, 68, 38, 33]
                        , [-1, -1, -1, -1, 5, 42, 52, 62, 52, 43, 41]
                        , [-1, -1, -1, -1, 1, 11, 29, 34, 30, 48, 68]
                        , [-1, -1, -1, -1, 1, -1, 12, 26, 42, 70, 101]
                        , [-1, -1, -1, -1, -1, 3, 11, 51, 58, 89, 136]
                        , [-1, -1, -1, -1, -1, 1, 4, 30, 77, 97, 130]
                        , [-1, -1, -1, -1, -1, -1, -1, 4, 44, 73, 86]
                        , [-1, -1, -1, -1, -1, -1, -1, -1, 4, 28, 60]
                        , [-1, -1, -1, -1, -1, -1, -1, -1, -2, 12, 56]]

        self.assertEqual(ImageIO.get_resolution(drv), (resx, resy))
        self.assertEqual(img_read.shape, (site.py, site.px))
        np.testing.assert_equal(expected_img, img_read)
        FileSystem.remove_directory(dem_dir)


if __name__ == '__main__':
    unittest.main()
