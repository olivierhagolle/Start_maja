#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Jul  5 17:42:44 2018

@author: akynos
"""

import logging


def touch(path):
    """
    Create a new dummy-file of given path
    :param path: The full path to the file
    :return:
    """
    import os
    with open(path, 'a'):
        os.utime(path, None)


def test_function(func):
    """
    Decorator to print the name of the function for debug purposes
    """
    def echo_func(*func_args, **func_kwargs):

        logging.debug("==={0:=^30}===".format(func.__name__))
        func(*func_args, **func_kwargs)

        logging.debug("====================================")

    return echo_func
