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

class Start_maja(object):
    """
    Run the MAJA processor
    """
    version = "3.0.1"
    #For examples of all regex expressions see unittests!
    date_regex = r"\d{4}-\d{2}-\d{2}"
    regS2 = [r"^S2[AB]_MSIL1C_\d+T\d+_N\d+_R\d+_TXXXXX_\d+T\d+.SAFE$",
                r"^SENTINEL2[AB]_[-\d]+_L\w+_TXXXXX_\w_V[\d-]+$",
                r"^S2[AB]_OPER_SSC_L2VALD_XXXXX_\w+.HDR$",
                r"^S2[AB]_OPER_PRD_MSIL1C_PDMC_\w+_R\d+_V\w+.SAFE$"]
    regL8 = [r"^LC8_[a-zA-Z]+$",
                r"^LANDSAT8-_\w+_L\w+_TXXXXX_\w_V\w+$",
                r"^LC08_[a-zA-Z_]+$"]
    regVns = [r"^VENUS-XS_[-\d]+_L\w+_XXXXX_\w_V\w+",
                 r"^VE_VM\d{2}_VSC_L2VALD_\w+.HDR$",
                 r"^VE_TEST_VSC_L1VALD_\w+.HDR$"]
    regDTM = r"\w+_AUX_REFDE2_\w+"
    regGIPP = ["\w+GIP_" + gipp + "\w+" for gipp in ["L2ALBD",
                                                     "L2DIFT",
                                                     "L2DIRT",
                                                     "L2TOCR",
                                                     "L2WATV"]
              ] + ["\w+GIP_" + gipp + "\w+" for gipp in ["CKEXTL",
                                                         "CKQLTL",
                                                         "L2COMM",
                                                         "L2SITE",
                                                         "L2SMAC"]]
    
    current_dir = os.path.dirname(os.path.realpath(__file__))
    
    
    def __init__(self, gipp, tile, site, orbit, folder, dtm, start, verbose):
        """
        Init the instance using the old start_maja parameters
        """
        from Common import DateConverter
        self.verbose = verbose
        if(self.str2bool(self.verbose)):
            self.initLoggers(msgLevel=logging.DEBUG)
        else:
            self.initLoggers(msgLevel=logging.INFO)
        logging.info("=============This is Start_Maja v%s==============" % self.version)
        
        logging.debug("Checking GIPP files")
        if(not os.path.isdir(gipp)):
            raise OSError("Cannot find GIPP folder: %s" % gipp)
        for regGIPP in self.regGIPP:
            if not [f for f in os.listdir(gipp) if re.search(regGIPP, f)]:
                raise OSError("Missing GIPP file: %s" % regGIPP.replace("\w+", "*"))
        self.gipp = gipp
        logging.debug("...found")
        
        if(tile[0] == "T" and len(tile) == 6 and tile[1:2].isdigit()):
            self.tile = tile[1:] #Remove the T from e.g. T32ABC
        else:
            self.tile = tile
        self.site = site
        if(self.site == None):
            logging.info("No site specified. Searching for product directly by TileID")
        self.orbit = orbit
        if(not os.path.isfile(folder)):
            raise OSError("Cannot find folder definition file!")
        logging.debug("Searching for DTM")
        if(dtm is None):
            logging.info("No DTM specified. Searching for DTM in %s" % self.current_dir)
            dtm = self.current_dir
        dtms = [f for f in os.listdir(dtm) if re.search(self.regDTM + self.tile + "\w+", os.path.basename(f))]
        if(len(dtms) != 1):
            raise OSError("Error finding DTM for %s in %s" % (self.tile, dtm))
        self.dtm = dtms[0]
        logging.debug("...found %s" % self.dtm)
        self.folder = folder
        if(re.search(self.date_regex, start)):
            self.start = DateConverter.stringToDatetime(start.replace("-", ""))
        else:
            raise ValueError("Unknown date encountered: %s" % start)
        return
    
    @staticmethod
    def str2bool(v):
        """
        Returns a boolean following a string input
        :param v: String to be tested if it"s containing a True/False value
        :return: True, if string contains ("yes", "true", "t", "y", "1"), false if not
        """
        if v.lower() in ("yes", "true", "t", "y", "1"):
            return True
        elif v.lower() in ("no", "false", "f", "n", "0"):
            return False
        else:
            raise argparse.ArgumentTypeError("Boolean value expected.")
        return

    def initLoggers(self, msgLevel = logging.DEBUG, filepath = ""):
        """
        Init a file and a stdout logger
        :param msgLevel: Standard msgLevel for both loggers. Default is DEBUG
        :param filepath: The path to save the log-file to. If empty, no log-to-file will be done"
        """
        
        filename = "Start_Maja.log"

        #Create default path or get the pathname without the extension, if there is one

        logger=logging.getLogger()
        logger.handlers=[] #Remove the standard handler again - Bug in logging module
       
        logger.setLevel(msgLevel)
        formatter = logging.Formatter("%(asctime)s [%(levelname)-5.5s] %(message)s")
        
        consoleHandler = logging.StreamHandler(sys.stdout)
        consoleHandler.setFormatter(formatter)
        logger.addHandler(consoleHandler)
        
        #Currently deactivated
        if(filepath is not ""):
            strDbgLogFullPath = os.path.join(filepath, filename)
            print("Logging to file " + strDbgLogFullPath)
            self.createDirectory(filepath)
            fileHandler=logging.FileHandler(strDbgLogFullPath)
            fileHandler.setFormatter(formatter)
            logger.addHandler(fileHandler)
        return logger
    
    @staticmethod
    def symlink(src, dst):
        """
        Create symlink from src to dst and raise Exception if it didnt work
        """
        try:
            os.symlink(src, dst)
        except:
            raise OSError("Cannot create symlink for %s in %s. Does your plaform support symlinks?" % src, dst)
    
    def readFoldersFile(self, cfg_file):
        """
        Read contents of the folders.txt file containing at least the config params:
            repWork, repL1, repL2 and exeMaja
        :param cfg_file: The path to the file
        """
        import configparser
        import os
        # Parsing configuration file
        config = configparser.ConfigParser()
        config.read(cfg_file)
    
        # get cfg parameters
        repWork = config.get("PATH", "repWork")
        if(not os.path.isdir(repWork)):
            raise OSError("repWork is missing: %s" % repWork)
        repL1 = config.get("PATH", "repL1")
        if(not os.path.isdir(repL1)):
            raise OSError("repL1 is missing: %s" % repL1)
        repL2 = config.get("PATH", "repL2")
        if(not os.path.isdir(repL2)):
            raise OSError("repL2 is missing: %s" % repL2)
        exeMaja = config.get("PATH", "exeMaja")
        if(not os.path.isfile(exeMaja)):
            raise OSError("exeMaja is missing: %s" % exeMaja)
        #CAMS is optional:
        try:
            repCAMS = config.get("PATH", "repCAMS")
            if(not os.path.isdir(repCAMS)):
                raise OSError("repCAMS is missing: %s" % repCAMS)
        except configparser.NoOptionError:
            logging.warning("repCAMS is missing. Processing without CAMS")
            repCAMS = None
        
        return repWork, repL1, repL2, exeMaja, repCAMS
    
    @staticmethod
    def getPlatformProducts(site, tile, rep, reg):
        """
        Get the available products for a given platform regex
        """
        if(site == None):
            specifier = tile
        else:
            specifier = os.path.join(site, tile)
        
        if(not os.path.isdir(os.path.join(rep, specifier))):
            return []
        
        prods = []
        for prod in os.listdir(os.path.join(rep, specifier)):
            for pattern in reg:
                if(re.search(re.compile(pattern.replace("XXXXX", tile)), prod)):
                    prods.append(prod)
        return prods
    
    def getAllProducts(self, site, tile, repL1, repL2):
        """
        Get all available L1 and L2 products for the tile and site
        """
        prevL1, prevL2 = [], []
        for platform in [self.regS2, self.regL8, self.regVns]:
            repL1filtered = self.getPlatformProducts(site, tile, repL1, platform)
            repL2filtered = self.getPlatformProducts(site, tile, repL2, platform)
            if(repL1filtered and not prevL1):
                prevL1 = repL1filtered
                prevL2 = repL2filtered
            elif(repL1filtered and prevL1):
                raise OSError("Products for multiple platforms found: %s, %s" % (prevL1, prevL2))
        if(not prevL1):
            raise OSError("Cannot find L1 products for tile %s in %s" % (tile, repL1))
        if(not prevL2):
            logging.debug("No L2 products found.")
            
        #Determine mode:
        if(len(prevL1) > 1):
            mode = "BACKWARD"
        elif(len(prevL2) == 1 and len(prevL1) == 1):
            mode = "NOMINAL"
        elif(len(prevL1) == 1):
            mode = "INIT"
        logging.info("Selected mode: %s" % mode)
        return prevL1, prevL2, mode
    
    def createInputDir(self):
        """
        Set up all files of the input directory, which are:
            Product (1C and eventually 2A)
            GIPPs
            DTM
            (CAMS)
        """
        
        pass
    
    def launchMAJA(self, maja_exe, input_dir, out_dir, mode, tile, conf):
        """
        Run the MAJA processing
        """
        pass

    def run(self):
        repWork, repL1, repL2, exeMaja, repCAMS = self.readFoldersFile(self.folder)
        self.getAllProducts(self.site, self.tile, repL1, repL2)
        self.createInputDir()
        pass

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("-g", "--gipp", help="Name of the GIPP folder to be used", type=str, required=True)
    parser.add_argument("-t", "--tile", help="Tile number", type=str, required=True)
    parser.add_argument("-s", "--site", help="Site name. If not specified, the tile number is used directly for finding the L1/L2 product", type=str, required=False)
    parser.add_argument("-o", "--orbit", help="Orbit number", type=int, required=True)
    parser.add_argument("-f", "--folder", type=str, help="Folder definition file", required=True)
    parser.add_argument("-m", "--dtm", type=str, help="DTM folder. If none is specified, it will be searched for in the code directory", required=False)
    parser.add_argument("-d", "--start", help="Start date for processing in format YYYY-MM-DD (optional)", type=str, required=False, default="2000-01-01")
    parser.add_argument("-v", "--verbose", help="Will provide debug logs. Default is false", type=str, default="false")
    args = parser.parse_args()
    
    s = Start_maja(args.gipp, args.tile, args.site, args.orbit, args.folder, args.dtm, args.start, args.verbose)
    s.run()