# -*- coding: utf-8 -*-

import unittest
from Common import ImageIO
import numpy as np
import os


class TestFileIO(unittest.TestCase):

    def testWriteGeoTiff(self):
        coordinates = (652594.9112913811, 10.00887639510383, 0,
                       5072876.717295351, 0, -9.974893672262251)
        projection = 'PROJCS["WGS 84 / UTM zone 31N",\
                        GEOGCS["WGS 84",DATUM["WGS_1984",\
                        SPHEROID["WGS 84",6378137,298.257223563,\
                        AUTHORITY["EPSG","7030"]],\
                        AUTHORITY["EPSG","6326"]],\
                        PRIMEM["Greenwich",0,\
                        AUTHORITY["EPSG","8901"]],\
                        UNIT["degree",0.0174532925199433,\
                        AUTHORITY["EPSG","9122"]],\
                        AUTHORITY["EPSG","4326"]],\
                        PROJECTION["Transverse_Mercator"],\
                        PARAMETER["latitude_of_origin",0],\
                        PARAMETER["central_meridian",3],\
                        PARAMETER["scale_factor",0.9996],\
                        PARAMETER["false_easting",500000],\
                        PARAMETER["false_northing",0],\
                        UNIT["metre",1,AUTHORITY["EPSG","9001"]],\
                        AXIS["Easting",EAST],AXIS["Northing",NORTH],\
                        AUTHORITY["EPSG","32631"]]'
        height = 200
        width = 100
        dstImage = np.ones((height, width), np.int16)
        path = os.path.join(os.getcwd(), "testWriteGeoTiff.tif")
        #Write Image and check return code
        self.assertEqual(ImageIO.writeGTiff(dstImage, path, projection, coordinates), 0)
        self.assertTrue(os.path.exists(path))
        
        arrRead, driverRead = ImageIO.tiffToArray(path, arrayOnly=False)
        self.assertTrue((arrRead == dstImage).all())
        coordinatesRead = driverRead.GetGeoTransform()
        projectionRead = driverRead.GetProjection()
        self.assertEqual(coordinatesRead, coordinates)
        #Compare projections by removing all spaces cause of multiline string
        self.assertEqual(projectionRead.replace(" ", ""), projection.replace(" ", ""))
        try:
            os.remove(path)
        except:
            pass
        #Check if file removed
        self.assertFalse(os.path.exists(path))
        
    def testFaultyGeotransform(self):
        coordinates = (652594.9112913811, 10.00887639510383, 0,
                       5072876.717295351, 0) #Missing one value
        projection = ''
        height = 200
        width = 100
        dstImage = np.ones((height, width), np.int16)
        path = os.path.join(os.getcwd(), "testWriteGeoTiff.tif")
        #Check geotransform wrong:
        with self.assertRaises(ValueError):
            self.assertEqual(ImageIO.writeGTiff(dstImage, path, projection, coordinates), 0)
        coordinates = (652594.9112913811, 10.00887639510383, 0,
                       5072876.717295351, 0, -9.974893672262251)
        #Check projection wrong:
        with self.assertRaises(ValueError):
            self.assertEqual(ImageIO.writeGTiff(dstImage, path, projection, coordinates), 0)


if __name__ == '__main__':
    unittest.main()
