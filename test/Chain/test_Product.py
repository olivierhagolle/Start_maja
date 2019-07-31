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
    Create a new file within the path
    :param path:
    :return:
    """
    with open(path, 'a'):
        os.utime(path, None)


class TestL8Product(LoggedTestCase.LoggedTestCase):
    root = "./test_filesystem"
    subdir_prefix = "subdir"
    file_a1 = "a"
    file_a2 = "a.jpg"
    file_b1 = "b.jpg"
    file_c1 = "c.xml"

    def setUp(self):
        os.makedirs(self.root)
        subdir = p.join(self.root, self.subdir_prefix)
        os.makedirs(subdir)

        touch(p.join(self.root, self.file_a1))
        touch(p.join(self.root, self.file_a2))
        touch(p.join(self.root, self.file_b1))
        touch(p.join(self.root, self.file_c1))
        touch(p.join(subdir, self.file_a1))
        touch(p.join(subdir, self.file_a2))
        touch(p.join(subdir, self.file_b1))
        touch(p.join(subdir, self.file_c1))

    def tearDown(self):
        import shutil
        shutil.rmtree(self.root)

    @testFunction.test_function
    def test_get_file(self):
        pass