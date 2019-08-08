# -*- coding: utf-8 -*-

import unittest
from Common import DateConverter


class TestDateConverter(unittest.TestCase):

    def testDateConversionShort(self):
       orig = "20180522"
       origAsDT = DateConverter.stringToDatetime(orig)
       self.assertEqual(DateConverter.datetimeToStringShort(origAsDT), orig)
       self.assertEqual(DateConverter.datetimeToString(origAsDT),
                        "2018-05-22T00:00:00.000Z")
       
    def testDateConversionLong(self):
       orig = "2018-05-22T00:00:00.000Z"
       origAsDT = DateConverter.stringToDatetime(orig)
       self.assertEqual(DateConverter.datetimeToStringShort(origAsDT), "20180522")
       self.assertEqual(DateConverter.datetimeToString(origAsDT),
                        orig)
       
    def test_PlatformDates(self):
        from Common import DateConverter as dc
        s2 = [(["S2A_MSIL1C_20170412T110621_N0204_R137_T29RPQ_20170412T111708.SAFE", 0], 0),
              (["SENTINEL2B_20171008-105012-463_L1C_T31TCH_C_V1-0", 1], 0),
              (["S2B_MSIL1C_20180316T103021_N0206_R108_T32TMR_20180316T123927.SAFE", 0], 0)]
        datesS2 = ["20170412", "20171008", "20180316"]
        l8 = [(["LANDSAT8-OLITIRS-XSTHPAN_20170501-103532-111_L1C_T31TCH_C_V1-0",2], 1),
              (["LC80390222013076EDC00", 1], 1),
              (["LC08_L1TP_199029_20170527_20170615_01_T1", 0], 1)]
        datesL8 = ["20170501", "20130317", "20170527", "20130626"]
        vns = [(["VENUS-XS_20180201-051359-000_L1C_KHUMBU_C_V1-0", 0], 2),
               (["VE_VM01_VSC_L2VALD_ISRAW906_20180317.HDR", 1], 2),
               (["VE_TEST_VSC_L1VALD_CAMARGUE_20120101.HDR", 1], 2)]
        datesVns = ["20180201", "20180317", "20120101"]
        for (prod, platform), date in zip(s2, datesS2):
            d = dc.datetimeToStringShort(dc.getDateFromProduct(prod, platform))
            self.assertEqual(date, d)
        for (prod, platform), date in zip(l8, datesL8):
            d = dc.datetimeToStringShort(dc.getDateFromProduct(prod, platform))
            self.assertEqual(date, d)
        for (prod, platform), date in zip(vns, datesVns):
            d = dc.datetimeToStringShort(dc.getDateFromProduct(prod, platform))
            self.assertEqual(date, d)


if __name__ == '__main__':
    unittest.main()

