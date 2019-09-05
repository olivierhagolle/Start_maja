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

    def atest_gsw_download(self):
        from Common import FileSystem
        gsw_codes = ['10E_50N']
        fnames = MNTBase.MNT.download_gsw(gsw_codes, os.getcwd())
        self.assertEqual(len(fnames), 1)
        for fn in fnames:
            self.assertTrue(os.path.exists(fn))
            self.assertEqual(os.path.basename(fn), "occurrence_10E_50N_v1_1.tif")
            FileSystem.remove_file(fn)
            self.assertFalse(os.path.isfile(fn))

    def test_get_water_data(self):
        import numpy as np
        from Common import ImageIO, FileSystem
        width, height = 100, 100
        water_input = MNTBase.Site("World", 4326,
                                   px=width,
                                   py=height,
                                   ul=(50, -10),
                                   lr=(50, -10),
                                   res_x=.5,
                                   res_y=-.5)
        site = MNTBase.Site("T31TCJ", 32631,
                            px=400,
                            py=500,
                            ul=(300000.000, 4900020.000),
                            lr=(409800.000, 4790220.000),
                            res_x=400,
                            res_y=-400)
        img = np.ones((height, width), np.int16) * 150
        img[:99, :99] = 0
        path = os.path.join(os.getcwd(), "test_get_water_data.tif")
        water_mask = os.path.join(os.getcwd(), "water_mask.tif")
        dem_dir = os.path.join(os.getcwd(), "dummy_dir")
        ImageIO.write_geotiff_existing(img, path, water_input.to_driver(water_mask))
        self.assertTrue(os.path.exists(path))

        mnt = MNTBase.MNT(site, dem_dir)
        mnt.get_water_data(water_mask, [path])
        self.assertTrue(os.path.exists(water_mask))
        img_read, drv = ImageIO.tiff_to_array(water_mask, array_only=False)
        np.testing.assert_almost_equal(img_read[:, :170], 0)
        np.testing.assert_almost_equal(img_read[0, 190:], 1)

        # TODO Finish this!
        FileSystem.remove_file(path)
        FileSystem.remove_file(water_mask)
        FileSystem.remove_directory(dem_dir)

if __name__ == '__main__':
    unittest.main()
