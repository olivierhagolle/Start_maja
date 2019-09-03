# -*- coding: utf-8 -*-

import unittest
from Common import ImageIO
import numpy as np
import os


class TestFileIO(unittest.TestCase):

    def setUp(self):
        self.coordinates = (652594.9112913811, 10.00887639510383, 0,
                            5072876.717295351, 0, -9.974893672262251)
        self.projection = 'PROJCS["WGS 84 / UTM zone 31N",\
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
        self.height = 200
        self.width = 100

    def test_write_read_geotiff(self):
        from Common import FileSystem

        img = np.ones((self.height, self.width), np.int16)
        path = os.path.join(os.getcwd(), "test_write_read_geotiff.tif")
        # Write Image and check return code
        ImageIO.write_geotiff(img, path, self.projection, self.coordinates)
        self.assertTrue(os.path.exists(path))
        
        img_read, driver = ImageIO.tiff_to_array(path, array_only=False)
        self.assertTrue((img_read == img).all())
        geotransform_read = driver.GetGeoTransform()
        projection_read = driver.GetProjection()
        self.assertEqual(geotransform_read, self.coordinates)
        # Compare projections by removing all spaces cause of multiline string
        self.assertEqual(projection_read.replace(" ", ""), self.projection.replace(" ", ""))
        FileSystem.remove_file(path)
        # Check if file removed
        self.assertFalse(os.path.exists(path))
        
    def test_faulty_geotransform_projection(self):
        from Common import FileSystem

        coordinates = (652594.9112913811, 10.00887639510383, 0,
                       5072876.717295351, 0)  # Missing one value
        projection = ''
        height = 200
        width = 100
        img = np.ones((height, width), np.int16)
        path = os.path.join(os.getcwd(), "test_faulty_geotransform_projection.tif")
        # Check geotransform wrong:
        with self.assertRaises(ValueError):
            ImageIO.write_geotiff(img, path, projection, coordinates)
        coordinates = (652594.9112913811, 10.00887639510383, 0,
                       5072876.717295351, 0, -9.974893672262251)
        # Check projection wrong:
        with self.assertRaises(ValueError):
            ImageIO.write_geotiff(img, path, projection, coordinates)
        FileSystem.remove_file(path)
        self.assertFalse(os.path.exists(path))

    def test_get_epsg(self):
        from Common import FileSystem
        epsg_ref = 32631
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
                        AUTHORITY["EPSG","%s"]]' % epsg_ref
        img = np.ones((self.height, self.width), np.int16)
        path = os.path.join(os.getcwd(), "test_epsg.tif")
        # Write Image and check return code
        ImageIO.write_geotiff(img, path, projection, self.coordinates)
        self.assertTrue(os.path.exists(path))

        img_read, driver = ImageIO.tiff_to_array(path, array_only=False)
        self.assertEqual(epsg_ref, ImageIO.get_epsg(driver))
        FileSystem.remove_file(path)
        # Check if file removed
        self.assertFalse(os.path.exists(path))

    def test_get_resolution(self):
        from Common import FileSystem
        img = np.ones((self.height, self.width), np.int16)
        path = os.path.join(os.getcwd(), "test_get_resolution.tif")
        # Write Image and check return code
        ImageIO.write_geotiff(img, path, self.projection, self.coordinates)
        self.assertTrue(os.path.exists(path))

        img_read, driver = ImageIO.tiff_to_array(path, array_only=False)
        ul, lr = ImageIO.get_ul_lr(driver)
        res_expected = (self.coordinates[1], self.coordinates[-1])
        self.assertEqual(res_expected, ImageIO.get_resolution(driver))

        FileSystem.remove_file(path)
        # Check if file removed
        self.assertFalse(os.path.exists(path))

    def test_get_ul_lr(self):
        from Common import FileSystem
        img = np.ones((self.height, self.width), np.int16)
        path = os.path.join(os.getcwd(), "test_get_ul_lr.tif")
        # Write Image and check return code
        ImageIO.write_geotiff(img, path, self.projection, self.coordinates)
        self.assertTrue(os.path.exists(path))

        img_read, driver = ImageIO.tiff_to_array(path, array_only=False)
        ul, lr = ImageIO.get_ul_lr(driver)
        self.assertEqual(ul, (652594.9112913811, 5072876.717295351))
        self.assertEqual(lr, (653595.7989308914, 5070881.738560899))

        FileSystem.remove_file(path)
        # Check if file removed
        self.assertFalse(os.path.exists(path))

    def test_transform_point_lat_lon(self):
        from Common import FileSystem
        img = np.ones((self.height, self.width), np.int16)
        path = os.path.join(os.getcwd(), "test_transform_point_lat_lon.tif")
        # Write Image and check return code
        ImageIO.write_geotiff(img, path, self.projection, self.coordinates)
        self.assertTrue(os.path.exists(path))

        img_read, driver = ImageIO.tiff_to_array(path, array_only=False)
        center = (653095.355, 5071879.228)
        lat_lon_expected = (4.9694934619557145, 45.78349724618419, 0.0)
        lat_lon_calc = ImageIO.transform_point(center, driver, new_epsg=4326)
        self.assertEqual(lat_lon_expected, lat_lon_calc)
        FileSystem.remove_file(path)
        # Check if file removed
        self.assertFalse(os.path.exists(path))

if __name__ == '__main__':
    unittest.main()
