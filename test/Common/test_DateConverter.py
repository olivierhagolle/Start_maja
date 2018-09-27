# -*- coding: utf-8 -*-

from Unittest import LoggedTestCase
from Unittest import testFunction
from Common import DateConverter

class testDateConverter(LoggedTestCase.LoggedTestCase):

    @testFunction.test_function
    def testDateConversionShort(self):
       orig = "20180522"
       origAsDT = DateConverter.stringToDatetime(orig)
       self.assertEqual(DateConverter.datetimeToStringShort(origAsDT), orig)
       self.assertEqual(DateConverter.datetimeToString(origAsDT),
                        "2018-05-22T00:00:00.000Z")
       
    @testFunction.test_function
    def testDateConversionLong(self):
       orig = "2018-05-22T00:00:00.000Z"
       origAsDT = DateConverter.stringToDatetime(orig)
       self.assertEqual(DateConverter.datetimeToStringShort(origAsDT), "20180522")
       self.assertEqual(DateConverter.datetimeToString(origAsDT),
                        orig)
       