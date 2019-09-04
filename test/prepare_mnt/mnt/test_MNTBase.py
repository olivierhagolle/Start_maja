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
from prepare_mnt.mnt import MNTBase


class TestMNTBase(unittest.TestCase):

    def atest_gsw_codes_toulouse(self):
        site = MNTBase.Site("T31TCJ", 32631,
                            ul=(300000.000, 4900020.000),
                            lr=(409800.000, 4790220.000),
                            res_x=10,
                            res_y=-10)

        gsw_codes = MNTBase.MNT.get_gsw_codes(site)
        self.assertEqual(gsw_codes, [0, 1])

    def test_gsw_codes_spain(self):
        site = MNTBase.Site("T31TBE", 32631,
                            ul=(199980.000, 4500000.000),
                            lr=(309780.000, 4390200.000),
                            res_x=10,
                            res_y=-10)

        gsw_codes = MNTBase.MNT.get_gsw_codes(site)
        self.assertEqual(gsw_codes, [0, 1])


if __name__ == '__main__':
    unittest.main()
