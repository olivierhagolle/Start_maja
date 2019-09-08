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
import os
from prepare_mnt.mnt import MNTBase


class TestMNTBase(unittest.TestCase):

    def test_gsw_codes_toulouse(self):
        site = MNTBase.Site("T31TCJ", 32631,
                            px=400,
                            py=500,
                            ul=(300000.000, 4900020.000),
                            lr=(409800.000, 4790220.000),
                            res_x=10,
                            res_y=-10)

        gsw_codes = MNTBase.MNT.get_gsw_codes(site)
        self.assertEqual(gsw_codes, ['0E_50N'])

    def test_gsw_codes_spain(self):
        site = MNTBase.Site("T31TBE", 32631,
                            px=400,
                            py=500,
                            ul=(199980.000, 4500000.000),
                            lr=(309780.000, 4390200.000),
                            res_x=10,
                            res_y=-10)

        gsw_codes = MNTBase.MNT.get_gsw_codes(site)
        self.assertEqual(gsw_codes, ['0E_40N', '0E_50N', '10W_40N', '10W_50N'])

    def test_gsw_codes_zero_center(self):
        site = MNTBase.Site("Somewhere_over_the_ocean", 32631,
                            px=400,
                            py=500,
                            ul=(-250000.000, 250000.000),
                            lr=(250000.000, -120000.000),
                            res_x=10,
                            res_y=-10)

        gsw_codes = MNTBase.MNT.get_gsw_codes(site)
        self.assertEqual(gsw_codes, ['0E_0N', '0E_10N', '10W_0N', '10W_10N'])

    def test_gsw_codes_south_america(self):
        site = MNTBase.Site("Ecuador", 32619,
                            px=400,
                            py=500,
                            ul=(-250000.000, 250000.000),
                            lr=(400000.000, -120000.000),
                            res_x=10,
                            res_y=-10)

        gsw_codes = MNTBase.MNT.get_gsw_codes(site)
        self.assertEqual(gsw_codes, ['70W_0N', '70W_10N', '80W_0N', '80W_10N'])

    def test_gsw_codes_longitude_change(self):
        site = MNTBase.Site("Russia", 32601,
                            px=400,
                            py=500,
                            ul=(-250000.000, 250000.000),
                            lr=(400000.000, -120000.000),
                            res_x=10,
                            res_y=-10)
        # TODO Support this:
        with self.assertRaises(ValueError):
            MNTBase.MNT.get_gsw_codes(site)

    def test_gsw_download(self):
        from Common import FileSystem
        site = MNTBase.Site("Ecuador", 32619,
                            px=400,
                            py=500,
                            ul=(-250000.000, 250000.000),
                            lr=(400000.000, -120000.000),
                            res_x=10,
                            res_y=-10)
        gsw_dir = os.path.join(os.getcwd(), "test_gsw_download")
        m = MNTBase.MNT(site, gsw_dir, raw_gsw=gsw_dir, raw_dem=gsw_dir)
        fnames = m.get_raw_water_data()
        self.assertEqual(len(fnames), 1)
        for fn in fnames:
            self.assertTrue(os.path.exists(fn))
            self.assertEqual(os.path.basename(fn), "occurrence_10E_50N_v1_1.tif")
        FileSystem.remove_directory(gsw_dir)
        self.assertFalse(os.path.exists(gsw_dir))

    def test_get_water_data_tls_s2(self):
        """
        Download the given gsw file and project it to a 10km x 10km resolution (11x11 image)
        """
        import numpy as np
        from Common import ImageIO, FileSystem
        resx, resy = 10000, -10000
        px, py = 11, 11
        site = MNTBase.Site("T31TCJ", 32631,
                            px=px,
                            py=py,
                            ul=(300000.000, 4900020.000),
                            lr=(409800.000, 4790220.000),
                            res_x=resx,
                            res_y=resy)
        dem_dir = os.path.join(os.getcwd(), "test_get_water_data_tls_s2")
        water_mask = os.path.join(dem_dir, "water_mask.tif")
        mnt = MNTBase.MNT(site, dem_dir, raw_dem=dem_dir, raw_gsw=dem_dir)
        self.assertTrue(os.path.exists(dem_dir))
        mnt.prepare_water_data(water_mask)
        self.assertTrue(os.path.exists(water_mask))
        img_read, drv = ImageIO.tiff_to_array(water_mask, array_only=False)
        img_expected = [[0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
                        , [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
                        , [0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0]
                        , [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
                        , [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
                        , [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
                        , [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
                        , [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
                        , [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
                        , [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
                        , [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]]
        # Note the the part of the image which is not covered by the unittest.
        # This is where the border is ascending:
        self.assertEqual(ImageIO.get_resolution(drv), (resx, resy))
        self.assertEqual(ImageIO.get_epsg(drv), 32631)
        self.assertEqual(img_read.shape, (py, py))
        np.testing.assert_almost_equal(img_expected, img_read)
        FileSystem.remove_file(water_mask)
        FileSystem.remove_directory(dem_dir)

    def test_get_water_data_spain_s2(self):
        """
        Download the given gsw file and project it to a 10km x 10km resolution (11x11 image)
        """
        import numpy as np
        from Common import ImageIO, FileSystem
        resx, resy = 10000, -10000
        px, py = 11, 11
        site = MNTBase.Site("T30TYK", 32630,
                            px=px,
                            py=py,
                            ul=(699960.000, 4500000.000),
                            lr=(809760.000, 4390200.000),
                            res_x=resx,
                            res_y=resy)
        dem_dir = os.path.join(os.getcwd(), "test_get_water_data_spain_s2")
        water_mask = os.path.join(dem_dir, "water_mask.tif")
        mnt = MNTBase.MNT(site, dem_dir, raw_dem=dem_dir, raw_gsw=dem_dir)
        self.assertTrue(os.path.exists(dem_dir))
        mnt.prepare_water_data(water_mask)
        self.assertTrue(os.path.exists(water_mask))
        img_read, drv = ImageIO.tiff_to_array(water_mask, array_only=False)
        img_expected = [[0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1]
                        , [0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1]
                        , [0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1]
                        , [0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1]
                        , [0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1]
                        , [0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 1]
                        , [0, 0, 0, 0, 0, 0, 1, 1, 1, 1, 1]
                        , [0, 0, 0, 0, 0, 0, 1, 1, 1, 1, 1]
                        , [0, 0, 0, 0, 0, 1, 1, 1, 1, 1, 1]
                        , [0, 0, 0, 0, 1, 1, 1, 1, 1, 1, 1]
                        , [0, 0, 0, 0, 1, 1, 1, 1, 1, 1, 1]]

        # Note the the part of the image which is not covered by the unittest.
        # This is where the border is ascending:
        self.assertEqual(ImageIO.get_resolution(drv), (resx, resy))
        self.assertEqual(ImageIO.get_epsg(drv), 32630)
        self.assertEqual(img_read.shape, (py, px))
        np.testing.assert_almost_equal(img_expected, img_read)
        FileSystem.remove_directory(dem_dir)

    def test_get_water_data_maccanw2_vns(self):
        import numpy as np
        from Common import ImageIO, FileSystem
        resx, resy = 5000, -5000
        px, py = 11, 14
        site = MNTBase.Site("MACCANW2", 32633,
                            px=px,
                            py=py,
                            ul=(246439.500, 4672656.500),
                            lr=(299769.500, 4604231.500),
                            res_x=resx,
                            res_y=resy)
        dem_dir = os.path.join(os.getcwd(), "test_get_water_data_maccanw2_vns")
        water_mask = os.path.join(dem_dir, "water_mask.tif")
        mnt = MNTBase.MNT(site, dem_dir, raw_dem=dem_dir, raw_gsw=dem_dir)
        self.assertTrue(os.path.exists(dem_dir))
        mnt.prepare_water_data(water_mask)
        self.assertTrue(os.path.exists(water_mask))
        img_read, drv = ImageIO.tiff_to_array(water_mask, array_only=False)
        img_expected = [[0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0]
                        , [0, 0, 0, 0, 1, 1, 0, 0, 0, 0, 0]
                        , [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
                        , [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
                        , [1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0]
                        , [1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0]
                        , [1, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0]
                        , [1, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0]
                        , [1, 1, 1, 1, 1, 0, 0, 0, 0, 0, 0]
                        , [1, 1, 1, 1, 1, 0, 0, 0, 0, 0, 0]
                        , [1, 1, 1, 1, 1, 1, 0, 0, 0, 0, 0]
                        , [1, 1, 1, 1, 1, 1, 1, 1, 0, 0, 0]
                        , [1, 1, 1, 1, 1, 1, 1, 1, 1, 0, 0]
                        , [1, 1, 1, 1, 1, 1, 1, 1, 1, 0, 0]]
        # Note the the part of the image which is not covered by the unittest.
        # This is where the border is ascending:
        self.assertEqual(ImageIO.get_resolution(drv), (resx, resy))
        self.assertEqual(ImageIO.get_epsg(drv), 32633)
        self.assertEqual(img_read.shape, (py, px))
        np.testing.assert_almost_equal(img_expected, img_read)
        FileSystem.remove_directory(dem_dir)

    def test_get_water_data_tls_l8(self):
        import numpy as np
        from Common import ImageIO, FileSystem
        resx, resy = 15000, -15000
        px, py = 15, 14
        site = MNTBase.Site("19080", 32631,
                            px=px,
                            py=py,
                            ul=(285431.584, 4884950.507),
                            lr=(510124.885, 4680403.373),
                            res_x=resx,
                            res_y=resy)
        dem_dir = os.path.join(os.getcwd(), "test_get_water_data_tls_l8")
        water_mask = os.path.join(dem_dir, "water_mask.tif")
        mnt = MNTBase.MNT(site, dem_dir, raw_dem=dem_dir, raw_gsw=dem_dir)
        self.assertTrue(os.path.exists(dem_dir))
        mnt.prepare_water_data(water_mask)
        self.assertTrue(os.path.exists(water_mask))
        img_read, drv = ImageIO.tiff_to_array(water_mask, array_only=False)
        img_expected = [[0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
                        , [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
                        , [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
                        , [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
                        , [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
                        , [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
                        , [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
                        , [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
                        , [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1]
                        , [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
                        , [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
                        , [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
                        , [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
                        , [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]]
        # Note the the part of the image which is not covered by the unittest.
        # This is where the border is ascending:
        self.assertEqual(ImageIO.get_resolution(drv), (resx, resy))
        self.assertEqual(ImageIO.get_epsg(drv), 32631)
        self.assertEqual(img_read.shape, (py, px))
        np.testing.assert_almost_equal(img_expected, img_read)
        FileSystem.remove_directory(dem_dir)


if __name__ == '__main__':
    unittest.main()
