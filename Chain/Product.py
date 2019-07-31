#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Copyright (C) CNES - All Rights Reserved
This file is subject to the terms and conditions defined in
file 'LICENSE.md', which is part of this source code package.

Author:         Peter KETTIG <peter.kettig@cnes.fr>
Project:        Start_maja, CNES
Created on:     Sun Feb  3 17:15:00 2019
"""


class MajaProduct(object):
    """
    Class to store all necessary information for a single L1- or L2- product
    """
    reg_s2_nat = r"^S2[AB]_MSIL1C_\d+T\d+_N\d+_R\d+_T\d{2}[a-zA-Z]{3}\_\d+T\d+.SAFE$"
    reg_s2_mus = r"^SENTINEL2[ABX]_[-\d]+_L(1C|2A|3A)_T\d{2}[a-zA-Z]{3}_\w_V[\d-]+$"
    reg_s2_ssc = r"^S2[AB]_OPER_SSC_L[12]VALD_\d{2}[a-zA-Z]{3}_\w+.DBL.DIR"
    reg_s2_prd = r"^S2[AB]_OPER_PRD_MSIL1C_PDMC_\w+_R\d+_V\w+.SAFE$"
    reg_l8_lc1 = r"^LC8\w+$"
    reg_l8_lc2 = r"^LC08_L\w+"
    reg_l8_mus = r"^LANDSAT8[\w-]*_[-\d]+_L(1C|2A)_T\d{2}[a-zA-Z]{3}_\w_V[\d-]+$"
    reg_l8_nat = r"^L8_\w{4}_L8C_L[12]VALD_[\d_]+.DBL.DIR"
    reg_vs_mus = r"^VENUS(-XS)?_[-\d]+_L(1C|2A|3A)_\w+_\w_V\w+"
    reg_vs_nat = r"^VE_\w{4}_VSC_L[12]VALD_\w+.DBL.DIR"
    reg_tile = r"T\d{2}[a-zA-Z]{3}"

    def __init__(self, filepath):
        """
        Set the path to the root product folder
        :param filepath: The full path to the root product folder
        """
        from os import path as p
        self.fpath = p.realpath(filepath)
        self.base = p.basename(self.fpath)

    def factory(self):
        """
        Detect the underlying product
        :return:
        """
        import re
        from Chain.S2Product import Sentinel2SSC, Sentinel2Muscate, Sentinel2Natif
        from Chain.L8Product import Landsat8LC1, Landsat8LC2, Landsat8Muscate, Landsat8Natif
        from Chain.VSProduct import VenusNatif, VenusMuscate
        # Sentinel-2
        if re.search(self.reg_s2_nat, self.base):
            return Sentinel2Natif(self.fpath)
        if re.search(self.reg_s2_mus, self.base):
            return Sentinel2Muscate(self.fpath)
        if re.search(self.reg_s2_ssc, self.base):
            return Sentinel2SSC(self.fpath)
        # Landsat-8
        if re.search(self.reg_l8_nat, self.base):
            return Landsat8Natif(self.fpath)
        if re.search(self.reg_l8_mus, self.base):
            return Landsat8Muscate(self.fpath)
        if re.search(self.reg_l8_lc1, self.base):
            return Landsat8LC1(self.fpath)
        if re.search(self.reg_l8_lc2, self.base):
            return Landsat8LC2(self.fpath)
        # Venus
        if re.search(self.reg_vs_mus, self.base):
            return VenusMuscate(self.fpath)
        if re.search(self.reg_vs_nat, self.base):
            return VenusNatif(self.fpath)
        pass

    @staticmethod
    def __get_item(path, reg):
        """
        Find a specific file/folder within a directory
        :param path: The full path to the directory
        :param reg: The regex to be searched for
        :return: The full path to the file/folder
        """
        import re
        import os
        available_dirs = [f for f in os.listdir(path) if re.search(reg, f)]
        if not available_dirs:
            raise IOError("Cannot find %s in %s" % (reg, path))
        return os.path.join(path, available_dirs[0])

    def get_platform(self):
        raise NotImplementedError

    def get_tile(self):
        raise NotImplementedError

    def get_type(self):
        raise NotImplementedError

    def get_file(self, **kwargs):
        """
        Get a single file from inside the root directory by glob or regex.
        The file can have one of the following characteristics:
        - folders: Inside a (sub-)folder
        - filename: Filename with specific pattern
        Or a combination of the two
        :param kwargs: The folders and filename arguments
        :return: The full path to the file if found or OSError if not.
        """
        import os
        supported_params = {
            param
            for param in ("folders", "filename")
            if kwargs.get(param, None) is not None
        }
        search_folder = self.fpath
        for key in supported_params:
            # The function supports globbing, so replace the globs for regex-like ones
            parameter = os.path.normpath(kwargs[key]).replace("*", ".*")
            if key == "folders":
                subdirs = parameter.split(os.sep)
                # Recursively update the search folder for each sub folder
                for sub in subdirs:
                    if sub == ".":
                        continue
                    if sub == "..":
                        search_folder = os.path.dirname(search_folder)
                        continue
                    search_folder = self.__get_item(search_folder, sub)
            elif key == "filename":
                return self.__get_item(search_folder, parameter)
        raise IOError("Cannot find file with parameters:", kwargs)

    def get_metadata_file(self):
        raise NotImplementedError

    def get_level(self):
        raise NotImplementedError

    def get_date(self):
        raise NotImplementedError

