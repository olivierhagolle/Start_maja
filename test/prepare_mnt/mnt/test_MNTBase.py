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
                            ul=(300000.000, 4900020.000),
                            lr=(409800.000, 4790220.000),
                            res_x=10,
                            res_y=-10)

        gsw_codes = MNTBase.MNT.get_gsw_codes(site)
        self.assertEqual(gsw_codes, ['0E_50N'])
        fn = MNTBase.MNT.download_gsw(gsw_codes, os.getcwd())
        self.assertEqual(len(fn), 1)
        self.assertEqual(os.path.basename(fn[0]), "occurrence_0E_50N_v1_1.tif")

    def test_gsw_codes_spain(self):
        site = MNTBase.Site("T31TBE", 32631,
                            ul=(199980.000, 4500000.000),
                            lr=(309780.000, 4390200.000),
                            res_x=10,
                            res_y=-10)

        gsw_codes = MNTBase.MNT.get_gsw_codes(site)
        self.assertEqual(gsw_codes, ['0E_40N', '0E_50N', '10W_40N', '10W_50N'])

    def test_gsw_codes_zero_center(self):
        site = MNTBase.Site("Somewhere_over_the_ocean", 32631,
                            ul=(-250000.000, 250000.000),
                            lr=(250000.000, -120000.000),
                            res_x=10,
                            res_y=-10)

        gsw_codes = MNTBase.MNT.get_gsw_codes(site)
        self.assertEqual(gsw_codes, ['0E_0N', '0E_10N', '10W_0N', '10W_10N'])

    def test_gsw_codes_south_america(self):
        site = MNTBase.Site("Ecuador", 32619,
                            ul=(-250000.000, 250000.000),
                            lr=(400000.000, -120000.000),
                            res_x=10,
                            res_y=-10)

        gsw_codes = MNTBase.MNT.get_gsw_codes(site)
        self.assertEqual(gsw_codes, ['70W_0N', '70W_10N', '80W_0N', '80W_10N'])

    def test_gsw_codes_longitude_change(self):
        site = MNTBase.Site("Russia", 32601,
                            ul=(-250000.000, 250000.000),
                            lr=(400000.000, -120000.000),
                            res_x=10,
                            res_y=-10)
        # TODO Support this:
        with self.assertRaises(ValueError):
            MNTBase.MNT.get_gsw_codes(site)


if __name__ == '__main__':
    unittest.main()
