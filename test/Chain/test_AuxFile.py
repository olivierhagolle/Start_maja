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
from Chain.AuxFile import EarthExplorer, CAMSFile, DTMFile
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

    def test_cams_creation(self):
        from Common import FileSystem

        dbl = FileSystem.find("DBL.DIR", self.subdir_prefix)
        print(dbl)
        c = CAMSFile(dbl)
        self.assertIsNotNone(c)
        base = os.path.basename(dbl).split(".")[0]

        hdr = os.path.join(os.path.dirname(dbl), base + ".HDR")
        self.assertEqual(hdr, c.hdr)

    def test_wrong_cams_creation(self):
        from Common import FileSystem
        dbl = FileSystem.find("DBL.DIR", self.mnt[0])
        print(dbl)
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
            c = CAMSFile(dbl)
            self.assertIsNotNone(c)
            base = os.path.basename(dbl).split(".")[0]

            hdr = os.path.join(os.path.dirname(dbl), base + ".HDR")
            self.assertEqual(hdr, c.hdr)
