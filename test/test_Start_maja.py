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


class TestStartMaja(LoggedTestCase.LoggedTestCase):
    @testFunction.test_function
    def test_AuxRegexes(self):
        import re
        cams = ["S2__TEST_EXO_CAMS_20171008T030000_20180628T174612.HDR",
                "S2__TEST_EXO_CAMS_20171008T150000_20180628T174630.DBL.DIR",
                "S2__TEST_EXO_CAMS_20171010T030000_20180628T174724.DBL"]
        dtms = ["S2__TEST_AUX_REFDE2_T29RPQ_0001",
                "NONAME_TEST_AUX_REFDE2_TKHUMBU_0001"]
        gippVns = ["VE_TEST_GIP_L2ALBD_L_ALLSITES_00010_20000101_99991231.HDR",
                   "VE_TEST_GIP_L2DIFT_L_ALLSITES_00010_20000101_99991231.HDR",
                   "VE_TEST_GIP_CKEXTL_S_CAMARGUE_00005_00000000_99999999.EEF",
                   "VE_TEST_GIP_L2SMAC_S_ALLSITES_00010_00000000_99999999.EEF",
                   "VE_TEST_GIP_L2SITE_S_ALLSITES_00001_00000000_99999999.EEF",
                   "VE_TEST_GIP_L2TOCR_L_ALLSITES_00010_20000101_99991231.HDR",
                   "VE_TEST_GIP_L2DIRT_L_ALLSITES_00010_20000101_99991231.HDR",
                   "VE_TEST_GIP_L2COMM_L_ALLSITES_00001_20170801_99991231.EEF",
                   "VE_TEST_GIP_L2WATV_L_ALLSITES_00005_20000101_99991231.HDR",
                   "VE_TEST_GIP_CKQLTL_S_CAMARGUE_00002_00000000_99999999.EEF"]
        gippS2 = ["S2B_TEST_GIP_L2COMM_L_ALLSITES_10009_20150703_21000101.EEF",
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
        gippL8 = ["L8_TEST_GIP_L2COMM_L_ALLSITES_90001_00000000_99999999.EEF",
                  "L8_TEST_GIP_L2SITE_S_EU93056200A00B_90001_00000000_99999999.EEF",
                  "L8_TEST_GIP_CKQLTL_S_EU93056200A00B_90001_00000000_99999999.EEF",
                  "L8_TEST_GIP_L2DIFT_L_CONTINEN_90001_00000000_99999999.HDR",
                  "L8_TEST_GIP_CKEXTL_S_EU93056200A00B_90001_00000000_99999999.EEF",
                  "L8_TEST_GIP_L2DIRT_L_CONTINEN_90001_00000000_99999999.HDR",
                  "L8_TEST_GIP_L2TOCR_L_CONTINEN_90001_00000000_99999999.HDR",
                  "L8_TEST_GIP_L2ALBD_L_CONTINEN_90001_00000000_99999999.HDR",
                  "L8_TEST_GIP_L2SMAC_L_ALLSITES_90001_00000000_99999999.EEF"]
        for f in cams:
            self.assertTrue(re.search(StartMaja.regCAMS, f))
        for dtm in dtms:
            self.assertTrue(re.search(StartMaja.regDTM, dtm))
        for gipp in gippVns + gippS2 + gippL8:
            l = list(re.search(pattern, gipp) for pattern in StartMaja.regGIPP)
            self.assertFalse(all(v is None for v in l))
