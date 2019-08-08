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
        from Common import FileSystem

        if not os.path.isdir(dbl):
            return None
        reg = cls.regex if regex is None else regex
        if not re.search(reg, os.path.basename(dbl)):
            return None
        cls.dbl = dbl
        cls.base = os.path.basename(dbl).split(".")[0]
        # Find associated HDR
        cls.hdr = FileSystem.get_file(root=os.path.join(dbl, "../"), filename=cls.base + ".HDR")
        assert os.path.isfile(cls.hdr)
        return object.__new__(cls)

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


class GIPPFile(EarthExplorer):
    regex = r"\w+_" \
            r"(TEST|PROD)_" \
            r"GIP_" \
            r"(L2ALBD|L2DIFT|L2DIRT|L2TOCR|L2WATV|L2COMM|L2SITE|L2SMAC|CKEXTL|CKQLTL)_" \
            r"\w_\w+_\d{5}_\d{8}_\d{8}\.\w+"

    regex_albd = r"\w+_(TEST|PROD)_GIP_L2ALBD_\w_\w+_\d{5}_\d{8}_\d{8}\.\w+"
    regex_dift = r"\w+_(TEST|PROD)_GIP_L2DIFT_\w_\w+_\d{5}_\d{8}_\d{8}\.\w+"
    regex_dirt = r"\w+_(TEST|PROD)_GIP_L2DIRT_\w_\w+_\d{5}_\d{8}_\d{8}\.\w+"
    regex_tocr = r"\w+_(TEST|PROD)_GIP_L2TOCR_\w_\w+_\d{5}_\d{8}_\d{8}\.\w+"
    regex_watv = r"\w+_(TEST|PROD)_GIP_L2WATV_\w_\w+_\d{5}_\d{8}_\d{8}\.\w+"
    regex_comm = r"\w+_(TEST|PROD)_GIP_L2COMM_\w_\w+_\d{5}_\d{8}_\d{8}\.\w+"
    regex_site = r"\w+_(TEST|PROD)_GIP_L2SITE_\w_\w+_\d{5}_\d{8}_\d{8}\.\w+"
    regex_smac = r"\w+_(TEST|PROD)_GIP_L2SMAC_\w_\w+_\d{5}_\d{8}_\d{8}\.\w+"
    regex_extl = r"\w+_(TEST|PROD)_GIP_CKEXTL_\w_\w+_\d{5}_\d{8}_\d{8}\.\w+"
    regex_qltl = r"\w+_(TEST|PROD)_GIP_CKQLTL_\w_\w+_\d{5}_\d{8}_\d{8}\.\w+"

    all_regexes = [regex_albd, regex_dift, regex_dirt,
                   regex_tocr, regex_watv, regex_comm,
                   regex_site, regex_smac, regex_extl,
                   regex_qltl]