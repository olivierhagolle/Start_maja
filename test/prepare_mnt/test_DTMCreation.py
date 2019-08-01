#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Copyright (C) CNES, CS-SI France - All Rights Reserved
This file is subject to the terms and conditions defined in
file 'LICENSE.md', which is part of this source code package.

Author:         Peter KETTIG <peter.kettig@cnes.fr>, Pierre LASSALLE <pierre.lassalle@cnes.fr>
Project:        StartMaja, CNES
Created on:     Wed Sep 12 09:12:51 2018
"""

from Unittest import LoggedTestCase
from Unittest import testFunction
from prepare_mnt import DTMCreation


class TestDTMCreation(LoggedTestCase.LoggedTestCase):

    @testFunction.test_function
    def testFileNotExisting(self):
        product = "a/b/c/notavalidproduct"
        with self.assertRaises(OSError):
            # File not existing
            import os
            DTMCreation.DTMCreator(product, None, None, os.getcwd(), os.getcwd())

    @testFunction.test_function
    def testExistingLocdalFileS2Native(self):
        import os
        product = "/home/akynos/MAJA/inputs/L1/29RPQ/S2A_MSIL1C_20180706T110621_N0206_R137_T29RPQ_20180706T132942.SAFE/"
        srtm = "/home/akynos/MAJA/DTM/Creation/SRTM"
        water = "/home/akynos/MAJA/DTM/Creation/Water"
        if(os.path.exists(product)):
            self.logger.info("Found existing product")
            c = DTMCreation.DTMCreator(dirProduct=product, kml=None, granuleID=None, dirSRTM=srtm, dirWater=water)
            self.assertTrue(c.isNativeProduct(product))
            mission, mtd, mtype = c.findMetadataFile(product)
            self.assertEqual(mission, c.s2Mission)
            self.assertTrue(os.path.exists(mtd))
        else:
            self.logger.warning("WARNING: Did not find existing product")
            self.assertEqual(1,1)
        
    @testFunction.test_function
    def testExistingLocalFileS2Muscate(self):
        import os
        product = "/home/akynos/MAJA/inputs/L1/31TCH_MUSCATE/SENTINEL2B_20171008-105012-463_L1C_T31TCH_C_V1-0"
        srtm = "/home/akynos/MAJA/DTM/Creation/SRTM"
        water = "/home/akynos/MAJA/DTM/Creation/Water"
        if(os.path.exists(product)):
            self.logger.info("Found existing product")
            c = DTMCreation.DTMCreator(dirProduct=product, kml=None, granuleID=None, dirSRTM=srtm, dirWater=water)
            self.assertTrue(c.isMuscateProduct(product))
            mission, mtd, mtype = c.findMetadataFile(product)
            self.assertEqual(mission, c.s2Mission)
            self.assertTrue(os.path.exists(mtd))
        else:
            self.logger.warning("WARNING: Did not find existing product")
            self.assertEqual(1,1)
        
    @testFunction.test_function
    def testGetSiteInfoNative(self):
        product = "/home/akynos/MAJA/inputs/L1/29RPQ/S2A_MSIL1C_20180706T110621_N0206_R137_T29RPQ_20180706T132942.SAFE/"
        srtm = "/home/akynos/MAJA/DTM/Creation/SRTM"
        water = "/home/akynos/MAJA/DTM/Creation/Water"
        c = DTMCreation.DTMCreator(dirProduct=product, kml=None, granuleID=None, dirSRTM=srtm, dirWater=water)
        mission, mtd, mtype = c.findMetadataFile(product)
        site = c.getSiteInfo(mtd, mtype)
        self.assertEqual(site.nom, "29RPQ")
        self.assertEqual(site.EPSG_out, 32629)
        self.assertEqual(site.marge, 0)
        self.assertEqual(site.orig_x, 600000)
        self.assertEqual(site.orig_y, 3500040)
        self.assertEqual(site.pas_x, 109800)
        self.assertEqual(site.pas_y, 109800)
        self.assertEqual(site.proj, "UTM29N")
        self.assertEqual(site.tx_max, 0)
        self.assertEqual(site.tx_min, 0)
        self.assertEqual(site.ty_max, 0)
        self.assertEqual(site.ty_min, 0)

    @testFunction.test_function
    def testGetSiteInfoMuscate(self):
        product = "/home/akynos/MAJA/inputs/L1/31TCH/SENTINEL2B_20171008-105012-463_L1C_T31TCH_C_V1-0"
        srtm = "/home/akynos/MAJA/DTM/Creation/SRTM"
        water = "/home/akynos/MAJA/DTM/Creation/Water"
        c = DTMCreation.DTMCreator(dirProduct=product, kml=None, granuleID=None, dirSRTM=srtm, dirWater=water)
        mission, mtd, mtype = c.findMetadataFile(product)
        site = c.getSiteInfo(mtd, mtype)
        self.assertEqual(site.nom, "31TCH")
        self.assertEqual(site.EPSG_out, 32631)
        self.assertEqual(site.marge, 0)
        self.assertEqual(site.orig_x, 300000)
        self.assertEqual(site.orig_y, 4800000)
        self.assertEqual(site.pas_x, 109800)
        self.assertEqual(site.pas_y, 109800)
        self.assertEqual(site.proj, "UTM31N")
        self.assertEqual(site.tx_max, 0)
        self.assertEqual(site.tx_min, 0)
        self.assertEqual(site.ty_max, 0)
        self.assertEqual(site.ty_min, 0)
    
    @testFunction.test_function
    def testGetSiteInfoKML(self):
        import os
        from Common import FileSystem
        kml = "/home/akynos/Downloads/S2A_OPER_GIP_TILPAR_MPC__20151209T095117_V20150622T000000_21000101T000000_B00.kml"
        granule = "29RPQ"
        srtm = "/home/akynos/MAJA/DTM/Creation/SRTM"
        water = "/home/akynos/MAJA/DTM/Creation/Water"
        c = DTMCreation.DTMCreator(dirProduct=None, kml=kml, granuleID=granule, dirSRTM=srtm, dirWater=water)
        testOut = os.path.join(os.getcwd(),"testGetSiteInfoKML")
        c.run(outdir=testOut, tempout=None)
        site = c.site
        self.assertEqual(site.nom, "29RPQ")
        self.assertEqual(site.EPSG_out, 32629)
        self.assertEqual(site.marge, 0)
        self.assertEqual(site.orig_x, 600000)
        self.assertEqual(site.orig_y, 3500040)
        self.assertEqual(site.pas_x, 109800)
        self.assertEqual(site.pas_y, 109800)
        self.assertEqual(site.proj, "UTM29N")
        self.assertEqual(site.tx_max, 0)
        self.assertEqual(site.tx_min, 0)
        self.assertEqual(site.ty_max, 0)
        self.assertEqual(site.ty_min, 0)
        self.assertTrue(os.path.exists(testOut))
        self.assertTrue(os.path.exists(os.path.join(testOut, "S2__TEST_AUX_REFDE2_T29RPQ_0001", "S2__TEST_AUX_REFDE2_T29RPQ_0001.HDR")))
        self.assertTrue(os.path.exists(os.path.join(testOut, "S2__TEST_AUX_REFDE2_T29RPQ_0001", "S2__TEST_AUX_REFDE2_T29RPQ_0001.DBL.DIR")))
        self.assertTrue(os.path.exists(os.path.join(testOut, "S2__TEST_AUX_REFDE2_T29RPQ_0001", "S2__TEST_AUX_REFDE2_T29RPQ_0001.DBL.DIR", "S2__TEST_AUX_REFDE2_T29RPQ_0001_ALC.TIF")))
        self.assertTrue(os.path.exists(os.path.join(testOut, "S2__TEST_AUX_REFDE2_T29RPQ_0001", "S2__TEST_AUX_REFDE2_T29RPQ_0001.DBL.DIR", "S2__TEST_AUX_REFDE2_T29RPQ_0001_ALT_R1.TIF")))
        self.assertTrue(os.path.exists(os.path.join(testOut, "S2__TEST_AUX_REFDE2_T29RPQ_0001", "S2__TEST_AUX_REFDE2_T29RPQ_0001.DBL.DIR", "S2__TEST_AUX_REFDE2_T29RPQ_0001_ALT_R2.TIF")))
        self.assertTrue(os.path.exists(os.path.join(testOut, "S2__TEST_AUX_REFDE2_T29RPQ_0001", "S2__TEST_AUX_REFDE2_T29RPQ_0001.DBL.DIR", "S2__TEST_AUX_REFDE2_T29RPQ_0001_ASC.TIF")))
        self.assertTrue(os.path.exists(os.path.join(testOut, "S2__TEST_AUX_REFDE2_T29RPQ_0001", "S2__TEST_AUX_REFDE2_T29RPQ_0001.DBL.DIR", "S2__TEST_AUX_REFDE2_T29RPQ_0001_ASP_R1.TIF")))
        self.assertTrue(os.path.exists(os.path.join(testOut, "S2__TEST_AUX_REFDE2_T29RPQ_0001", "S2__TEST_AUX_REFDE2_T29RPQ_0001.DBL.DIR", "S2__TEST_AUX_REFDE2_T29RPQ_0001_ASP_R2.TIF")))
        self.assertTrue(os.path.exists(os.path.join(testOut, "S2__TEST_AUX_REFDE2_T29RPQ_0001", "S2__TEST_AUX_REFDE2_T29RPQ_0001.DBL.DIR", "S2__TEST_AUX_REFDE2_T29RPQ_0001_MSK.TIF")))
        self.assertTrue(os.path.exists(os.path.join(testOut, "S2__TEST_AUX_REFDE2_T29RPQ_0001", "S2__TEST_AUX_REFDE2_T29RPQ_0001.DBL.DIR", "S2__TEST_AUX_REFDE2_T29RPQ_0001_SLC.TIF")))
        self.assertTrue(os.path.exists(os.path.join(testOut, "S2__TEST_AUX_REFDE2_T29RPQ_0001", "S2__TEST_AUX_REFDE2_T29RPQ_0001.DBL.DIR", "S2__TEST_AUX_REFDE2_T29RPQ_0001_SLP_R1.TIF")))
        self.assertTrue(os.path.exists(os.path.join(testOut, "S2__TEST_AUX_REFDE2_T29RPQ_0001", "S2__TEST_AUX_REFDE2_T29RPQ_0001.DBL.DIR", "S2__TEST_AUX_REFDE2_T29RPQ_0001_SLP_R2.TIF")))
        self.assertEqual(FileSystem.removeDirectory(testOut), 0)