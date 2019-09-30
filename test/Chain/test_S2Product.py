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
from Common import TestFunctions, FileSystem
from Chain.Product import MajaProduct
from Chain.S2Product import Sentinel2Natif, Sentinel2Muscate, Sentinel2SSC
import os


class TestS2Product(unittest.TestCase):
    prod_s2_nat = ["S2A_MSIL1C_20170412T110621_N0204_R137_T29RPQ_20170412T111708.SAFE",
                   "S2B_MSIL1C_20180316T103021_N0206_R108_T32TMR_20180316T123927.SAFE"]
    prod_s2_prd = ["S2A_OPER_PRD_MSIL1C_PDMC_20161109T171237_R135_V20160924T074932_20160924T081448.SAFE"]
    prod_s2_ssc = ["S2A_OPER_SSC_L2VALD_36JTT____20160914.DBL.DIR",
                   "S2B_OPER_SSC_L1VALD_21MXT____20180925.DBL.DIR"]
    prod_s2_mus = ["SENTINEL2B_20171008-105012-463_L1C_T31TCH_C_V1-0",
                   "SENTINEL2A_20161206-105012-463_L2A_T31TCH_C_V1-0",
                   "SENTINEL2X_20190415-000000-000_L3A_T31UFR_C_V1-1"]
    prods_other = ["LANDSAT8-OLITIRS-XSTHPAN_20170501-103532-111_L1C_T31TCH_C_V1-0",
                   "LANDSAT8_20170501-103532-111_L2A_T31TCH_C_V1-0",
                   "LC80390222013076EDC00",
                   "LC08_L1TP_199029_20170527_20170615_01_T1",
                   "L8_TEST_L8C_L2VALD_198030_20130626.DBL.DIR",
                   "VENUS-XS_20180201-051359-000_L1C_KHUMBU_C_V1-0",
                   "VENUS_20180201-051359-000_L2A_KHUMBU_C_V1-0",
                   "VENUS-XS_20180201-051359-000_L3A_KHUMBU_C_V1-0",
                   "VE_VM01_VSC_L2VALD_ISRAW906_20180317.DBL.DIR",
                   "VE_OPER_VSC_L1VALD_UNH_20180329.DBL.DIR"]

    @classmethod
    def setUpClass(cls):
        """
        Simulate the basic folder + metadata_file structure
        :return:
        """
        import os
        for root in cls.prod_s2_ssc:
            os.makedirs(root)
            metadata = root.split(".")[0] + ".HDR"
            TestFunctions.touch(metadata)
        for root in cls.prod_s2_mus:
            os.makedirs(root)
            metadata = os.path.join(root, root + "_MTD_ALL.xml")
            TestFunctions.touch(metadata)
        for root in cls.prod_s2_nat:
            os.makedirs(root)
            metadata = os.path.join(root, "MTD_MSIL1C.xml")
            TestFunctions.touch(metadata)

    @classmethod
    def tearDownClass(cls):
        import shutil
        import os
        for root in cls.prod_s2_ssc:
            shutil.rmtree(root)
            metadata = root.split(".")[0] + ".HDR"
            os.remove(metadata)
        for root in cls.prod_s2_mus + cls.prod_s2_nat:
            shutil.rmtree(root)

    def test_reg_s2_muscate(self):
        tiles = ["31TCH", "31TCH", "31UFR"]
        levels = ["l1c", "l2a", "l3a"]
        dates = ["20171008T105012", "20161206T105012", "20190415T000000"]
        validity = [True, False, False]
        for prod, tile, date, level, valid in zip(self.prod_s2_mus, tiles, dates, levels, validity):
            p = MajaProduct(prod).factory()
            self.assertIsInstance(p, Sentinel2Muscate)
            self.assertEqual(p.level, level)
            self.assertEqual(p.platform, "sentinel2")
            self.assertEqual(p.type, "muscate")
            self.assertEqual(p.tile, tile)
            self.assertEqual(p.date.strftime("%Y%m%dT%H%M%S"), date)
            self.assertTrue(os.path.basename(p.metadata_file).endswith("_MTD_ALL.xml"))
            self.assertTrue(os.path.exists(p.metadata_file))
            self.assertEqual(p.validity, valid)
            link_dir = "linkdir"
            FileSystem.create_directory(link_dir)
            p.link(link_dir)
            self.assertTrue(os.path.islink(os.path.join(link_dir, p.base)))
            self.assertEqual(p.mnt_resolutions_dict, [{"name": "R1", "val": "10 -10"},
                                                      {"name": "R2", "val": "20 -20"}])
            self.assertEqual(p, p)
        # Other prods:
        for prod in self.prod_s2_prd + self.prod_s2_ssc + self.prod_s2_nat + self.prods_other:
            p = MajaProduct(prod).factory()
            self.assertNotIsInstance(p, Sentinel2Muscate)

    def test_reg_s2_natif(self):
        tiles = ["29RPQ", "32TMR"]
        dates = ["20170412T110621", "20180316T103021"]
        for prod, tile, date in zip(self.prod_s2_nat, tiles, dates):
            p = MajaProduct(prod).factory()
            self.assertIsInstance(p, Sentinel2Natif)
            self.assertEqual(p.level, "l1c")
            self.assertEqual(p.platform, "sentinel2")
            self.assertEqual(p.type, "natif")
            self.assertEqual(p.tile, tile)
            self.assertEqual(p.date.strftime("%Y%m%dT%H%M%S"), date)
            self.assertTrue(os.path.basename(p.metadata_file), "MTD_MSIL1C.xml")
            self.assertTrue(os.path.exists(p.metadata_file))
            self.assertEqual(p.validity, True)
            link_dir = "linkdir"
            FileSystem.create_directory(link_dir)
            p.link(link_dir)
            self.assertTrue(os.path.islink(os.path.join(link_dir, p.base)))
            self.assertEqual(p.mnt_resolutions_dict, [{"name": "R1", "val": "10 -10"},
                                                      {"name": "R2", "val": "20 -20"}])
            self.assertEqual(p, p)

        # Other prods:
        for prod in self.prod_s2_prd + self.prod_s2_ssc + self.prod_s2_mus + self.prods_other:
            p = MajaProduct(prod).factory()
            self.assertNotIsInstance(p, Sentinel2Natif)

    def test_reg_s2_ssc(self):
        tiles = ["36JTT", "21MXT"]
        dates = ["20160914T120000", "20180925T120000"]
        levels = ["l2a", "l1c"]
        validity = [True, True]
        for prod, tile, date, level, valid in zip(self.prod_s2_ssc, tiles, dates, levels, validity):
            p = MajaProduct(prod).factory()
            self.assertIsInstance(p, Sentinel2SSC)
            self.assertEqual(p.level, level)
            self.assertEqual(p.platform, "sentinel2")
            self.assertEqual(p.type, "natif")
            self.assertEqual(p.tile, tile)
            self.assertEqual(p.date.strftime("%Y%m%dT%H%M%S"), date)
            self.assertEqual(os.path.basename(p.metadata_file), prod.split(".")[0] + ".HDR")
            self.assertTrue(os.path.exists(p.metadata_file))
            self.assertEqual(p.validity, valid)
            link_dir = "linkdir"
            FileSystem.create_directory(link_dir)
            p.link(link_dir)
            self.assertTrue(os.path.islink(os.path.join(link_dir, p.base)))
            self.assertEqual(p.mnt_resolutions_dict, [{"name": "R1", "val": "10 -10"},
                                                      {"name": "R2", "val": "20 -20"}])
            self.assertEqual(p, p)

        # Other prods:
        for prod in self.prod_s2_prd + self.prod_s2_nat + self.prod_s2_mus:
            p = MajaProduct(prod).factory()
            self.assertNotIsInstance(p, Sentinel2SSC)

    def test_reg_s2_prd(self):
        tiles = [None]
        dates = ["20161109T171237"]
        levels = ["l1c"]
        for prod, tile, date, level in zip(self.prod_s2_prd, tiles, dates, levels):
            # TODO Currently not supported
            self.assertIsNone(MajaProduct(prod).factory())
