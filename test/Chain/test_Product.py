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
from Chain.Product import MajaProduct
import os
from os import path as p


def touch(path):
    """
    Create a new dummy-file of given path
    :param path: The full path to the file
    :return:
    """
    with open(path, 'a'):
        os.utime(path, None)


class TestProduct(LoggedTestCase.LoggedTestCase):
    root = "S2A_MSIL1C_20170412T110621_N0204_R137_T29RPQ_20170412T111708.SAFE"

    subdir_prefix = "subdir"
    file_a1 = "a"
    file_a2 = "a.jpg"
    file_b1 = "b.jpg"
    file_c1 = "c.xml"

    def setUp(self):
        """
        Sets up a random tree-like structure with a few sub-files and -folders
        :return:
        """
        os.makedirs(self.root)
        touch(p.join(self.root, self.file_a1))
        touch(p.join(self.root, self.file_a2))
        touch(p.join(self.root, self.file_b1))
        touch(p.join(self.root, self.file_c1))
        for i in range(2):
            subdir = p.join(self.root, self.subdir_prefix + str(i))
            os.makedirs(subdir)
            touch(p.join(subdir, self.file_a1))
            touch(p.join(subdir, self.file_a2))
            touch(p.join(subdir, self.file_b1))
            touch(p.join(subdir, self.file_c1))
            for j in range(2):
                ssubdir = p.join(subdir, self.subdir_prefix + str(j))
                os.makedirs(ssubdir)
                touch(p.join(ssubdir, self.file_a1))
                touch(p.join(ssubdir, self.file_a2))
                touch(p.join(ssubdir, self.file_b1))
                touch(p.join(ssubdir, self.file_c1))

    def tearDown(self):
        import shutil
        shutil.rmtree(self.root)

    @testFunction.test_function
    def test_get_file_depth1(self):
        product = MajaProduct(self.root).factory()
        expected = "S2A_MSIL1C_20170412T110621_N0204_R137_T29RPQ_20170412T111708.SAFE/a"
        self.assertEqual(expected, product.get_file(filename="^a$"))

    @testFunction.test_function
    def test_get_file_depth2(self):
        product = MajaProduct(self.root).factory()
        expected = r"S2A_MSIL1C_20170412T110621_N0204_R137_T29RPQ_20170412T111708.SAFE/subdir0/a"
        dirname = p.dirname(expected)[:-1]
        filename = p.basename(expected)
        calculated = product.get_file(folders="subdir*", filename="^a$")
        self.assertEqual(dirname, p.dirname(calculated)[:-1])
        self.assertEqual(filename, p.basename(calculated))

    @testFunction.test_function
    def test_get_file_depth3(self):
        product = MajaProduct(self.root).factory()
        expected = "S2A_MSIL1C_20170412T110621_N0204_R137_T29RPQ_20170412T111708.SAFE/subdir0/subdir1/c.xml"
        dirnames_e = p.normpath(expected).split(os.sep)
        filename = p.basename(expected)
        calculated = product.get_file(folders="subdir*/subdir*", filename="*xml")
        dirnames_c = p.normpath(calculated).split(os.sep)
        for exp, calc in zip(dirnames_c, dirnames_e):
            self.assertEqual(exp[:-1], calc[:-1])
        self.assertEqual(filename, p.basename(calculated))

    @testFunction.test_function
    def test_get_file_ending(self):
        product = MajaProduct(self.root).factory()
        expected = "S2A_MSIL1C_20170412T110621_N0204_R137_T29RPQ_20170412T111708.SAFE/c.xml"
        self.assertEqual(expected, product.get_file(filename="./*xml"))

    @testFunction.test_function
    def test_get_file_full(self):
        product = MajaProduct(self.root).factory()
        expected = "S2A_MSIL1C_20170412T110621_N0204_R137_T29RPQ_20170412T111708.SAFE/b.jpg"
        self.assertEqual(expected, product.get_file(folders="./", filename="b.jpg"))
