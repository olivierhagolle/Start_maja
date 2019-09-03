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
    reg_l8_lc2 = r"^LC08_L\w+$"
    reg_l8_mus = r"^LANDSAT8[\w-]*_[-\d]+_L(1C|2A)_T\d{2}[a-zA-Z]{3}_\w_V[\d-]+$"
    reg_l8_nat = r"^L8_\w{4}_L8C_L[12]VALD_[\d_]+.DBL.DIR$"
    reg_vs_mus = r"^VENUS(-XS)?_\d{8}-\d{6}-\d{3}_L(1C|2A|3A)_\w+_[DC]_V\d*-\d*$"
    reg_vs_nat = r"^VE_\w{4}_VSC_L[12]VALD_\w+.DBL.DIR$"
    reg_s5_mus = r"^SPOT5-HR\w+-XS_(\d{8})-\d{6}-\d{3}_L1C_\d{3}-\d{3}-\d_[DC]_V\d*-\d*$"
    reg_s4_mus = r"^SPOT4-HR\w+-XS_(\d{8})-\d{6}-\d{3}_L1C_\d{3}-\d{3}-\d_[DC]_V\d*-\d*$"
    reg_tile = r"T\d{2}[a-zA-Z]{3}"

    def __init__(self, filepath):
        """
        Set the path to the root product folder
        :param filepath: The full path to the root product folder
        """
        from os import path as p
        self.fpath = p.realpath(filepath)
        self.base = p.basename(self.fpath)
        
    def __str__(self):
        return "\n".join(["Product:   " + self.base,
                          "Acq-Date:  " + self.get_date().strftime("%Y-%m-%d %H:%M:%S"),
                          "Platform:  " + self.get_platform(),
                          "Level:     " + self.get_level(),
                          "Tile/Site: " + self.get_tile(),
                          ""])

    def __repr__(self):
        return self.__str__()

    def factory(self):
        """
        Detect the underlying product
        :return:
        """
        import re
        from Chain.S2Product import Sentinel2SSC, Sentinel2Muscate, Sentinel2Natif
        from Chain.L8Product import Landsat8LC1, Landsat8LC2, Landsat8Muscate, Landsat8Natif
        from Chain.VSProduct import VenusNatif, VenusMuscate
        from Chain.SpotProduct import Spot4Muscate, Spot5Muscate
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
        # Spot
        if re.search(self.reg_s5_mus, self.base):
            return Spot5Muscate(self.fpath)
        if re.search(self.reg_s4_mus, self.base):
            return Spot4Muscate(self.fpath)
        pass

    def get_platform(self):
        raise NotImplementedError

    def get_tile(self):
        raise NotImplementedError

    def get_type(self):
        raise NotImplementedError

    def get_file(self, **kwargs):
        from Common.FileSystem import get_file
        return get_file(root=self.fpath, **kwargs)

    def get_metadata_file(self):
        raise NotImplementedError

    def get_level(self):
        raise NotImplementedError

    def get_date(self):
        raise NotImplementedError

    def is_valid(self):
        raise NotImplementedError

    def get_site(self):
        raise NotImplementedError

    def __lt__(self, other):
        return self.get_date() < other.get_date()

    def __eq__(self, other):
        return self.get_date() == other.get_date() and \
               self.get_level() == other.get_level() and \
               self.get_metadata_file() == other.get_metadata_file() and \
               self.get_tile() == other.get_tile() and \
               self.get_platform() == other.get_platform()
