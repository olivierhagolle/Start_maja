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
from Chain.Workplan import Workplan


class TestWorkplan(unittest.TestCase):

    def test_name_hash(self):
        product_name = "S2B_MSIL1C_20400602T121200_N0044_R001_T31TCH_20400602T121200.SAFE"
        self.assertEqual(Workplan.get_dirname(product_name), "f9bfae79e5aa4a59feda03c8d6717f35")


if __name__ == '__main__':
    unittest.main()
