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

    regex = r"^[\w-]+.\w+"

    # TODO Add platform detection

    def __new__(cls, dbl, regex=None):
        """
        Instantiate a new EarthExplorer file
        :param dbl: A folder name
        :return:
        """

        if not os.path.isdir(dbl):
            return None
        reg = cls.regex if regex is None else regex
        if not re.search(reg, os.path.basename(dbl)):
            return None
        return object.__new__(cls)

    def __init__(self, dbl, regex=None):
        from Common import FileSystem
        self.regex = self.regex if regex is None else regex
        self.dbl = dbl
        self.base = os.path.basename(dbl).split(".")[0]
        # Find associated HDR
        self.hdr = FileSystem.get_file(root=os.path.join(dbl, "../"), filename=self.base + ".HDR")
        assert os.path.isfile(self.hdr)

    def __str__(self):
        return "\n".join(["DBL: " + self.dbl,
                          "HDR: " + self.hdr])

    def __repr__(self):
        return self.__str__()

    @classmethod
    def get_specifiable_regex(cls):
        return cls.regex[:-3]

    def link(self, dest):
        """
        Symlink a file to the working dir without copying it
        :param dest: The destination folder
        :return:
        """
        from Common import FileSystem
        FileSystem.symlink(self.hdr, os.path.join(dest, os.path.basename(self.hdr)))
        FileSystem.symlink(self.dbl, os.path.join(dest, os.path.basename(self.dbl)))


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


class GIPPFile(EarthExplorer):
    regex = r"\w+_" \
            r"(TEST|PROD)_" \
            r"GIP_" \
            r"(L2ALBD|L2DIFT|L2DIRT|L2TOCR|L2WATV|L2COMM|L2SITE|L2SMAC|CKEXTL|CKQLTL)_" \
            r"\w_\w+_\d{5}_\d{8}_\d{8}\.\w+"

    def get_mission(self):
        """
        Return the "Mission" field for a single GIPP file.
        :return:
        """
        ns = {"xmlns": "http://eop-cfi.esa.int/CFI"}
        from xml.etree import ElementTree
        root = ElementTree.parse(self.hdr).getroot()
        xpath = "./xmlns:Fixed_Header/xmlns:Mission"
        return root.find(xpath, namespace=ns).text


class GippALBD(EarthExplorer):
    regex = r"\w+_(TEST|PROD)_GIP_L2ALBD_\w_\w+_\d{5}_\d{8}_\d{8}\.\w+"


class GippDIFT(EarthExplorer):
    regex = r"\w+_(TEST|PROD)_GIP_L2DIFT_\w_\w+_\d{5}_\d{8}_\d{8}\.\w+"


class GippDIRT(EarthExplorer):
    regex = r"\w+_(TEST|PROD)_GIP_L2DIRT_\w_\w+_\d{5}_\d{8}_\d{8}\.\w+"


class GippTOCR(EarthExplorer):
    regex = r"\w+_(TEST|PROD)_GIP_L2TOCR_\w_\w+_\d{5}_\d{8}_\d{8}\.\w+"


class GippWATV(EarthExplorer):
    regex = r"\w+_(TEST|PROD)_GIP_L2WATV_\w_\w+_\d{5}_\d{8}_\d{8}\.\w+"


class GippCOMM(EarthExplorer):
    regex = r"\w+_(TEST|PROD)_GIP_L2COMM_\w_\w+_\d{5}_\d{8}_\d{8}\.\w+"


class GippSITE(EarthExplorer):
    regex = r"\w+_(TEST|PROD)_GIP_L2SITE_\w_\w+_\d{5}_\d{8}_\d{8}\.\w+"


class GippSMAC(EarthExplorer):
    regex = r"\w+_(TEST|PROD)_GIP_L2SMAC_\w_\w+_\d{5}_\d{8}_\d{8}\.\w+"


class GippEXTL(EarthExplorer):
    regex = r"\w+_(TEST|PROD)_GIP_L2EXTL_\w_\w+_\d{5}_\d{8}_\d{8}\.\w+"


class GippQLTL(EarthExplorer):
    regex = r"\w+_(TEST|PROD)_GIP_L2QLTL_\w_\w+_\d{5}_\d{8}_\d{8}\.\w+"


class GippSet(object):
    """
    Stores a set of Gipp Files
    """
    def __init__(self, filepath):
        """
        Set the path to the root gipp folder
        :param filepath: The full path to the root gipp folder
        """
        from os import path as p
        self.fpath = p.realpath(filepath)

    def factory(self):
        pass

    def get_platform(self):
        raise NotImplementedError

    def get_type(self):
        raise NotImplementedError

    def get_file(self, **kwargs):
        from Common.FileSystem import get_file
        return get_file(root=self.fpath, **kwargs)

    def get_date(self):
        raise NotImplementedError


class GippMuscate(GippSet):
    """
    Store a set of 'muscate' gipps
    """
    pass