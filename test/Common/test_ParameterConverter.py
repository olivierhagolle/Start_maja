# -*- coding: utf-8 -*-


from Unittest import LoggedTestCase
from Unittest import testFunction
from Common import ParameterConverter

class testParameterConverter(LoggedTestCase.LoggedTestCase):

    @testFunction.test_function
    def testParameterConversion(self):
       orig = ["1","0","True","False"]
       converted = [True, False, True, False]
       for param, res in zip(orig, converted):
           self.assertEqual(ParameterConverter.str2bool(param), res)