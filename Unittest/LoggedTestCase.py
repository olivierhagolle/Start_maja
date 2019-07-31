# -*- coding: utf-8 -*-

import unittest
import logging


class LogThisTestCase(type):
    def __new__(cls, name, bases, dct):
        # if the TestCase already provides setUp, wrap it
        if 'setUp' in dct:
            setUp = dct['setUp']
        else:
            setUp = lambda self: None

        def wrappedSetUp(self):
            self.logger = logging.getLogger()
            self.handler = logging.StreamHandler()
            self.logger.addHandler(self.handler)
            self.logger.setLevel(logging.DEBUG)
            setUp(self)
        dct['setUp'] = wrappedSetUp

        # same for tearDown
        if 'tearDown' in dct:
            tearDown = dct['tearDown']
        else:
            tearDown = lambda self: None

        def wrappedTearDown(self):
            tearDown(self)
            self.logger.removeHandler(self.handler)
        dct['tearDown'] = wrappedTearDown

        # return the class instance with the replaced setUp/tearDown
        return type.__new__(cls, name, bases, dct)


class LoggedTestCase(unittest.TestCase):
    __metaclass__ = LogThisTestCase
    logger = logging.getLogger("unittestLogger")
    logger.setLevel(logging.DEBUG) # or whatever you prefer
