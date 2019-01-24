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

class Workplan(object):
    productsL1 = []
    productsL2 = []
    cams = []
    
    def execute(self):
        """
        Run the workplan with its given parameters
        """
        raise NotImplementedError

class ModeInit(Workplan):
    
    def execute(self):
        """
        Run the workplan with its given parameters
        """
        raise NotImplementedError
        
class ModeBackward(Workplan):
    
    def execute(self):
        """
        Run the workplan with its given parameters
        """
        raise NotImplementedError
        
class ModeNominal(Workplan):
    productsL1 = []
    productsL2 = []
    cams = []
    
    def execute(self):
        """
        Run the workplan with its given parameters
        """
        raise NotImplementedError

if __name__ == "__main__":
    pass
