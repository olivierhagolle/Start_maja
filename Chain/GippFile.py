#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Copyright (C) CNES - All Rights Reserved
This file is subject to the terms and conditions defined in
file 'LICENSE.md', which is part of this source code package.

Author:         Peter KETTIG <peter.kettig@cnes.fr>
Project:        Start_maja, CNES
"""

from os import path as p
from Chain.AuxFile import EarthExplorer


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
    url = "http://tully.ups-tlse.fr/olivier/gipp_maja/repository/archive.zip?ref=master"
    zenodo_reg = r"https://zenodo.org/record/\d+/files/\w+.tgz?download=1"

    platforms = ["sentinel2", "landsat8", "venus"]
    gtypes = ["muscate", "natif", "tm"]

    def __init__(self, root, platform, gtype, cams=False):
        """
        Set the path to the root gipp folder
        :param root: The full path to the root gipp folder
        :param platform: The platform name
        :param gtype: The gipp type
        """
        from Common import FileSystem
        assert platform in self.platforms
        assert gtype in self.gtypes
        self.fpath = p.realpath(root)
        FileSystem.create_directory(self.fpath)
        self.gipp_archive = p.join(self.fpath, "archive.zip")
        self.lut_archive = p.join(self.fpath, "lut_archive.zip")
        self.temp_folder = p.join(self.fpath, "tempdir")

        self.platform = platform
        self.gtype = gtype
        self.cams = "_CAMS" if cams else ""
        self.gipp_folder_name = "%s_%s" % (self.platform, self.gtype) + self.cams

    def download(self):
        """
        Download a specific set of Gipps to the given folder.
        First, attempt to download the most recent git archive containing the .EEF files as well as the
        url to download the LUTs. Then, the latter will be downloaded separately.
        :return:
        """
        import os
        from Common import FileSystem
        FileSystem.download_file(self.url, self.archive)
        FileSystem.unzip(self.archive, self.temp_folder)
        gipp_maja_git = p.join(self.fpath, "gipp_maja.git")
        platform_folder = FileSystem.get_file(root=gipp_maja_git, filename=self.gipp_folder_name)
        if not platform_folder:
            raise OSError("Cannot find any gipp folder for platform %s" % self.gipp_folder_name)
        readme = FileSystem.get_file(filename="download.md", root=platform_folder)
        if not readme:
            raise OSError("Cannot find download-file for LUT-Download in %s" % platform_folder)
        lut_url = FileSystem.find_in_file(readme, self.zenodo_reg)
        if not lut_url:
            raise OSError("Cannot find url to download LUTs")
        FileSystem.download_file(lut_url, self.lut_archive)
        FileSystem.unzip(self.lut_archive, self.temp_folder)
        lut_folder = FileSystem.get_file(root=self.temp_folder, filename="LUTs")
        if not lut_folder:
            raise OSError("Cannot find 'LUTs' folder in %s" % self.temp_folder)

        eefs = FileSystem.find("*(EEF|HDR)", self.temp_folder)
        dbls = FileSystem.find("*DBL.DIR", self.temp_folder)
        for gipp_file in eefs + dbls:
            base = p.basename(gipp_file)
            os.rename(gipp_file, p.join(self.fpath, base))

        FileSystem.remove_directory(self.temp_folder)
        FileSystem.remove_file(self.lut_archive)
        FileSystem.remove_file(self.gipp_archive)
