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
    date_regex = r"\d{4}-\d{2}-\d{2}" #YYYY-MM-DD
    regS2 = [r"^S2[AB]_MSIL1C_\d+T\d+_N\d+_R\d+_TXXXXX_\d+T\d+.SAFE$",
                r"^SENTINEL2[AB]_[-\d]+_L(1C|2A)_TXXXXX_\w_V[\d-]+$",
                r"^S2[AB]_OPER_SSC_L[12]VALD_XXXXX_\w+.HDR$",
                r"^S2[AB]_OPER_PRD_MSIL1C_PDMC_\w+_R\d+_V\w+.SAFE$"]
    regL8 = [r"^LC08_L\w+",
                r"^LC8\w+$",
                r"^LANDSAT8-[\w-]+_[-\d]+_L(1C|2A)_TXXXXX_\w_V[\d-]+$",
                r"^L8_\w{4}_L8C_L[12]VALD_[\d_]+.HDR$"]
    regVns = [r"^VENUS-XS_[-\d]+_L(1C|2A)_XXXXX_\w_V\w+",
                 r"^VE_\w{4}_VSC_L[12]VALD_\w+.HDR$"]
    regCAMS = r"\w{3}_TEST_EXO_CAMS_\w+"
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
    
    
    def __init__(self, input_dirs, gipp, tile, site, folder, dtm, start, end, verbose):
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
        
        self.input_dirs = input_dirs
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
        if(not os.path.isfile(folder)):
            raise OSError("Cannot find folder definition file!")
        self.folder = folder
        self.dtm = self.getDTMFiles(dtm)
        if(re.search(self.date_regex, start)):
            self.start = DateConverter.stringToDatetime(start.replace("-", ""))
        else:
            raise ValueError("Unknown date encountered: %s" % start)
        if(re.search(self.date_regex, end)):
            self.end = DateConverter.stringToDatetime(end.replace("-", ""))
        else:
            raise ValueError("Unknown date encountered: %s" % end)
        self.userconf = os.path.join(self.current_dir, "userconf")
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
        if(os.path.exists(dst) and os.path.islink(dst)):
            logging.debug("File already existing: %s" % dst)
            return
        
        try:
            os.symlink(src, dst)
        except:
            raise OSError("Cannot create symlink for %s at %s. Does your plaform support symlinks?" % (src, dst))
    def findDTMFiles(self, dtm_dir):
        pass
    
    def getDTMFiles(self, dtm_dir):
        """
        Find DTM folder for tile and search for associated HDR and DBL files
        A DTM folder has the following naming structure:
            S2__TEST_AUX_REFDE2_TILEID_0001 with TILEID e.g. T31TCH, KHUMBU ...
        Inside the folder, a single .HDR file and an associated .DBL.DIR file
        has to be found. OSError is thrown otherwise.
        :param dtm_dir: The directory containing the DTM folder.
        """
        logging.debug("Searching for DTM")
        if(dtm_dir is None):
            logging.info("No DTM specified. Searching for DTM in %s" % self.current_dir)
            dtm_dir = self.current_dir
            
        hdr_files, dbl_files = [], []
        for f in os.listdir(os.path.join(dtm_dir)):
            if(re.search(self.regDTM + self.tile + "\w*" + ".HDR", os.path.basename(f))):
                hdr_files.append(os.path.join(dtm_dir, f))
            if(re.search(self.regDTM + self.tile + "\w*" + ".DBL", os.path.basename(f))):
                dbl_files.append(os.path.join(dtm_dir, f))
        if(len(hdr_files) == 1 and len(dbl_files) >= 1):
            logging.debug("...found %s" % os.path.basename(hdr_files[0]))
            return hdr_files + dbl_files
        
        #If not found yet, search for folder with the same name:
        hdr_files, dbl_files = [], []
        dtm_folder = [f for f in os.listdir(dtm_dir) if re.search(self.regDTM + self.tile + "\w+", os.path.basename(f))]        
        if(len(dtm_folder) != 1):
            raise OSError("Error finding DTM folder for %s in %s" % (self.tile, dtm_dir))
        for f in os.listdir(os.path.join(dtm_dir, dtm_folder[0])):
            if(re.search(self.regDTM + self.tile + "\w*" + ".HDR", os.path.basename(f))):
                hdr_files.append(os.path.join(dtm_dir, dtm_folder[0], f))
            if(re.search(self.regDTM + self.tile + "\w*" + ".DBL", os.path.basename(f))):
                dbl_files.append(os.path.join(dtm_dir, dtm_folder[0], f))
        if(len(hdr_files) != 1):
            raise OSError("More than one .HDR file found for DTM %s in %s" % (self.tile, dtm_dir))
        dtm = [os.path.join(dtm_dir, dtm_folder[0], f) for f in hdr_files + dbl_files]
        logging.debug("...found %s" % os.path.basename(hdr_files[0]))
        return dtm
    
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
        except:
            logging.warning("repCAMS is missing. Processing without CAMS")
            repCAMS = None
        
        return repWork, repL1, repL2, exeMaja, repCAMS
    
    @staticmethod
    def setInputDirectories(prodL1, prodL2, input_dirs):
        """
        Set the L1 and L2 product directory paths. If input_dirs is set, it
        overloads first the L1C directory, then the L2A directory
        """
        if(not input_dirs):
            return prodL1, prodL2
        
        if(len(input_dirs) == 1):
            if(not os.path.exists(input_dirs[0])):
                raise OSError("Cannot find L1C directory: %s" % input_dirs[0])
            return input_dirs[0], prodL2
        elif(len(input_dirs) == 2):
            if(not os.path.exists(input_dirs[0])):
                raise OSError("Cannot find L1C directory: %s" % input_dirs[0])
            if(not os.path.exists(input_dirs[1])):
                raise OSError("Cannot find L2A directory: %s" % input_dirs[1])
            return input_dirs[0], input_dirs[1]
        
        raise ValueError("More than two input directories given: %s" % input_dirs)
        
    def getCAMSFiles(self, cams_dir):
        """
        Find CAMS folder and search for associated HDR and DBL files
        A CAMS folder has the following naming structure:
            MMM_TEST_EXO_CAMS_YYYYMMDDThhmmss_YYYYMMDDThhmmss
            with MMM = mission (e.g. S2_)
        Inside the folder, a single .HDR file and an associated .DBL.DIR/.DBL file
        has to be found. OSError is thrown otherwise.
        :param dtm_dir: The directory containing the CAMS folder.
        """
        hdr_files, dbl_files = [], []
        if(cams_dir == None):
            return []
        logging.debug("Searching for CAMS")
        for f in os.listdir(cams_dir):
            if(re.search(self.regCAMS + ".HDR", os.path.basename(f))):
                hdr_files.append(os.path.join(cams_dir, f))
            if(re.search(self.regCAMS + ".DBL", os.path.basename(f))):
                dbl_files.append(os.path.join(cams_dir, f))
        if(len(hdr_files) > len(dbl_files)):
            raise OSError("One or more CAMS HDR files imcomplete: #HDR=%s, #DBL=%s"
                % (len(hdr_files), len(dbl_files)))
        cams = hdr_files + dbl_files
        logging.debug("...found %s CAMS files" % len(hdr_files))
        return cams
    
    @staticmethod
    def filterCAMSByDate(cams_files, start_date, end_date):
        """
        Filter out all CAMS files if they are between the given start_date and end_date
        """
        from Common import DateConverter as dc
        cams_filtered = []
        for cams in cams_files:
            date = dc.getCAMSDate(cams)
            if(date <= start_date or date >= end_date):
                cams_filtered.append(cams)
        return cams_filtered
    
    @staticmethod
    def getSpecifier(site, tile):
        if(site == None):
            specifier = tile
        else:
            specifier = site
        return specifier
    
    @staticmethod
    def getPlatformProducts(input_dir, tile, reg):
        """
        Get the available products for a given platform regex
        """
        prods = []
        if(not os.path.isdir(input_dir)):
            return prods
        for prod in os.listdir(input_dir):
            for i, pattern in enumerate(reg):
                if(re.search(re.compile(pattern.replace("XXXXX", tile)), prod)):
                    prods.append((os.path.join(input_dir, prod), i))
        return prods
    
    def getAllProducts(self, site, tile, repL1, repL2, input_dirs):
        """
        Get all available L1 and L2 products for the tile and site
        """
        prevL1, prevL2 = [], []
        platformID = -1
        specifier = Start_maja.getSpecifier(site, tile)
        input_repL1 = os.path.join(repL1, specifier)
        input_repL2 = os.path.join(repL2, specifier)
        input_dirL1, input_dirL2 = self.setInputDirectories(input_repL1, input_repL2, input_dirs)
        for i, platform in enumerate([self.regS2, self.regL8, self.regVns]):
            repL1filtered = self.getPlatformProducts(input_dirL1, tile, platform)
            repL2filtered = self.getPlatformProducts(input_dirL2, tile, platform)
            if(repL1filtered and not prevL1):
                platformID = i
                prevL1 = repL1filtered
                prevL2 = repL2filtered
            elif(repL1filtered and prevL1 or repL2filtered and prevL2):
                raise OSError("Products for multiple platforms found: %s, %s" % (prevL1, prevL2))
        if(not prevL1):
            raise OSError("Cannot find L1 products for site %s or tile %s in %s"
                          % (site, tile, repL1))
        if(not prevL2):
            logging.debug("No L2 products found.")
            
        return prevL1, prevL2, platformID
    
    @staticmethod
    def filterProductsByDate(prodsL1, prodsL2, platform, start_date, end_date):
        """
        Filter out all products if they are between the given start_date and end_date
        """
        from Common import DateConverter as dc
        prodsL1filtered, prodsL2filtered = [], []
        for prod in prodsL1:
            d = dc.getDateFromProduct(prod, platform)
            if(d >= start_date and d <= end_date):
                prodsL1filtered.append(prod)
        for prod in prodsL2:
            d = dc.getDateFromProduct(prod, platform)
            if(d >= start_date and d <= end_date):
                prodsL2filtered.append(prod)
        if(len(prodsL1filtered) == 0):
            raise ValueError("No L1 products between %s and %s" %
                             (dc.datetimeToStringShort(start_date),
                              dc.datetimeToStringShort(end_date)))
        
        return prodsL1filtered, prodsL2filtered
    
    @staticmethod
    def determineMode(prodsL1, prodsL2):
        """
        Determine the mode that Maja will run in depending
        on the available L1 and L2 products
        """
        #Determine mode:
        if(len(prodsL1) > 1):
            mode = "BACKWARD"
        elif(len(prodsL2) == 1 and len(prodsL1) == 1):
            mode = "NOMINAL"
        elif(len(prodsL1) == 1):
            mode = "INIT"
        else:
            raise ValueError("Unknown configuration encountered: Products L1: %s, Products L2: %s"
                             % (len(prodsL1), len(prodsL2)))
        logging.info("Selected mode: %s" % mode)
        return mode
        
    def createInputDir(self, wdir, products, cams, dtm, gipps):
        """
        Set up all files of the input directory, which are:
            Product (1C and eventually 2A)
            GIPPs
            DTM
            (CAMS) if existing
        """
        
        from Common.FileSystem import createDirectory
        
        input_dir = os.path.join(wdir, "StartMaja")
        createDirectory(input_dir)
        
        for prod, i in products:
            self.symlink(prod, os.path.join(input_dir, os.path.basename(prod)))
        for f in cams:
            self.symlink(f, os.path.join(input_dir, os.path.basename(f)))
        for f in dtm:
            self.symlink(f, os.path.join(input_dir, os.path.basename(f)))
        for gipp in os.listdir(gipps):
            self.symlink(os.path.join(gipps, gipp), os.path.join(input_dir, os.path.basename(gipp)))
        return input_dir

    @staticmethod
    def runExternalApplication(name, args):
        """
        Run an external application using the subprocess module
        :param name: the Name of the application
        :param args: The list of arguments to run the app with
        :return: The return code of the App
        """
        from timeit import default_timer as timer
        import subprocess
        fullArgs = [name] + args
        logging.info(" ".join(a for a in fullArgs))
        fullArgs = fullArgs #Prepend other programs here
        start = timer()
        proc = subprocess.Popen(fullArgs, shell=False, bufsize=1, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        while (True):
            # Read line from stdout, break if EOF reached, append line to output
            line = proc.stdout.readline().decode('utf-8')
            #Poll(): Used to get the return code at the end of the execution
            if (line == "") and proc.poll() is not None:
                break
            logging.debug(line[:-1])
        end = timer()
        returnCode = proc.returncode
        #If this is not the testRun, raise an Error:
        if(returnCode != 0):
            raise subprocess.CalledProcessError(returnCode, name)
        #Show total execution time for the App:
        logging.info("{0} took: {1}s".format(os.path.basename(name), end - start))
        return returnCode

    def launchMAJA(self, maja_exe, input_dir, out_dir, mode, tile, conf, verbose):
        """        print(input_dirL2)

        Run the MAJA processor for the given input_dir, mode and tile 
        """
        
        args = [
                "-i",
                input_dir,
                "-o",
                out_dir,
                "-m",
                "L2" + mode,
                "-ucs",
                conf,
                "--TileId",
                tile]
        
        if(verbose):
            args += ["-l", "DEBUG"]
        return self.runExternalApplication(maja_exe, args)

    def run(self):
        """
        Run the whole artillery:
            - Find all L1 and L2 products
            - Find all CAMS files
            - Filter both by start and end dates, if there are
            - Determine the Mode: INIT, BACKWARD, NOMINAL
            - Create the input directory and linking all the needed inputs
            - Create the output directory
            - Run MAJA
        """
        from Common import FileSystem
        repWork, repL1, repL2, exeMaja, repCAMS = self.readFoldersFile(self.folder)
        availProdsL1, availProdsL2, platform = self.getAllProducts(self.site, self.tile, repL1, repL2, self.input_dirs)
        availCAMS = self.getCAMSFiles(repCAMS)
        cams = self.filterCAMSByDate(availCAMS,self.start, self.end)
        prodsL1, prodsL2 = self.filterProductsByDate(availProdsL1, availProdsL2, platform, self.start, self.end)
        mode = self.determineMode(prodsL1, prodsL2)
        input_dir = self.createInputDir(repWork, prodsL1 + prodsL2, cams, self.dtm, self.gipp)
        specifier = self.getSpecifier(self.site, self.tile)
        output_dir = os.path.join(repL2, specifier)
        if(not os.path.exists(output_dir)):
            FileSystem.createDirectory(output_dir)
        #self.launchMAJA(exeMaja, input_dir, output_dir, mode, self.tile, self.userconf, self.verbose)
        FileSystem.removeDirectory(input_dir)
        logging.info("=============Start_Maja v%s finished=============" % self.version)

        pass

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("-g", "--gipp", help="Name of the GIPP folder to be used", type=str, required=True)
    parser.add_argument("-t", "--tile", help="Tile number", type=str, required=True)
    parser.add_argument("-i", "--input", help="Product input directory list. This OVERLOADS the L1C dir (and if given) the L2C dir!", nargs="+", type=str, required=False)
    parser.add_argument("-s", "--site", help="Site name. If not specified, the tile number is used directly for finding the L1/L2 product", type=str, required=False)
    parser.add_argument("-f", "--folder", type=str, help="Folder definition file", required=True)
    parser.add_argument("-m", "--dtm", type=str, help="DTM folder. If none is specified, it will be searched for in the code directory", required=False)
    parser.add_argument("-d", "--start", help="Start date for processing in format YYYY-MM-DD (optional)", type=str, required=False, default="2000-01-01")
    parser.add_argument("-e", "--end", help="Start date for processing in format YYYY-MM-DD (optional)", type=str, required=False, default="3000-01-01")
    parser.add_argument("-v", "--verbose", help="Will provide debug logs. Default is false", type=str, default="false")
    args = parser.parse_args()
    
    s = Start_maja(args.input, args.gipp, args.tile, args.site, args.folder, args.dtm, args.start, args.end, args.verbose)
    s.run()