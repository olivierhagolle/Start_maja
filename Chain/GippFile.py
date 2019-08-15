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
import logging
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
    zenodo_reg = r"https?:\/\/zenodo.org\/record\/\d+\/files\/\w+.zip\?download=1"

    platforms = ["sentinel2", "landsat8", "venus"]
    gtypes = ["muscate", "natif", "tm"]

    def __init__(self, root, platform, gtype, cams=False, log_level=logging.INFO):
        """
        Set the path to the root gipp folder
        :param root: The full path to the root gipp folder
        :param platform: The platform name. Has to be in ["sentinel2", "landsat8", "venus"]
        :param gtype: The gipp type. Has to be in ["muscate", "natif", "tm"]
        :param cams: Build GIPP with CAMS models
        :param log_level: The log level for the messages displayed.
        """
        from Common import FileSystem
        assert platform in self.platforms
        assert gtype in self.gtypes
        self.fpath = os.path.realpath(root)
        FileSystem.create_directory(self.fpath)
        self.gipp_archive = os.path.join(self.fpath, "archive.zip")
        self.lut_archive = os.path.join(self.fpath, "lut_archive.zip")
        self.temp_folder = os.path.join(self.fpath, "tempdir")

        self.platform = platform
        self.gtype = gtype
        self.cams = "_CAMS" if cams else ""
        self.log_level = log_level

        # Create folder names:
        self.gipp_folder_name = "%s_%s" % (self.platform.upper(), self.gtype.upper()) + self.cams
        self.out_path = os.path.join(self.fpath, self.gipp_folder_name)

    def __clean_up(self):
        """
        Clean up the download directory.
        :return:
        """
        from Common import FileSystem
        FileSystem.remove_directory(self.temp_folder)
        FileSystem.remove_file(self.lut_archive)
        FileSystem.remove_file(self.gipp_archive)

    def download(self):
        """
        Download a specific set of Gipps to the given folder.
        First, attempt to download the most recent git archive containing the .EEF files as well as the
        url to download the LUTs. Then, the latter will be downloaded separately.
        :return:
        """
        import shutil
        from Common import FileSystem
        FileSystem.download_file(self.url, self.gipp_archive, self.log_level)
        FileSystem.unzip(self.gipp_archive, self.temp_folder)
        gipp_maja_git = os.path.join(self.temp_folder, "gipp_maja.git")
        platform_folder = FileSystem.get_file(root=gipp_maja_git, filename=self.gipp_folder_name)
        if not platform_folder:
            self.__clean_up()
            raise OSError("Cannot find any gipp folder for platform %s" % self.gipp_folder_name)
        readme = FileSystem.get_file(filename="readme*", root=platform_folder)
        if not readme:
            self.__clean_up()
            raise OSError("Cannot find download-file for LUT-Download in %s" % platform_folder)
        lut_url = FileSystem.find_in_file(readme, self.zenodo_reg)
        if not lut_url:
            self.__clean_up()
            raise OSError("Cannot find url to download LUTs")
        FileSystem.download_file(lut_url, self.lut_archive, self.log_level)
        FileSystem.unzip(self.lut_archive, platform_folder)
        lut_folder = FileSystem.get_file(root=platform_folder, filename="LUTs")
        if not lut_folder:
            self.__clean_up()
            raise OSError("Cannot find 'LUTs' folder in %s" % self.temp_folder)
        for f in os.listdir(lut_folder):
            shutil.move(os.path.join(lut_folder, f), platform_folder)
        FileSystem.remove_directory(lut_folder)
        if os.path.isdir(self.out_path):
            FileSystem.remove_directory(self.out_path)
        shutil.move(platform_folder, self.out_path)
        self.__clean_up()

    def link(self, dest):
        """
        Symlink a set of Gipps to a given destination
        :param dest: The destination directory
        :return:
        """
        from Common import FileSystem
        eefs = FileSystem.find("*.(EEF|HDR)", self.out_path)
        dbls = FileSystem.find("*.DBL.DIR", self.out_path)
        for f in eefs + dbls:
            base = os.path.basename(f)
            FileSystem.symlink(f, os.path.join(dest, base))

    def check_completeness(self):
        # TODO Need to implement this using good ol' regex's.
        raise NotImplementedError
