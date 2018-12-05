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

class Start_maja(object):
    def __init__(self, context, tile, site, orbit, folder, start, verbose):
        """
        Init the instance using the old start_maja parameters
        """
        self.context = context
        if(not os.path.isdir(self.context)):
            raise OSError("Cannot find GIPP folder: %s" % self.context)
        if(tile[0] == "T" and len(tile) == 6 and tile[1:2].isdigit()):
            self.tile = tile[1:] #Remove the T
        else:
            self.tile = tile
        self.site = site
        if(orbit == None):
            #Get orbit
        else:
            self.orbit = orbit
        self.folder = folder
        self.start = start
        self.verbose = verbose
        pass
    
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
        Read contents of the folders.txt file
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
            print("WARNING: repCAMS is missing. Processing without CAMS")
            repCAMS = None
        
        return repWork, repL1, repL2, exeMaja, repCAMS
    
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
        self.readFoldersFile(self.folder)
        self.createInputDir()
        pass

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("-c", "--context", help="Name of the GIPP folder to be used", type=str, required=True)
    parser.add_argument("-t", "--tile", help="Tile number", type=str, required=True)
    parser.add_argument("-s", "--site", help="Site name", type=str, required=True)
    parser.add_argument("-o", "--orbit", help="Orbit number", type=str, required=False)
    parser.add_argument("-f", "--folder", type=str, help="Folder definition file", required=True)
    parser.add_argument("-d", "--start", help="Start date for processing (optional)", type=str, required=False)
    parser.add_argument("-e", "--end", help="End date for processing (optional)", type=str, required=False)
    parser.add_argument("-v", "--verbose", help="Will provide debug logs. Default is false", type=str, default="false")
    args = parser.parse_args()
    
    s = Start_maja(args.context, args.tile, args.site, args.orbit, args.folder, args.start, args.verbose)
    s.run()