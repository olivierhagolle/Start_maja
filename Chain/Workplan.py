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

    def __init__(self, wdir, outdir, l1, **kwargs):
        supported_params = {
            param
            for param in ("cams", "meteo")
            if kwargs.get(param, None) is not None
        }
        # Check if the directories exist:
        assert os.path.isdir(wdir)
        assert os.path.isdir(outdir)

        self.wdir = wdir
        self.outdir = outdir
        self.l1 = l1
        self.aux_files = [kwargs[key] for key in supported_params]

    def __str__(self):
        return str("%8s | %5s | %8s | %70s | %15s" % (self.l1.get_date(),
                                                      self.l1.get_tile(),
                                                      self.mode, self.l1.base, "from previous"))

    # TODO Write this for each mode (and update params)
    def execute(self, dtm, gipp, conf):
        """
        Run the workplan with its given parameters
        """
        raise NotImplementedError

    def get_dirname(self):
        """
        Create a hash of the product name in order to have a unique folder name
        :return: The product name as hex-hash
        """
        import hashlib
        return hashlib.md5(self.l1.base.encode("utf-8")).hexdigest()

    def create_working_dir(self):
        """
        Set up all files of the input directory, which are:
            Product (1C and eventually 2A)
            GIPPs
            DTM
            (CAMS) if existing
        :return:
        """
        from Common.FileSystem import create_directory, symlink

        input_dir = os.path.join(self.wdir, "Start_maja_" + self.get_dirname())
        create_directory(input_dir)
        # TODO Link stuff
        for prod, i in products:
            symlink(prod, os.path.join(input_dir, os.path.basename(prod)))
        for f in cams:
            symlink(f, os.path.join(input_dir, os.path.basename(f)))
        for f in dtm:
            symlink(f, os.path.join(input_dir, os.path.basename(f)))
        for gipp in os.listdir(gipps):
            symlink(os.path.join(gipps, gipp), os.path.join(input_dir, os.path.basename(gipp)))
        return input_dir

    # TODO revise this if needed:

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
        
    def __str__(self):
        from Common import DateConverter as dc
        return str("%8s | %5s | %8s | %70s | %15s" % (dc.datetimeToStringShort(self.date), self.tile, self.mode, bname(self.L1[0]), "No previous L2"))
    
class ModeBackward(Workplan):
    mode = "BACKWARD"
    
    def execute(self):
        """
        Run the workplan with its given parameters
        """
        raise NotImplementedError
        
    def __str__(self):
        from Common import DateConverter as dc
        return str("%8s | %5s | %8s | %70s | %15s" % (dc.datetimeToStringShort(self.date), self.tile, self.mode, bname(self.L1[0][0]), "%s products" % len(self.L1)))
    
class ModeNominal(Workplan):
    mode = "NOMINAL"
    
    def execute(self):
        """
        Run the workplan with its given parameters
        """
        raise NotImplementedError


if __name__ == "__main__":
    pass
