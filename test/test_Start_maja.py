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
