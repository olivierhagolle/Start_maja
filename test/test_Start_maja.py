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
from Start_maja import StartMaja
import os
from datetime import datetime


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
        testFunction.touch(metadata_path)
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
        testFunction.touch(metadata_path)
    print(product_path)
    return product_path, [platform, tile, date]


def create_dummy_mnt(root, tile, platform="GEN"):
    """
    Create a dummy mnt with no content specific to a platform and tile
    :param root: The path to create the mnt in
    :param tile: The tile identifier
    :param platform: The platform name, e.g. "S2" or "L8"
    :return: Returns the directory containing the dummy mny
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


class TestStartMaja(LoggedTestCase.LoggedTestCase):

    root = os.getcwd()
    n_not_used = 2
    n_dummies = 2
    start_product = datetime(2014, 12, 31, 10, 50)
    end_product = datetime(2099, 12, 31)

    products = []
    tile = "T31TCH"
    site = None
    gipp = os.path.join(os.getcwd(), "nominal")
    start = None
    end = None
    nbackward = 8
    verbose = "True"
    template_folders_file = os.path.join(os.getcwd(), "test", "test_folders.txt")

    @classmethod
    def setUpClass(cls):
        cls.product_root = os.path.join(cls.root, cls.tile)
        os.makedirs(cls.product_root)
        cls.products += [create_dummy_product(cls.product_root, "L1C",
                                              tile=cls.tile,
                                              date=cls.start_product)[0]]
        cls.products += [create_dummy_product(cls.product_root, "L1C",
                                              tile=cls.tile,
                                              date=cls.end_product)[0]]
        cls.products += [create_dummy_product(cls.product_root, "L1C", tile=cls.tile)[0] for _ in range(cls.n_dummies)]
        cls.products += [create_dummy_product(cls.product_root, "L2A", tile=cls.tile)[0] for _ in range(cls.n_dummies)]
        cls.products += [create_dummy_product(cls.product_root, "L1C")[0] for _ in range(cls.n_not_used)]
        cls.products += [create_dummy_product(cls.product_root, "L2A")[0] for _ in range(cls.n_not_used)]
        cls.folders_file = os.path.join(cls.root, "test_working_folders_file.txt")
        modify_folders_file(cls.template_folders_file, new_file=cls.folders_file,
                            repWork=os.getcwd(),
                            repL1=os.getcwd(),
                            repL2=os.getcwd(),
                            repMNT=os.getcwd())
        cls.mnt = create_dummy_mnt(root=cls.root, tile=cls.tile)
        assert os.path.isfile(cls.folders_file)

    @classmethod
    def tearDownClass(cls):
        import shutil
        # In case there's duplicates, remove them:
        shutil.rmtree(cls.product_root)
        os.remove(cls.folders_file)
        shutil.rmtree(cls.mnt)

    @testFunction.test_function
    def test_cams_reg(self):
        import re
        cams = ["S2__PROD_EXO_CAMS_20171008T030000_20180628T174612.HDR",
                "VE__TEST_EXO_CAMS_20171008T150000_20180628T174630.DBL.DIR",
                "L8__TEST_EXO_CAMS_20171010T030000_20180628T174724.DBL"]
        for f in cams:
            self.assertTrue(re.search(StartMaja.regCAMS, f))

    @testFunction.test_function
    def test_dtm_reg(self):
        import re
        dtms = ["S2__TEST_AUX_REFDE2_T29RPQ_0001",
                "NONAME_TEST_AUX_REFDE2_TKHUMBU_0001"]
        for dtm in dtms:
            self.assertTrue(re.search(StartMaja.regDTM, dtm))

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
            check = list(re.search(pattern, gipp) for pattern in StartMaja.regGIPP)
            self.assertFalse(all(v is None for v in check))

    @testFunction.test_function
    def test_dates_and_products(self):
        start_maja = StartMaja(self.folders_file,
                               self.tile,
                               self.site,
                               self.gipp,
                               self.start,
                               self.end,
                               self.nbackward,
                               self.verbose)
        self.assertEqual(len(start_maja.avail_input_l1), self.n_dummies + 2)
        self.assertEqual(len(start_maja.avail_input_l2), self.n_dummies)
        self.assertEqual(start_maja.start, self.start_product)
        self.assertEqual(start_maja.end, self.end_product)

    @testFunction.test_function
    def test_parasite_l2a_product(self):
        self.products += [create_dummy_product(self.product_root, "L2A",
                                               platform="LANDSAT8",
                                               tile="T31TCH",
                                               date=self.end_product)[0]]
        with self.assertRaises(IOError):
            StartMaja(self.folders_file,
                      self.tile,
                      self.site,
                      self.gipp,
                      self.start,
                      self.end,
                      self.nbackward,
                      self.verbose)

    @testFunction.test_function
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
                      self.verbose)

        os.remove(folders_path)
        self.assertFalse(os.path.exists(folders_path))

    @testFunction.test_function
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
                      self.verbose)

        os.remove(folders_path)
        self.assertFalse(os.path.exists(folders_path))

    @testFunction.test_function
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
                      self.verbose)

        self.assertEqual(s.start, start)
        self.assertEqual(s.end, end)
