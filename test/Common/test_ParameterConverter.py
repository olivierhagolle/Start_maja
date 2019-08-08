# -*- coding: utf-8 -*-


import unittest
from Common import ParameterConverter


class TestParameterConverter(unittest.TestCase):

    def testParameterConversion(self):
        orig = ["1", "0", "True", "False"]
        converted = [True, False, True, False]
        for param, res in zip(orig, converted):
            self.assertEqual(ParameterConverter.str2bool(param), res)


if __name__ == '__main__':
    unittest.main()
