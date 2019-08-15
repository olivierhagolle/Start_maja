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
from Chain.GippFile import GIPPFile, GippSet
import os


class TestGippFile(unittest.TestCase):
    root = os.getcwd()

    subdir_prefix = os.path.join(root, "CAMS")
    n_cams = 3
    tiles = ["T31TCH", "T12SQE", "SO2", "12949"]
    mnt = []

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

    def test_download_s2_tm_nocams(self):
        from Common import FileSystem
        g = GippSet(self.root, "sentinel2", "tm")
        g.download()
        self.assertTrue(os.path.isdir(g.out_path))
        n_l2comm = len(FileSystem.find("*L2COMM*", g.out_path))
        self.assertEqual(n_l2comm, 4)
        n_qltl = len(FileSystem.find("*CKQLTL*", g.out_path))
        self.assertEqual(n_qltl, 4)
        n_extl = len(FileSystem.find("*CKEXTL*", g.out_path))
        self.assertEqual(n_extl, 4)
        n_extl = len(FileSystem.find("*EEF", g.out_path))
        self.assertEqual(n_extl, 15)
        FileSystem.remove_directory(g.out_path)
        self.assertFalse(os.path.isdir(g.out_path))
        FileSystem.remove_file(os.path.join(self.root, "wget-log"))

    def test_download_s2_muscate_nocams(self):
        from Common import FileSystem
        g = GippSet(self.root, "sentinel2", "muscate")
        g.download()
        self.assertTrue(os.path.isdir(g.out_path))
        n_l2comm = len(FileSystem.find("*L2COMM*", g.out_path))
        self.assertEqual(n_l2comm, 2)
        n_qltl = len(FileSystem.find("*CKQLTL*", g.out_path))
        self.assertEqual(n_qltl, 2)
        n_extl = len(FileSystem.find("*CKEXTL*", g.out_path))
        self.assertEqual(n_extl, 2)
        n_extl = len(FileSystem.find("*EEF", g.out_path))
        self.assertEqual(n_extl, 9)
        FileSystem.remove_directory(g.out_path)
        self.assertFalse(os.path.isdir(g.out_path))
        FileSystem.remove_file(os.path.join(self.root, "wget-log"))

    def test_download_s2_natif_nocams(self):
        from Common import FileSystem
        g = GippSet(self.root, "sentinel2", "natif")
        g.download()
        self.assertTrue(os.path.isdir(g.out_path))
        n_l2comm = len(FileSystem.find("*L2COMM*", g.out_path))
        self.assertEqual(n_l2comm, 2)
        n_qltl = len(FileSystem.find("*CKQLTL*", g.out_path))
        self.assertEqual(n_qltl, 2)
        n_extl = len(FileSystem.find("*CKEXTL*", g.out_path))
        self.assertEqual(n_extl, 2)
        n_extl = len(FileSystem.find("*EEF", g.out_path))
        self.assertEqual(n_extl, 9)
        FileSystem.remove_directory(g.out_path)
        self.assertFalse(os.path.isdir(g.out_path))
        FileSystem.remove_file(os.path.join(self.root, "wget-log"))

    def test_download_l8_muscate_nocams(self):
        from Common import FileSystem
        g = GippSet(self.root, "landsat8", "muscate")
        g.download()
        self.assertTrue(os.path.isdir(g.out_path))
        n_l2comm = len(FileSystem.find("*L2COMM*", g.out_path))
        self.assertEqual(n_l2comm, 1)
        n_qltl = len(FileSystem.find("*CKQLTL*", g.out_path))
        self.assertEqual(n_qltl, 1)
        n_extl = len(FileSystem.find("*CKEXTL*", g.out_path))
        self.assertEqual(n_extl, 1)
        n_extl = len(FileSystem.find("*EEF", g.out_path))
        self.assertEqual(n_extl, 5)
        FileSystem.remove_directory(g.out_path)
        self.assertFalse(os.path.isdir(g.out_path))
        FileSystem.remove_file(os.path.join(self.root, "wget-log"))

    def test_download_vs_muscate_nocams(self):
        from Common import FileSystem
        g = GippSet(self.root, "venus", "muscate")
        g.download()
        self.assertTrue(os.path.isdir(g.out_path))
        n_l2comm = len(FileSystem.find("*L2COMM*", g.out_path))
        self.assertEqual(n_l2comm, 1)
        n_qltl = len(FileSystem.find("*CKQLTL*", g.out_path))
        self.assertEqual(n_qltl, 1)
        n_extl = len(FileSystem.find("*CKEXTL*", g.out_path))
        self.assertEqual(n_extl, 1)
        n_extl = len(FileSystem.find("*EEF", g.out_path))
        self.assertEqual(n_extl, 5)
        FileSystem.remove_directory(g.out_path)
        self.assertFalse(os.path.isdir(g.out_path))
        FileSystem.remove_file(os.path.join(self.root, "wget-log"))

    def test_download_l8_natif_nocams(self):
        from Common import FileSystem
        g = GippSet(self.root, "landsat8", "natif")
        g.download()
        self.assertTrue(os.path.isdir(g.out_path))
        n_l2comm = len(FileSystem.find("*L2COMM*", g.out_path))
        self.assertEqual(n_l2comm, 1)
        n_qltl = len(FileSystem.find("*CKQLTL*", g.out_path))
        self.assertEqual(n_qltl, 1)
        n_extl = len(FileSystem.find("*CKEXTL*", g.out_path))
        self.assertEqual(n_extl, 1)
        n_extl = len(FileSystem.find("*EEF", g.out_path))
        self.assertEqual(n_extl, 5)
        FileSystem.remove_directory(g.out_path)
        self.assertFalse(os.path.isdir(g.out_path))
        FileSystem.remove_file(os.path.join(self.root, "wget-log"))

    def test_download_vs_natif_nocams(self):
        from Common import FileSystem
        g = GippSet(self.root, "venus", "natif")
        g.download()
        self.assertTrue(os.path.isdir(g.out_path))
        n_l2comm = len(FileSystem.find("*L2COMM*", g.out_path))
        self.assertEqual(n_l2comm, 1)
        n_qltl = len(FileSystem.find("*CKQLTL*", g.out_path))
        self.assertEqual(n_qltl, 1)
        n_extl = len(FileSystem.find("*CKEXTL*", g.out_path))
        self.assertEqual(n_extl, 1)
        n_extl = len(FileSystem.find("*EEF", g.out_path))
        self.assertEqual(n_extl, 5)
        FileSystem.remove_directory(g.out_path)
        self.assertFalse(os.path.isdir(g.out_path))
        FileSystem.remove_file(os.path.join(self.root, "wget-log"))

    def test_symlink(self):
        from Common import FileSystem
        g = GippSet(self.root, "sentinel2", "tm")
        g.download()
        self.assertTrue(os.path.isdir(g.out_path))
        symlink_dir = os.path.join(self.root, "symlinks")
        FileSystem.create_directory(symlink_dir)
        with self.assertRaises(ValueError):
            self.assertTrue(len(FileSystem.find("*EEF", symlink_dir)), 0)
        g.link(symlink_dir)
        self.assertEqual(len(FileSystem.find("*EEF", symlink_dir)), 15)
        FileSystem.remove_directory(symlink_dir)
        self.assertFalse(os.path.isdir(symlink_dir))


if __name__ == '__main__':
    unittest.main()
