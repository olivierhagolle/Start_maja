#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Copyright (C) CNES - All Rights Reserved
This file is subject to the terms and conditions defined in
file 'LICENSE.md', which is part of this source code package.

Author:         Peter KETTIG <peter.kettig@cnes.fr>
Project:        Start_maja, CNES
Created on:     Fri Jan 11 16:57:37 2019
"""

import os
import logging

class Workplan(object):
    productsL1 = []
    productsL2 = []
    cams = []
    dtm = None
    tile = None
    conf = None
    mode = None
    
    def __init__(self, L1, L2, CAMS, DTM, tile, conf):
        self.productsL1 = L1
        self.productsL2 = L2
        self.cams = CAMS
        self.dtm = DTM
        self.tile = tile
        self.conf = conf
        pass
    
    def __str__(self):
        return str("%5s | %8s | %8s | %8s" % (self.tile, self.mode, self.productsL1, self.productsL2))
    
    def execute(self):
        """
        Run the workplan with its given parameters
        """
        raise NotImplementedError

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
        """
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

class ModeInit(Workplan):
    mode = "INIT"
    
    def execute(self):
        """
        Run the workplan with its given parameters
        """
        raise NotImplementedError
        
class ModeBackward(Workplan):
    mode = "BACKWARD"
    
    def execute(self):
        """
        Run the workplan with its given parameters
        """
        raise NotImplementedError
        
class ModeNominal(Workplan):
    mode = "NOMINAL"
    
    def execute(self):
        """
        Run the workplan with its given parameters
        """
        raise NotImplementedError

if __name__ == "__main__":
    pass
