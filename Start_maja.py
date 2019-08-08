#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Copyright (C) CNES - All Rights Reserved
This file is subject to the terms and conditions defined in
file 'LICENSE.md', which is part of this source code package.

Author:         Peter KETTIG <peter.kettig@cnes.fr>
Project:        Start_maja, CNES
Created on:     Tue Dec  4 09:26:05 2018
"""

import os
import sys
import re
import logging
from os import path as p
from datetime import timedelta

from Chain import Product
from Common import FileSystem
from Chain import AuxFile


class StartMaja(object):
    """
    Run the MAJA processor
    """
    version = "4.0.0rc1"
    date_regex = r"\d{4}-\d{2}-\d{2}"  # YYYY-MM-DD
    current_dir = p.dirname(p.realpath(__file__))

    def __init__(self, folder, tile, site, gipp, start, end, nbackward, overwrite, verbose):
        """
        Init the instance using the old start_maja parameters
        """
        from Common import DateConverter, ParameterConverter
        self.verbose = verbose
        logging_level = logging.DEBUG if ParameterConverter.str2bool(self.verbose) else logging.INFO
        self.__init_loggers(msg_level=logging_level)
        logging.info("=============This is Start_Maja v%s==============" % self.version)
        self.userconf = p.realpath(p.join(self.current_dir, "userconf"))
        if not p.isdir(self.userconf):
            raise OSError("Cannot find userconf folder: %s" % self.userconf)
        self.folder = p.realpath(folder)
        logging.debug("Checking config file: %s" % folder)
        if not p.isfile(self.folder):
            raise OSError("Cannot find folder definition file: %s" % self.folder)
        self.rep_work, self.rep_l1, self.rep_l2, self.rep_mnt, self.maja, self.rep_cams = self.parse_config(self.folder)
        logging.debug("Config file parsed without errors.")
        logging.debug("Checking GIPP files")
        self.gipp = p.realpath(gipp)
        if not p.isdir(self.gipp):
            raise OSError("Cannot find GIPP folder: %s" % self.gipp)
        for regGIPP in AuxFile.GIPPFile.all_regexes:
            if not [f for f in os.listdir(gipp) if re.search(regGIPP, f)]:
                raise OSError("Missing GIPP file: %s" % regGIPP)
        logging.debug("Found GIPP folder: %s" % gipp)
        
        if tile[0] == "T" and re.search(Product.MajaProduct.reg_tile, tile):
            self.tile = tile[1:]  # Remove the T from e.g. T32ABC
        else:
            self.tile = tile

        self.site = site
        if self.site:
            site_l1 = FileSystem.find_single(self.site, self.rep_l1)
            site_l2 = FileSystem.find_single(self.site, self.rep_l2)
            self.path_input_l1 = FileSystem.find_single(self.tile, site_l1)
            self.path_input_l2 = FileSystem.find_single(self.tile, site_l2)
            self.__site_info = "site %s and tile %s" % (self.site, self.tile)
        else:
            self.path_input_l1 = FileSystem.find_single(self.tile, self.rep_l1)
            self.path_input_l2 = FileSystem.find_single(self.tile, self.rep_l2)
            self.__site_info = "tile %s" % self.tile
            logging.debug("No site-folder specified. Searching for product directly by Tile-ID")

        # TODO wrap this in functions

        if not p.isdir(self.path_input_l1):
            raise OSError("L1 folder for %s not existing: %s" % (self.__site_info, self.path_input_l1))

        if not p.isdir(self.path_input_l2):
            logging.warning("L2 folder for %s not existing: %s" % (self.__site_info, self.path_input_l1))

        self.avail_input_l1 = sorted(self.get_available_products(self.path_input_l1, level="L1C", tile=self.tile))

        if not self.avail_input_l1:
            raise IOError("No L1C products detected for %s in %s" % (self.__site_info, self.path_input_l1))
        else:
            logging.info("%s L1C product(s) detected for %s in %s" % (len(self.avail_input_l1),
                                                                      self.__site_info,
                                                                      self.path_input_l1))
        self.avail_input_l2 = sorted(self.get_available_products(self.path_input_l2, level="L2A", tile=self.tile))

        if not self.avail_input_l2:
            logging.warning("No L2A products detected for %s in %s" % (self.__site_info, self.path_input_l2))
        else:
            logging.info("%s L2A product(s) detected for %s in %s" % (len(self.avail_input_l2),
                                                                      self.__site_info,
                                                                      self.path_input_l2))

        platform = list(set([prod.get_platform() for prod in self.avail_input_l1 + self.avail_input_l2]))

        if len(platform) != 1:
            raise IOError("Cannot mix multiple platforms: %s" % platform)
        self.platform = platform[0]

        # Parse products
        if start:
            if re.search(self.date_regex, start):
                self.start = DateConverter.stringToDatetime(start.replace("-", ""))
            else:
                raise ValueError("Unknown date encountered: %s" % start)
        else:
            dates = sorted([prod.get_date() for prod in self.avail_input_l1])
            self.start = dates[0]

        if end:
            if re.search(self.date_regex, end):
                self.end = DateConverter.stringToDatetime(end.replace("-", ""))
            else:
                raise ValueError("Unknown date encountered: %s" % end)
        else:
            dates = sorted([prod.get_date() for prod in self.avail_input_l1])
            self.end = dates[-1]

        if self.start > self.end:
            raise ValueError("Start date has to be before the end date!")

        # Subtract 1, which means excluding the actual product:
        self.nbackward = nbackward - 1

        self.overwrite = ParameterConverter.str2bool(overwrite)

        logging.debug("Searching for DTM")
        try:
            self.dtm = self.get_dtm()
        except OSError as e:
            logging.debug("Cannot find DTM!")
            logging.debug(e)
        else:
            logging.debug("Found DTM: %s" % self.dtm.hdr)

        self.cams_files = []
        if self.rep_cams:
            logging.debug("Searching for CAMS")
            self.cams_files = self.get_cams_files()
            logging.debug("...found %s CAMS files" % len(self.cams_files))
        return

    @staticmethod
    def __init_loggers(msg_level=logging.DEBUG):
        """
        Init a stdout logger
        :param msg_level: Standard msgLevel for both loggers. Default is DEBUG
        """

        # Create default path or get the pathname without the extension, if there is one
        logger = logging.getLogger()
        logger.handlers = []  # Remove the standard handler again - Bug in logging module
       
        logger.setLevel(msg_level)
        formatter = logging.Formatter("%(asctime)s [%(levelname)-5.5s] %(message)s")
        
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)
        return logger

    @staticmethod
    def __read_config_param(config, section, option):
        """
        Read a config parameter (a path) and check whether it exists
        :param config: The parsed config file
        :param section: The section to be searched for, e.g. PATH
        :param option: The parameter name
        :return: The path read as string or OSError if not
        """

        param = config.get(section, option)
        if not p.exists(param):
            raise OSError("%s %s is missing: %s" % (section, option, param))
        return param

    def parse_config(self, cfg_file):
        """
        Read contents of the config/folders.txt file containing:
        Required params:
            repWork, repL1, repL2, repMNT, exeMaja
        Optional params:
            repCAMS
        :param cfg_file: The path to the file
        :return: The parsed paths for each of the directories. None for the optional ones if not given.
        """
        try:
            import configparser as cfg
        except ImportError:
            import ConfigParser as cfg
        
        # Parsing configuration file
        config = cfg.ConfigParser()
        config.read(cfg_file)
    
        # get cfg parameters
        rep_work = self.__read_config_param(config, "PATH", "repWork")
        rep_l1 = self.__read_config_param(config, "PATH", "repL1")
        rep_l2 = self.__read_config_param(config, "PATH", "repL2")
        rep_mnt = self.__read_config_param(config, "PATH", "repMNT")
        exe_maja = self.__read_config_param(config, "PATH", "exeMaja")

        # CAMS is optional:
        try:
            rep_cams = self.__read_config_param(config, "PATH", "repCAMS")
        except cfg.NoOptionError:
            logging.warning("repCAMS is missing. Processing without CAMS")
            rep_cams = None
        
        return rep_work, rep_l1, rep_l2, rep_mnt, exe_maja, rep_cams

    @staticmethod
    def get_available_products(root, level, tile):
        """
        Parse the products from the constructed L1- or L2- directories
        :param root: The root folder to be searched from
        :param level: The product level to be search for
        :param tile: The tileID
        :return: A list of MajaProducts available in the given directory
        """
        avail_folders = [f for f in os.listdir(root) if p.isdir(p.join(root, f))]
        avail_products = [Product.MajaProduct(f).factory() for f in avail_folders]
        # Remove the ones that didn't work:
        avail_products = [prod for prod in avail_products if prod is not None]
        return [prod for prod in avail_products if prod.get_level() == level.lower() and prod.get_tile() == tile]

    def get_dtm(self):
        """
        Find DTM folder for tile and search for associated HDR and DBL files
        A DTM folder has the following naming structure:
            *_AUX_REFDE2_TILEID_*DBL.DIR with TILEID e.g. T31TCH, KHUMBU ...
        A single .HDR file and an associated .DBL.DIR file
        has to be found. OSError is thrown otherwise.
        :return: The full path to the hdr and dbl.dir
        """
        from Common import FileSystem
        regex = AuxFile.DTMFile.get_specifiable_regex() + r"T?" + self.tile + r"\w+.DBL.DIR"
        mnt_folders = FileSystem.find(regex, self.rep_mnt)
        mnts = [AuxFile.DTMFile(mnt) for mnt in mnt_folders]
        mnts = [mnt for mnt in mnts if mnt is not None]
        return mnts[0]

    def get_cams_files(self):
        """
        Find all associated CAMS- HDR and DBL files
        A CAMS folder has the following naming structure:
            MMM_TEST_EXO_CAMS_YYYYMMDDThhmmss_YYYYMMDDThhmmss
            with MMM = mission (see regex tests)
        For each CAMS a single .HDR file and an associated .DBL.DIR/.DBL file
        has to be found. Otherwise it gets discarded
        """
        from Common import FileSystem
        cams_folders = FileSystem.find(AuxFile.CAMSFile.regex, self.rep_cams)
        cams = [AuxFile.CAMSFile(c) for c in cams_folders]
        cams = [c for c in cams if c is not None]
        return cams

    @staticmethod
    def filter_cams_by_date(cams_files, start_date, end_date):
        """
        Filter out all CAMS files if they are between the given start_date and end_date
        """
        cams_filtered = []
        for cams in cams_files:
            date = cams.get_date()
            if date <= start_date or date >= end_date:
                cams_filtered.append(cams)
        return cams_filtered

    def create_workplans(self, max_product_difference=timedelta(hours=6), max_l2_diff=timedelta(days=14)):
        """
        Create a workplan for each Level-1 product found between the given date period
        For the first product available, check on top if an L2 product from the date
        before is present to run in NOMINAL.
        If not, check if there are at minimum n_backward products to run
        a BACKWARD processing.
        If both of those conditions are not met, a simple INIT is run and the rest
        in NOMINAL
        :param max_product_difference: Maximum time difference that the same L1 and L2 products date can be apart.
        This is necessary due to the fact that the acquisition date can vary in between platforms.
        :param max_l2_diff: Maximum time difference a separate L2 product can be apart from an L1 following it.
        :return: List of workplans to be executed
        """
        from Chain import Workplan

        # Get actually usable L1 products:
        used_prod_l1 = [prod for prod in self.avail_input_l1
                        if self.start <= prod.get_date() <= self.end]

        if not used_prod_l1:
            raise ValueError("No products available for the given start and end dates: %s -> %s"
                             % (self.start, self.end))

        # Get L1 products that already have an L2 product available using a timedelta (as times can be differing):
        has_l2 = [l1 for l1, l2 in zip(used_prod_l1, self.avail_input_l2)
                  if l1.get_date() - l2.get_date() < max_product_difference]

        # Setup workplans:
        workplans = []

        # TODO Write workplans
        # Process the first product separately:
        if used_prod_l1[0] not in has_l2 or self.overwrite:
            # Check if there is a recent L2 available for a nominal workplan
            min_time = used_prod_l1[0].get_date() - max_l2_diff
            max_time = used_prod_l1[0]
            has_closest_l2_prod = [prod for prod in self.avail_input_l2 if min_time <= prod.get_date() <= max_time]
            if has_closest_l2_prod:
                # Proceed with NOMINAL
                pass
            else:
                if len(self.avail_input_l1) >= self.nbackward:
                    # Proceed with BACKWARD
                    pass
                else:
                    # Proceed with INIT
                    logging.info("Not enough L1 products available for a BACKWARD mode. Beginning with INIT...")
                    pass
                pass

        # For the rest: Setup NOMINAL
        for prod in used_prod_l1[1:]:
            if prod in has_l2 and self.overwrite:
                logging.info("Skipping L1 product %s because it was already processed!")
                continue
            workplans.append(Workplan.ModeNominal(date=date,
                                                  L1=prod,
                                                  L2=None,
                                                  CAMS=CAMS,
                                                  DTM=DTM,
                                                  tile=tile,
                                                  conf=conf,
                                                  checkL2=True
                                                  ))
        
        # This should never happen:
        if not workplans:
            raise ValueError("No workplans created!")
        
        return workplans

    def run(self):
        """
        Run the whole artillery:
            - Find all L1 and L2 products
            - Find all CAMS files
            - Filter both by start and end dates, if there are
            - Determine the Workplans and a mode for each (INIT, BACKWARD, NOMINAL)
            - For each workplan:
            -   Create the input directory and link all the needed inputs
            -   Create the output directory
            -   Run MAJA
        """
        from Common import FileSystem
        availProdsL1, availProdsL2, platform = self.get_all_products(self.site, self.tile, rep_l1, rep_l2, self.input_dirs)
        availCAMS = self.get_cams_files(repCAMS)
        cams = self.filter_cams(availCAMS,self.start, self.end)
        workplans = self.create_workplans(prods_l1=availProdsL1, prods_l2=availProdsL2, platform=platform, CAMS=cams,
                                          DTM=self.dtm, tile=self.tile, conf=self.userconf, start_date=self.start,
                                          end_date=self.end, n_backward=self.nbackward)
        logging.info("%s workplan(s) successfully created:" % len(workplans))
        # Print without the logging-formatting:
        print(str("%8s | %5s | %8s | %70s | %15s" % ("DATE", "TILE", "MODE", "L1-PRODUCT", "INFO/L2-PRODUCT")))
        for wp in workplans:
            print(wp)
#            input_dir = self.createInputDir(rep_work, wp.productsL1 + wp.productsL2, cams, self.dtm, self.gipp)
#            specifier = self.getSpecifier(self.site, self.tile)
#            output_dir = p.join(rep_l2, specifier)
#            if(not p.exists(output_dir)):
#                FileSystem.createDirectory(output_dir)
#            wp.execute(exeMaja, input_dir, output_dir, self.tile, self.userconf, self.verbose)
#            FileSystem.removeDirectory(input_dir)
        logging.info("=============Start_Maja v%s finished=============" % self.version)

        pass


if __name__ == "__main__":
    assert sys.version_info >= (2, 7)

    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("-g", "--gipp", help="Full path to the GIPP folder being used",
                        type=str, required=True)
    parser.add_argument("-t", "--tile", help="Tile number",
                        type=str, required=True)
    parser.add_argument("-s", "--site", help="Site name. If not specified,"
                                             "the tile number is used directly for finding the L1/L2 product directory",
                        type=str, required=False)
    parser.add_argument("-f", "--folder", help="Config/Folder-definition file used for all permanent settings.",
                        type=str, required=True)
    parser.add_argument("-d", "--start", help="Start date for processing in format YYYY-MM-DD. If none is provided,"
                                              "all products until the end date will be processed",
                        type=str, required=False, default="2000-01-01")
    parser.add_argument("-e", "--end", help="Start date for processing in format YYYY-MM-DD. If none is provided,"
                                            "all products from the start date on will be processed",
                        type=str, required=False, default="3000-01-01")
    parser.add_argument("-v", "--verbose", help="Provides detailed logging for Maja. Default is false",
                        type=str, default="false")
    parser.add_argument("--nbackward", help="Number of products used to run in backward mode. Default is 8.",
                        type=int, default=int(8))
    parser.add_argument("--overwrite", help="Overwrite existing L2 products. Default is false.",
                        type=str, default="False")
    # TODO Add optional platform parameter in order to distinguish between S2/L8/Vns for each site/tile

    args = parser.parse_args()
    
    s = StartMaja(args.folder, args.tile, args.site, args.gipp,
                  args.start, args.end, args.nbackward,
                  args.overwrite, args.verbose)
    # s.run()
