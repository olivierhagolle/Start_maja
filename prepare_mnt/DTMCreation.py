#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Copyright (C) CNES - All Rights Reserved
This file is subject to the terms and conditions defined in
file 'LICENSE.md', which is part of this source code package.

Author:         Peter KETTIG <peter.kettig@cnes.fr>, Pierre LASSALLE <pierre.lassalle@cnes.fr>
Project:        StartMaja, CNES
Created on:     Tue Sep 11 15:31:00 2018
"""

import sys
import os
# TODO Check if this is needed:
# sys.path.append(os.path.join(os.path.dirname(os.path.realpath(__file__)), '..'))  # Import relative modules
from Common import FileSystem


class DTMCreator:
    """
    Class to create the DTM based on the SRTMs, Water-masks and Metadata of a
    L1 product file downloaded. The output DTM contains an HDR File and a Folder
    both of filename *AUX_REFDE2*, which are created in the given output path
    """
    dem_types = ["SRTM"]

    def __init__(self, product_path, dem_dir, water_dir, type_dem, coarse_res):
        """
        Init the DTMCreator by finding the Metadata file assiociated with the product
        :param product: The full path to the L1C/L2A product folder
        :type product: string
        :param dem_dir: DEM directory
        :param water_dir: Water-mask directory
        :param type_dem: Type of mnt
        :param coarse_res: Coarse resolution of the MNT in Meter
        :type coarse_res: int
        """
        from Chain import Product
        self.product = Product.MajaProduct(product_path)
        if not self.product:
            raise ValueError("Unknown product found for path %s" % product_path)
        self.site = self.product.get_dem_info()
        self.dem_dir = dem_dir
        FileSystem.create_directory(self.dem_dir)
        self.water_dir = water_dir
        FileSystem.create_directory(self.water_dir)
        if type_dem.upper() not in self.dem_types:
            raise ValueError("Unknown DEM type found: %s" % type_dem)
        self.type_dem = type_dem
        self.coarse_res = int(coarse_res)

    def get_dem_data(self):
        """
        Get the DEM raw-data from the given directory. If not existing, an attempt will be made to download
        it automatically.
        :return:
        """
        pass

    def get_water_data(self):
        """
        Get the Water-mask raw-data from the given directory. If not existing, an attempt will be made to download
        it automatically.
        :return:
        """
        pass

    def run(self, outdir, tempout):
        """
        Run the DTM Creation using the two modules tuilage_mnt_eau*py and lib_mnt.py
        :param outdir: Output directory
        :param tempout: Directory to write temporary files to
        """
        # TODO Move this to the respective get_site() functions:
        from osgeo import gdal
        # Script runs fine with gdal >= 2.1.x
        if int(gdal.VersionInfo()) <= 2010000:
            raise ImportError("Please update your GDAL version to >2.1")
        # TODO Verify this:
        # Bug with v2.3.0 results in errors within the script:
        if int(gdal.VersionInfo()) == 2030000:
            raise ImportError("DTMCreation can not run on GDAL 2.3.0. Please select another version")

        # TODO:
        # - Write get_site() for each product type
        # - Write get_site() for kml
        # - In main: Run get_site() for the given input (kml/product)
        # - In run: Interface with libmnt + download the necessary srtm files
        # - In run: Download the needed GSW tiles and prepare tiled water-mask
        # - Put mnt into given mnt directory
        # - Interface new DTMCreation with new StartMaja

        print("Finished DTM creation for site/tile %s" % (self.site.name))


if __name__ == "__main__":
    import sys
    assert sys.version_info >= (2, 7)
    import argparse
    parser = argparse.ArgumentParser()
    tmp_dir = os.path.join("tmp", "prepare_mnt")
    parser.add_argument("-p", "--product",
                        help="The path to a Landsat-8, Venus or Sentinel-2 L1C/L2A product folder.",
                        required=True, type=str)
    parser.add_argument("-d", "--dem_dir",
                        help="The path to the folder containing the extracted SRTM zip-archives."
                             "If not existing, an attempt will be made to download them.",
                        default=tmp_dir, required=True, type=str)
    parser.add_argument("-w", "--water_dir",
                        help="The path to the folder containing the GSW occurence .tif-files."
                             "If not existing, an attempt will be made to download them.",
                        default=tmp_dir, required=True, type=str)
    parser.add_argument("-o", "--out", help="Output directory. Default is the current directory.",
                        default=os.getcwd(), required=True, type=str)
    parser.add_argument("-t", "--tempout", help="Temporary working directory."
                                                "If none is given, it is set to /tmp/prepare_mnt",
                        default=tmp_dir, required=True, type=str)
    parser.add_argument("-t", "--type_dem",
                        help="DEM type. Default is 'SRTM'. Other options are:"
                             "[TBD]",
                        default="SRTM", required=True, type=str)
    parser.add_argument("-c", "--coarse_res",
                        help="Coarse resolution in meters. Default is 240",
                        default=240, required=True, type=int)
    # TODO Check the syntax for this:
    parser.add_argument("--raw_resolution",
                        help="Do not round the product resolution to the next integer",
                        action="store", required=True)
    parser.add_argument("--nodownload",
                        help="Do not attempt any downloading of the files.",
                        action="store", required=True)

    args = parser.parse_args()

    # TODO run: Try getting local files. Then download. Then process.
    # TODO split run into run and create (once all files are available)
    creator = DTMCreator(args.product, args.dem_dir, args.water_dir, args.type_dem, args.coarse_res)
    creator.run(args.out, args.tempout)