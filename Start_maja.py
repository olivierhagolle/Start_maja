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
from Chain import Product


class StartMaja(object):
    """
    Run the MAJA processor
    """
    version = "3.0.1"
    date_regex = r"\d{4}-\d{2}-\d{2}"  # YYYY-MM-DD

    regCAMS = r"\w{3}_(TEST|PROD)_EXO_CAMS_\w+"
    regDTM = r"\w+_AUX_REFDE2_\w*"
    regGIPP = [r"\w+_(TEST|PROD)_GIP_" + gipp + "\w+" for gipp in ["L2ALBD",
                                                                   "L2DIFT",
                                                                   "L2DIRT",
                                                                   "L2TOCR",
                                                                   "L2WATV"]] +\
              [r"\w+_(TEST|PROD)_GIP_" + gipp + "\w+" for gipp in ["CKEXTL",
                                                                   "CKQLTL",
                                                                   "L2COMM",
                                                                   "L2SITE",
                                                                   "L2SMAC"]]

    current_dir = p.dirname(p.realpath(__file__))

    def __init__(self, folder, tile, site, gipp, start, end, nbackward, verbose):
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
        for regGIPP in self.regGIPP:
            if not [f for f in os.listdir(gipp) if re.search(regGIPP, f)]:
                raise OSError("Missing GIPP file: %s" % regGIPP)
        logging.debug("Found GIPP folder: %s" % gipp)
        
        if tile[0] == "T" and re.search(Product.MajaProduct.reg_tile, tile):
            self.tile = tile[1:]  # Remove the T from e.g. T32ABC
        else:
            self.tile = tile
        self.site = site
        if not site:
            self.path_input_l1 = p.join(self.rep_l1, self.tile)
            self.path_input_l2 = p.join(self.rep_l2, self.tile)
            self.__site_info = "tile %s" % self.tile
            logging.info("No site-folder specified. Searching for product directly by Tile-ID")
        else:
            self.path_input_l1 = p.join(self.rep_l1, self.site, self.tile)
            self.path_input_l2 = p.join(self.rep_l2, self.site, self.tile)
            self.__site_info = "site %s and tile %s" % (self.site, self.tile)

        # TODO wrap this in functions

        if not p.isdir(self.path_input_l1):
            raise OSError("L1 folder for %s not existing: %s" % (self.__site_info, self.path_input_l1))

        if not p.isdir(self.path_input_l2):
            logging.warning("L2 folder for %s not existing: %s" % (self.__site_info, self.path_input_l1))

        self.avail_input_l1 = self.parse_products(self.path_input_l1)

        if not self.avail_input_l1:
            raise IOError("No L1C products detected for %s in %s" % (self.__site_info, self.path_input_l1))
        else:
            logging.info("%s L1C products detected for %s in %s" % (len(self.avail_input_l1),
                                                                    self.__site_info,
                                                                    self.path_input_l1))
        self.avail_input_l2 = self.parse_products(self.path_input_l2)

        if not self.avail_input_l2:
            logging.warning("No L2A products detected for %s in %s" % (self.__site_info, self.path_input_l2))
        else:
            logging.info("%s L2A products detected for %s in %s" % (len(self.avail_input_l2),
                                                                    self.__site_info,
                                                                    self.path_input_l2))

        # TODO if no dates given, parse then automatically
        # Parse products
        if start and re.search(self.date_regex, start):
            self.start = DateConverter.stringToDatetime(start.replace("-", ""))
        else:
            raise ValueError("Unknown date encountered: %s" % start)
        if re.search(self.date_regex, end):
            self.end = DateConverter.stringToDatetime(end.replace("-", ""))
        else:
            raise ValueError("Unknown date encountered: %s" % end)
        if self.start > self.end:
            raise ValueError("Start date has to be before the end date!")
        # Subtract 1, which means including the actual product:
        self.nbackward = nbackward - 1
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
    def parse_products(root):
        """
        Parse the products from the constructed L1- or L2- directories
        :param root: The root folder to be searched from
        :return: A list of MajaProducts available in the given directory
        """
        avail_folders = [f for f in os.listdir(root) if p.isdir(p.join(root, f))]
        return [Product.MajaProduct(f).factory() for f in avail_folders]

    def get_dtm_files(self, dtm_dir):
        """
        Find DTM folder for tile and search for associated HDR and DBL files
        A DTM folder has the following naming structure:
            S2__TEST_AUX_REFDE2_TILEID_0001 with TILEID e.g. T31TCH, KHUMBU ...
        Inside the folder, a single .HDR file and an associated .DBL.DIR file
        has to be found. OSError is thrown otherwise.
        :param dtm_dir: The directory containing the DTM folder.
        """
        logging.debug("Searching for DTM")
        if dtm_dir is None:
            logging.info("No DTM specified. Searching for DTM in %s" % self.current_dir)
            dtm_dir = self.current_dir

        hdr_files, dbl_files = [], []
        for f in os.listdir(p.join(dtm_dir)):
            if re.search(self.regDTM + self.tile + "\w*" + ".HDR", p.basename(f)):
                hdr_files.append(p.join(dtm_dir, f))
            if re.search(self.regDTM + self.tile + "\w*" + ".DBL", p.basename(f)):
                dbl_files.append(p.join(dtm_dir, f))
        if len(hdr_files) == 1 and len(dbl_files) >= 1:
            logging.debug("...found %s" % p.basename(hdr_files[0]))
            return hdr_files + dbl_files

        # If not found yet, search for folder with the same name:
        hdr_files, dbl_files = [], []
        dtm_folder = [f for f in os.listdir(dtm_dir) if re.search(self.regDTM + self.tile + "\w+", p.basename(f))]
        if len(dtm_folder) != 1:
            raise OSError("Error finding DTM folder for %s in %s" % (self.tile, dtm_dir))
        for f in os.listdir(p.join(dtm_dir, dtm_folder[0])):
            if re.search(self.regDTM + self.tile + "\w*" + ".HDR", p.basename(f)):
                hdr_files.append(p.join(dtm_dir, dtm_folder[0], f))
            if re.search(self.regDTM + self.tile + "\w*" + ".DBL", p.basename(f)):
                dbl_files.append(p.join(dtm_dir, dtm_folder[0], f))
        if len(hdr_files) != 1:
            raise OSError("More than one .HDR file found for DTM %s in %s" % (self.tile, dtm_dir))
        dtm = [p.join(dtm_dir, dtm_folder[0], f) for f in hdr_files + dbl_files]
        logging.debug("...found %s" % p.basename(hdr_files[0]))
        return dtm

    @staticmethod
    def set_input_directories(prod_l1, prod_l2, input_dirs):
        """
        Set the L1 and L2 product directory paths. If input_dirs is set, it
        overloads first the L1C directory, then the L2A directory
        """
        if not input_dirs:
            if not p.isdir(prod_l1):
                raise OSError("repL1 is missing: %s" % prod_l1)
            if not p.isdir(prod_l2):
                raise OSError("repL2 is missing: %s" % prod_l2)
            return prod_l1, prod_l2
        
        if len(input_dirs) == 1:
            if not p.exists(input_dirs[0]):
                raise OSError("Cannot find L1C directory: %s" % input_dirs[0])
            if not p.isdir(prod_l2):
                raise OSError("repL2 is missing: %s" % prod_l2)
            return input_dirs[0], prod_l2
        elif len(input_dirs) == 2:
            if not p.exists(input_dirs[0]):
                raise OSError("Cannot find L1C directory: %s" % input_dirs[0])
            if not p.exists(input_dirs[1]):
                raise OSError("Cannot find L2A directory: %s" % input_dirs[1])
            return input_dirs[0], input_dirs[1]
        
        raise ValueError("More than two input directories given: %s" % input_dirs)
        
    def get_cams_files(self, cams_dir):
        """
        Find CAMS folder and search for associated HDR and DBL files
        A CAMS folder has the following naming structure:
            MMM_TEST_EXO_CAMS_YYYYMMDDThhmmss_YYYYMMDDThhmmss
            with MMM = mission (e.g. S2_)
        Inside the folder, a single .HDR file and an associated .DBL.DIR/.DBL file
        has to be found. OSError is thrown otherwise.
        :param cams_dir: The directory containing the CAMS folder.
        """
        hdr_files, dbl_files = [], []
        if not cams_dir:
            return []
        logging.debug("Searching for CAMS")
        for f in os.listdir(cams_dir):
            if re.search(self.regCAMS + ".HDR", p.basename(f)):
                hdr_files.append(p.join(cams_dir, f))
            if re.search(self.regCAMS + ".DBL", p.basename(f)):
                dbl_files.append(p.join(cams_dir, f))
        if len(hdr_files) > len(dbl_files):
            raise OSError("One or more CAMS HDR files imcomplete: #HDR=%s, #DBL=%s"
                          % (len(hdr_files), len(dbl_files)))
        cams = hdr_files + dbl_files
        logging.debug("...found %s CAMS files" % len(hdr_files))
        return cams
    
    @staticmethod
    def filter_cams(cams_files, start_date, end_date):
        """
        Filter out all CAMS files if they are between the given start_date and end_date
        """
        from Common import DateConverter as dc
        cams_filtered = []
        for cams in cams_files:
            date = dc.getCAMSDate(cams)
            if date <= start_date or date >= end_date:
                cams_filtered.append(cams)
        return cams_filtered
    
    @staticmethod
    def get_specifier(site, tile):
        """
        Determine whether the products are ordered by site and tile or only by tile
        """
        if not site:
            specifier = tile
        else:
            specifier = site
        return specifier
    
    @staticmethod
    def get_platform_products(input_dir, tile, reg):
        """
        Get the available products for a given platform regex
        """
        prods = []
        if not p.isdir(input_dir):
            return prods
        for prod in os.listdir(input_dir):
            for i, pattern in enumerate(reg):
                if re.search(re.compile(pattern.replace("XXXXX", tile)), prod):
                    prods.append((p.join(input_dir, prod), i))
        return prods
    
    def get_all_products(self, site, tile, rep_l1, rep_l2, input_dirs):
        """
        Get all available L1 and L2 products for the tile and site
        """
        prev_l1, prev_l2 = [], []
        platform_id = -1
        specifier = self.get_specifier(site, tile)
        input_rep_l1 = p.join(rep_l1, specifier)
        input_rep_l2 = p.join(rep_l2, specifier)
        input_dir_l1, input_dir_l2 = self.set_input_directories(input_rep_l1, input_rep_l2, input_dirs)
        for i, platform in enumerate([self.regS2, self.regL8, self.regVns]):
            rep_l1_filtered = self.get_platform_products(input_dir_l1, tile, platform)
            rep_l2_filtered = self.get_platform_products(input_dir_l2, tile, platform)
            if rep_l1_filtered and not prev_l1:
                platform_id = i
                prev_l1 = rep_l1_filtered
                prev_l2 = rep_l2_filtered
            elif rep_l1_filtered and prev_l1 or rep_l2_filtered and prev_l2:
                raise OSError("Products for multiple platforms found: %s, %s" % (prev_l1, prev_l2))
        if not prev_l1:
            raise OSError("Cannot find L1 products for site %s or tile %s in %s"
                          % (site, tile, rep_l1))
        if not prev_l2:
            logging.debug("No L2 products found.")
            
        return prev_l1, prev_l2, platform_id
    
    @staticmethod
    def filter_products_by_date(prods_l1, prods_l2, platform, start_date, end_date, nbackward):
        """
        Filter out all products if they are between the given start_date and end_date
        """
        from Common import DateConverter as dc
        prods_l1_filtered, prods_l2_filtered = [], []
        print(prods_l1)
        print(prods_l2)
        # Get the first available L1 product for the current start date
        process_l1 = [dc.getDateFromProduct(d, platform) for d in prods_l1 if dc.getDateFromProduct(d, platform) >= start_date]
        if not process_l1:
            raise ValueError("No products found after start date %s" % dc.datetimeToString(start_date))
        start_l1 = sorted(process_l1)[0]
        # Get products before this date
        prev_l1 = [d for d in prods_l1 if dc.getDateFromProduct(d, platform) < start_l1]
        prev_l2 = [d for d in prods_l2 if dc.getDateFromProduct(d, platform) < start_l1]
        if prev_l2:
            mode = ["NOMINAL"]
        elif prev_l1:
            mode = ["BACKWARD"]
            if len(prev_l1) < nbackward:
                logging.warning("Less than %s L1 products found for the %s mode" % (nbackward, mode[0]))
        elif not prev_l1:
            mode = ["INIT"]
            logging.warning("Missing previous L2 products. Will begin with INIT mode")
        else:
            raise ValueError("Unknown configuration encountered with products %s %s", prev_l1, prev_l2)
        print(mode)
        exit(1)
        for prod in prods_l1:
            d = dc.getDateFromProduct(prod, platform)
            if start_date <= d <= end_date:
                prods_l1_filtered.append(prod)
        for prod in prods_l2:
            d = dc.getDateFromProduct(prod, platform)
            if start_date <= d <= end_date:
                prods_l2_filtered.append(prod)
        if len(prods_l1_filtered) == 0:
            raise ValueError("No L1 products between %s and %s" %
                             (dc.datetimeToStringShort(start_date),
                              dc.datetimeToStringShort(end_date)))
        
        return prods_l1_filtered, prods_l2_filtered
    
    def create_workplans(self, prods_l1, prods_l2, platform, tile, CAMS, DTM, start_date, conf, end_date, n_backward):
        """
        Create a workplan for each Level-1 product found between the given date period
        For the first product available, check on top if an L2 product from the date
        before is present to run in NOMINAL.
        If not, check if there are at minimum n_backward products to run
        a BACKWARD processing.
        If both of those conditions are not met, a simple INIT is run and the rest
        in NOMINAL
        :param prods_l1: All L1 products found
        :param prods_l2: All L2 products found
        :param platform: The platform of the L1 and L2 products
        :param start_date: Beginning of the desired processing period
        :param end_date: End of the desired processing period
        :param n_backward: Minimum number of products to be used for a BACKWARD mode
        :return: List of workplans to be executed
        """
        from Common import DateConverter as dc
        from Chain import Workplan as wp
        
        # Create list of L2 and L1 products with their respective date:
        dates_l2 = sorted([(dc.getDateFromProduct(prod, platform), prod) for prod in prods_l2], key=lambda tup: tup[0])
        dates_l1 = sorted([(dc.getDateFromProduct(prod, platform), prod) for prod in prods_l1], key=lambda tup: tup[0])
        
        # Filter out all L1 products before the start_date:
        dates_l1filtered = [(date, prod) for date, prod in dates_l1 if date > start_date]
        if len(dates_l1) - len(dates_l1filtered) > 0:
            logging.info("Discarding %s products older than the start date %s" %
                         (len(dates_l1) - len(dates_l1filtered), dc.datetimeToStringShort(start_date)))
        
        workplans = []
        # First product: Check if L2 existing, if not check if BACKWARD possible:
        date_l1 = dc.getDateFromProduct(dates_l1filtered[0][1], platform)
        if date_l1 > end_date:
            raise ValueError("No workplan can be created for the chosen period %s to %s" %
                             (dc.datetimeToStringShort(start_date), dc.datetimeToStringShort(end_date)))
        prod_l2 = dc.findPreviousL2Product(dates_l2, date_l1)
        past_l1 = dc.findNewerProducts(dates_l1filtered, date_l1)
        if prod_l2:
            workplans.append(wp.ModeNominal(date=dates_l1filtered[0][0],
                                            L1=dates_l1filtered[0][1],
                                            L2=prod_l2[0][1],
                                            CAMS=CAMS,
                                            DTM=DTM,
                                            tile=tile,
                                            conf=conf
                                            ))
        elif len(past_l1) >= n_backward:
            logging.warning("No previous L2 product found. Beginning in BACKWARD mode")
            workplans.append(wp.ModeBackward(date=dates_l1filtered[0][0],
                                             L1=[dates_l1filtered[0][1]] + [prod for date, prod in past_l1[:n_backward]],
                                             L2=None,
                                             CAMS=CAMS,
                                             DTM=DTM,
                                             tile=tile,
                                             conf=conf
                                             ))
        else:
            print("Test1", dates_l1filtered[0])
            # If both fail, go for an INIT mode and log a warning:
            logging.warning("Less than %s _l1 products found. Beginning in INIT mode" % n_backward)
            workplans.append(wp.ModeInit(date=dates_l1filtered[0][0],
                                         L1=dates_l1filtered[0][1],
                                         L2=None,
                                         CAMS=CAMS,
                                         DTM=DTM,
                                         tile=tile,
                                         conf=conf
                                         ))
        # For the rest: Setup NOMINAL
        for date, prod in dates_l1filtered[1:]:
            if date > end_date:
                continue
            workplans.append(wp.ModeNominal(date=date,
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

    args = parser.parse_args()
    
    s = StartMaja(args.folder, args.tile, args.site, args.gipp, args.start, args.end, args.nbackward, args.verbose)
    # s.run()
