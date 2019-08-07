#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Copyright (C) CNES - All Rights Reserved
This file is subject to the terms and conditions defined in
file 'LICENSE.md', which is part of this source code package.

Author:         Peter KETTIG <peter.kettig@cnes.fr>
Project:        Start_maja, CNES
"""

import os
import re


class EarthExplorer(object):
    """
    Class to store an auxiliary EarthExplorer file
    """

    regex = r"^[\w-]+.DBL.DIR$"

    def __new__(cls, dbl):
        """
        Instantiate a new EarthExplorer file
        :param dbl: A folder name
        :return:
        """
        from Common import FileSystem

        if not os.path.isdir(dbl):
            return None
        print(cls.regex)
        print(dbl)
        if re.search(os.path.basename(dbl), cls.regex):
            print("NoPAss")
            return None
        print("Pass")
        cls.dbl = dbl
        cls.base = os.path.basename(dbl).split(".")[0]
        # Find associated HDR
        cls.hdr = FileSystem.get_file(root=os.path.join(dbl, "../"), filename=cls.base + ".HDR")
        assert os.path.isfile(cls.hdr)
        return object.__new__(cls)

    def link(self, dest):
        """
        Symlink a file to the working dir without copying it
        :param dest: The destination folder
        :return:
        """
        os.symlink(self.hdr, dest)
        os.symlink(self.dbl, dest)


class CAMSFile(EarthExplorer):
    """
    Stores a single CAMS file
    """
    regex = r"\w{3}_(TEST|PROD)_EXO_CAMS_\w+"

    @classmethod
    def check_regex(cls, dbl):
        return re.search(cls.regex, dbl)

    def get_date(self):
        from datetime import datetime
        base = os.path.splitext(os.path.basename(self.hdr))[0]
        return datetime.strptime(base.split("_")[-2], "%Y%m%dT%H%M%S")

    def get_end_date(self):
        from datetime import datetime
        base = os.path.splitext(os.path.basename(self.hdr))[0]
        return datetime.strptime(base.split("_")[-1], "%Y%m%dT%H%M%S")


class DTMFile(EarthExplorer):
    """
    Stores a single DTM
    """
    regex = r"\w*_(TEST|PROD)_AUX_REFDE2_\w+"

