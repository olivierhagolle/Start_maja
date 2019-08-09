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
from Start_maja import StartMaja
import sys
import os
from datetime import datetime
sys.path.append(StartMaja.current_dir)  # Replaces __init__.py


def create_dummy_product(root, product_level, **kwargs):
    """
    Create a dummy S2 product with no content
    :param root: The base directory to create the product in
    :param product_level: "L1C", "L2A" or "L3A"
    :param kwargs: Optional overloading of parameters
    :return:
    """
    import random
    import string
    from datetime import timedelta
    from Common import TestFunctions

    assert os.path.isdir(root)
    letters = string.ascii_uppercase
    platform_options = {"L1C": ["S2A", "S2B"],
                        "L2A": ["SENTINEL2B", "SENTINEL2A"],
                        "L3A": ["SENTINEL2A", "SENTINEL2B", "VENUS-XS"]}
    platform = kwargs.get("platform", random.choice(platform_options[product_level]))
    date = kwargs.get("date", datetime(2015, 1, 1) + timedelta(days=random.randint(0, 10000),
                                                               hours=random.randint(10, 12),
                                                               minutes=random.randint(0, 60),
                                                               seconds=random.randint(0, 60)))
    tile = kwargs.get("tile", "T" + str(random.randint(0, 99)).zfill(2) +
                      ''.join(random.choice(letters) for _ in range(3)))
    orbit_ms = kwargs.get("orbit", random.randint(0, 999))
    version_orbit = kwargs.get("version", random.randint(0, 9))
    if product_level == "L1C":
        date_str = date.strftime("%Y%m%dT%H%M%S")
        product_name = "_".join([platform,
                                 "MSIL1C",
                                 date_str,
                                 "N" + str(orbit_ms).zfill(4),
                                 "R" + str(version_orbit).zfill(3),
                                 tile,
                                 date_str + ".SAFE"])
        product_path = os.path.join(root, product_name)
        metadata_path = os.path.join(product_path, "MTD_MSIL1C.xml")
        os.makedirs(product_path)
        TestFunctions.touch(metadata_path)
    elif product_level in ["L2A", "L3A"]:
        date_str = date.strftime("%Y%m%d-%H%M%S-") + str(orbit_ms)
        product_name = "_".join([platform,
                                date_str,
                                product_level,
                                tile,
                                random.choice("DC"),
                                "V" + str(version_orbit) + "-" + str(version_orbit)])
        product_path = os.path.join(root, product_name)
        metadata_path = os.path.join(product_path, product_name + "_MTD_ALL.xml")
        os.makedirs(product_path)
        TestFunctions.touch(metadata_path)
    print(product_path)
    return product_path, date


def create_dummy_mnt(root, tile, platform="GEN"):
    """
    Create a dummy mnt with no content specific to a platform and tile
    :param root: The path to create the mnt in
    :param tile: The tile identifier
    :param platform: The platform name, e.g. "S2" or "L8"
    :return: Returns the directory containing the dummy mnt
    """
    import random
    from Common import TestFunctions

    basename = "_".join([platform, "TEST", "AUX", "REFDE2", tile, str(random.randint(0, 1000)).zfill(4)])
    mnt_name = os.path.join(root, basename)
    dbl_name = os.path.join(mnt_name, basename + ".DBL.DIR")
    hdr_name = os.path.join(mnt_name, basename + ".HDR")
    os.makedirs(mnt_name)
    os.makedirs(dbl_name)
    TestFunctions.touch(hdr_name)
    return mnt_name


def modify_folders_file(root, new_file, **kwargs):
    """
    Modify the template test_folders file with the given arguments
    :param root: The path to the existing template file
    :param new_file: The new file path
    :param kwargs: The arguments to modify inside the file
    :return: The full path to the new file
    """
    try:
        import configparser as cfg
    except ImportError:
        import ConfigParser as cfg

    assert os.path.isfile(root)
    cfg_parser = cfg.RawConfigParser()
    cfg_parser.read(root)
    for arg in kwargs:
        cfg_parser.set("PATH", arg, kwargs[arg])

    with open(new_file, 'w') as f:
        cfg_parser.write(f)
    return new_file


def create_dummy_cams(root, date, platform="GEN"):
    """
    Create a few dummy CAMS files
    :param root: The path to create the cams folder in
    :param date: The start date the cams file is valid for.
    :param platform: The platform name, e.g. "S2" or "L8"
    :return: Creates the directory containing the cams folder
    """
    from Common import TestFunctions
    end_date = datetime(2099, 1, 1, 23, 59, 59)

    basename = "_".join([platform, "TEST", "EXO", "CAMS",
                         date.strftime("%Y%m%dT%H%M%S"),
                         end_date.strftime("%Y%m%dT%H%M%S")])
    dbl_name = os.path.join(root, basename + ".DBL.DIR")
    hdr_name = os.path.join(root, basename + ".HDR")
    os.makedirs(dbl_name)
    TestFunctions.touch(hdr_name)


class TestStartMaja(unittest.TestCase):

    root = os.getcwd()
    n_not_used = 2
    n_dummies = 2
    start_product = datetime(2014, 12, 31, 10, 50)
    end_product = datetime(2099, 12, 31)

    dates = []
    tile = "T31TCH"
    site = None
    gipp = os.path.join(os.getcwd(), "nominal")
    start = None
    end = None
    nbackward = 8
    overwrite = "True"
    verbose = "True"
    template_folders_file = os.path.join(os.getcwd(), "test", "test_folders.txt")

    @classmethod
    def setUpClass(cls):
        cls.product_root = os.path.join(cls.root, cls.tile)
        os.makedirs(cls.product_root)
        cls.youngest, date = create_dummy_product(cls.product_root, "L1C",
                                                  tile=cls.tile,
                                                  date=cls.start_product)
        cls.dates.append(date)
        cls.oldest, date = create_dummy_product(cls.product_root, "L1C",
                                                tile=cls.tile,
                                                date=cls.end_product)
        cls.dates.append(date)

        for i in range(cls.n_dummies):
            product, date = create_dummy_product(cls.product_root, "L1C", tile=cls.tile)
            cls.dates.append(date)
            product, date = create_dummy_product(cls.product_root, "L2A", tile=cls.tile)
            cls.dates.append(date)

        for i in range(cls.n_not_used):
            product, date = create_dummy_product(cls.product_root, "L1C")
            cls.dates.append(date)
            product, date = create_dummy_product(cls.product_root, "L2A")
            cls.dates.append(date)
        cls.folders_file = os.path.join(cls.root, "test_working_folders_file.txt")
        modify_folders_file(cls.template_folders_file, new_file=cls.folders_file,
                            repWork=os.getcwd(),
                            repL1=os.getcwd(),
                            repL2=os.getcwd(),
                            repMNT=os.getcwd())
        cls.mnt = create_dummy_mnt(root=cls.root, tile=cls.tile)

        cls.cams = os.path.join(cls.root, "CAMS")
        os.makedirs(cls.cams)
        for date in cls.dates:
            create_dummy_cams(cls.cams, date)

        assert os.path.isfile(cls.folders_file)

    @classmethod
    def tearDownClass(cls):
        import shutil
        # In case there's duplicates, remove them:
        shutil.rmtree(cls.product_root)
        os.remove(cls.folders_file)
        shutil.rmtree(cls.mnt)
        shutil.rmtree(cls.cams)

    def test_dates_and_products(self):
        start_maja = StartMaja(self.folders_file,
                               self.tile,
                               self.site,
                               self.gipp,
                               self.start,
                               self.end,
                               self.nbackward,
                               self.overwrite,
                               self.verbose)
        self.assertEqual(len(start_maja.avail_input_l1), self.n_dummies + 2)
        self.assertEqual(len(start_maja.avail_input_l2), self.n_dummies)
        self.assertEqual(start_maja.start, self.start_product)
        self.assertEqual(start_maja.end, self.end_product)

    def test_parasite_l2a_product(self):
        product, _ = create_dummy_product(self.product_root, "L2A",
                                          platform="LANDSAT8",
                                          tile="T31TCH",
                                          date=self.end_product)
        with self.assertRaises(IOError):
            StartMaja(self.folders_file,
                      self.tile,
                      self.site,
                      self.gipp,
                      self.start,
                      self.end,
                      self.nbackward,
                      self.overwrite,
                      self.verbose)
        import shutil
        shutil.rmtree(product)
        self.assertFalse(os.path.exists(product))

    def test_non_existing_l1c_folder(self):
        folders_path = os.path.join(os.getcwd(), "test_error_folder_file.txt")
        modify_folders_file(self.folders_file, new_file=folders_path,
                            repL1="/a/b/c")
        with self.assertRaises(OSError):
            StartMaja(folders_path,
                      self.tile,
                      self.site,
                      self.gipp,
                      self.start,
                      self.end,
                      self.nbackward,
                      self.overwrite,
                      self.verbose)

        os.remove(folders_path)
        self.assertFalse(os.path.exists(folders_path))

    def test_non_existing_l2a_folder(self):
        folders_path = os.path.join(os.getcwd(), "test_error_folder_file.txt")
        modify_folders_file(self.folders_file, new_file=folders_path,
                            repL2="/a/b/c")
        with self.assertRaises(OSError):
            StartMaja(folders_path,
                      self.tile,
                      self.site,
                      self.gipp,
                      self.start,
                      self.end,
                      self.nbackward,
                      self.overwrite,
                      self.verbose)

        os.remove(folders_path)
        self.assertFalse(os.path.exists(folders_path))

    def test_custom_start_end_dates(self):
        start = datetime(2017, 1, 1)
        end = datetime(2019, 1, 1)
        s = StartMaja(self.folders_file,
                      self.tile,
                      self.site,
                      self.gipp,
                      start.strftime("%Y-%m-%d"),
                      end.strftime("%Y-%m-%d"),
                      self.nbackward,
                      self.overwrite,
                      self.verbose)

        self.assertEqual(s.start, start)
        self.assertEqual(s.end, end)

    def test_product_sorting(self):
        s = StartMaja(self.folders_file,
                      self.tile,
                      self.site,
                      self.gipp,
                      self.start,
                      self.end,
                      self.nbackward,
                      self.overwrite,
                      self.verbose)

        self.assertEqual(s.avail_input_l1[-1].fpath, self.oldest)
        self.assertEqual(s.avail_input_l1[0].fpath, self.youngest)


if __name__ == '__main__':
    unittest.main()
