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

from Unittest import LoggedTestCase
from Unittest import testFunction
from Chain.AuxFile import CAMSFile, DTMFile, GIPPFile
import os
from datetime import datetime


def create_dummy_cams(root, date, platform="GEN"):
    """
    Create a few dummy CAMS files
    :param root: The path to create the cams folder in
    :param date: The start date the cams file is valid for.
    :param platform: The platform name, e.g. "S2" or "L8"
    :return: Creates the directory containing the cams folder
    """
    end_date = datetime(2099, 1, 1, 23, 59, 59)

    basename = "_".join([platform, "TEST", "EXO", "CAMS",
                         date.strftime("%Y%m%dT%H%M%S"),
                         end_date.strftime("%Y%m%dT%H%M%S")])
    dbl_name = os.path.join(root, basename + ".DBL.DIR")
    hdr_name = os.path.join(root, basename + ".HDR")
    os.makedirs(dbl_name)
    testFunction.touch(hdr_name)


def create_dummy_mnt(root, tile, platform="GEN"):
    """
    Create a dummy mnt with no content specific to a platform and tile
    :param root: The path to create the mnt in
    :param tile: The tile identifier
    :param platform: The platform name, e.g. "S2" or "L8"
    :return: Returns the directory containing the dummy mnt
    """
    import random
    basename = "_".join([platform, "TEST", "AUX", "REFDE2", tile, str(random.randint(0, 1000)).zfill(4)])
    mnt_name = os.path.join(root, basename)
    dbl_name = os.path.join(mnt_name, basename + ".DBL.DIR")
    hdr_name = os.path.join(mnt_name, basename + ".HDR")
    os.makedirs(mnt_name)
    os.makedirs(dbl_name)
    testFunction.touch(hdr_name)
    return mnt_name


class TestAuxFile(LoggedTestCase.LoggedTestCase):
    root = os.getcwd()

    subdir_prefix = os.path.join(root, "CAMS")
    n_cams = 3
    tiles = ["T31TCH", "T12SQE", "SO2", "12949"]
    mnt = []

    @classmethod
    def setUpClass(cls):
        """
        Sets up a random tree-like structure with a few sub-files and -folders
        Similar to test_FileSystem.
        :return:
        """
        from random import randint, choice
        os.makedirs(cls.subdir_prefix)
        for i in range(cls.n_cams):
            d = datetime(year=randint(2010, 2050),
                         month=randint(1, 12),
                         day=randint(1, 25),
                         hour=randint(1, 23),
                         minute=randint(1, 59))
            platform = choice(["S2_", "L8_", "GEN", "VE_"])
            create_dummy_cams(cls.subdir_prefix, d, platform)

        for tile in cls.tiles:
            platform = choice(["S2_", "L8_", "GEN", "VE_"])
            cls.mnt += [create_dummy_mnt(cls.root, tile, platform)]

    @classmethod
    def tearDownClass(cls):
        import shutil
        shutil.rmtree(cls.subdir_prefix)
        for m in cls.mnt:
            shutil.rmtree(m)

    @testFunction.test_function
    def test_cams_reg(self):
        import re
        cams = ["S2__PROD_EXO_CAMS_20171008T030000_20180628T174612.HDR",
                "VE__TEST_EXO_CAMS_20171008T150000_20180628T174630.DBL.DIR",
                "L8__TEST_EXO_CAMS_20171010T030000_20180628T174724.DBL"]
        for f in cams:
            self.assertTrue(re.search(CAMSFile.regex, f))

    @testFunction.test_function
    def test_dtm_reg(self):
        import re
        dtms = ["S2__TEST_AUX_REFDE2_T29RPQ_0001",
                "NONAME_TEST_AUX_REFDE2_TKHUMBU_0001"]
        for dtm in dtms:
            self.assertTrue(re.search(DTMFile.regex, dtm))

    @testFunction.test_function
    def test_gipp_reg(self):
        import re
        gipp_vns = ["VE_TEST_GIP_L2ALBD_L_ALLSITES_00010_20000101_99991231.HDR",
                    "VE_TEST_GIP_L2DIFT_L_ALLSITES_00010_20000101_99991231.HDR",
                    "VE_TEST_GIP_CKEXTL_S_CAMARGUE_00005_00000000_99999999.EEF",
                    "VE_TEST_GIP_L2SMAC_S_ALLSITES_00010_00000000_99999999.EEF",
                    "VE_TEST_GIP_L2SITE_S_ALLSITES_00001_00000000_99999999.EEF",
                    "VE_TEST_GIP_L2TOCR_L_ALLSITES_00010_20000101_99991231.HDR",
                    "VE_TEST_GIP_L2DIRT_L_ALLSITES_00010_20000101_99991231.HDR",
                    "VE_TEST_GIP_L2COMM_L_ALLSITES_00001_20170801_99991231.EEF",
                    "VE_TEST_GIP_L2WATV_L_ALLSITES_00005_20000101_99991231.HDR",
                    "VE_TEST_GIP_CKQLTL_S_CAMARGUE_00002_00000000_99999999.EEF"]
        gipp_s2 = ["S2B_PROD_GIP_L2COMM_L_ALLSITES_10009_20150703_21000101.EEF",
                   "S2B_TEST_GIP_L2TOCR_L_CONTINEN_10002_20150703_21000101.HDR",
                   "S2B_TEST_GIP_L2SMAC_L_ALLSITES_10005_20150703_21000101.EEF",
                   "S2A_TEST_GIP_L2TOCR_L_CONTINEN_10005_20150703_21000101.HDR",
                   "S2A_TEST_GIP_L2SMAC_L_ALLSITES_10005_20150703_21000101.EEF",
                   "S2A_TEST_GIP_L2COMM_L_ALLSITES_10009_20150703_21000101.EEF",
                   "S2B_TEST_GIP_L2ALBD_L_CONTINEN_10003_20150703_21000101.HDR",
                   "S2B_TEST_GIP_CKQLTL_S_31TJF____10005_20150703_21000101.EEF",
                   "S2A_TEST_GIP_L2DIRT_L_CONTINEN_10005_20150703_21000101.HDR",
                   "S2B_TEST_GIP_CKEXTL_S_31TJF____10001_20150703_21000101.EEF",
                   "S2A_TEST_GIP_L2DIFT_L_CONTINEN_10005_20150703_21000101.HDR",
                   "S2A_TEST_GIP_L2WATV_L_CONTINEN_10005_20150703_21000101.HDR",
                   "S2B_TEST_GIP_L2WATV_L_CONTINEN_10005_20150703_21000101.HDR",
                   "S2B_TEST_GIP_L2DIFT_L_CONTINEN_10002_20150703_21000101.HDR",
                   "S2A_TEST_GIP_CKEXTL_S_31TJF____10001_20150703_21000101.EEF",
                   "S2A_TEST_GIP_CKQLTL_S_31TJF____10005_20150703_21000101.EEF",
                   "S2__TEST_GIP_L2SITE_S_31TJF____10001_00000000_99999999.EEF",
                   "S2A_TEST_GIP_L2ALBD_L_CONTINEN_10005_20150703_21000101.HDR",
                   "S2B_TEST_GIP_L2DIRT_L_CONTINEN_10002_20150703_21000101.HDR"]
        gipp_l8 = ["L8_TEST_GIP_L2COMM_L_ALLSITES_90001_00000000_99999999.EEF",
                   "L8_TEST_GIP_L2SITE_S_EU93056200A00B_90001_00000000_99999999.EEF",
                   "L8_TEST_GIP_CKQLTL_S_EU93056200A00B_90001_00000000_99999999.EEF",
                   "L8_TEST_GIP_L2DIFT_L_CONTINEN_90001_00000000_99999999.HDR",
                   "L8_TEST_GIP_CKEXTL_S_EU93056200A00B_90001_00000000_99999999.EEF",
                   "L8_TEST_GIP_L2DIRT_L_CONTINEN_90001_00000000_99999999.HDR",
                   "L8_TEST_GIP_L2TOCR_L_CONTINEN_90001_00000000_99999999.HDR",
                   "L8_TEST_GIP_L2ALBD_L_CONTINEN_90001_00000000_99999999.HDR",
                   "L8_TEST_GIP_L2SMAC_L_ALLSITES_90001_00000000_99999999.EEF"]
        for gipp in gipp_vns + gipp_l8 + gipp_s2:
            self.assertTrue(re.search(GIPPFile.regex, gipp))

    def test_cams_creation(self):
        from Common import FileSystem

        dbl = FileSystem.find("DBL.DIR", self.subdir_prefix)
        c = CAMSFile(dbl)
        self.assertIsNotNone(c)
        base = os.path.basename(dbl).split(".")[0]

        hdr = os.path.join(os.path.dirname(dbl), base + ".HDR")
        self.assertEqual(hdr, c.hdr)

    def test_wrong_cams_creation(self):
        from Common import FileSystem
        dbl = FileSystem.find("DBL.DIR", self.mnt[0])
        self.assertIsNone(CAMSFile(dbl))

    def test_cams_date(self):
        from Common import FileSystem

        dbl = FileSystem.find("DBL.DIR", self.subdir_prefix)
        c = CAMSFile(dbl)
        base = os.path.basename(dbl).split(".")[0]
        date = datetime.strptime(base.split("_")[-2], "%Y%m%dT%H%M%S")
        self.assertEqual(c.get_date(), date)

    def test_mnt_creation(self):
        from Common import FileSystem
        for m in self.mnt:
            dbl = FileSystem.find("DBL.DIR", m)
            d = DTMFile(dbl)
            self.assertIsNotNone(d)
            base = os.path.basename(dbl).split(".")[0]
            hdr = os.path.join(os.path.dirname(dbl), base + ".HDR")
            self.assertEqual(hdr, d.hdr)

    def test_wrong_mnt_creation(self):
        from Common import FileSystem
        dbl = FileSystem.find("DBL.DIR", self.subdir_prefix)
        self.assertIsNone(DTMFile(dbl))