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
        ImageIO.write_geotiff(img, path, self.projection, self.coordinates)
        self.assertTrue(os.path.exists(path))

        img_read, driver = ImageIO.tiff_to_array(path, array_only=False)
        res_expected = (self.coordinates[1], self.coordinates[-1])
        self.assertEqual(res_expected, ImageIO.get_resolution(driver))

        FileSystem.remove_file(path)
        # Check if file removed
        self.assertFalse(os.path.exists(path))

    def test_get_ul_lr(self):
        from Common import FileSystem
        img = np.ones((self.height, self.width), np.int16)
        path = os.path.join(os.getcwd(), "test_get_ul_lr.tif")
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
        center = (653095.355, 5071879.228)
        lat_lon_expected = (45.78349724618419, 4.9694934619557145)
        lat_lon_calc = ImageIO.transform_point(center, old_epsg=32631, new_epsg=4326)
        self.assertEqual(lat_lon_expected, lat_lon_calc)

    def test_gdal_merge(self):
        from Common import FileSystem
        img = np.ones((self.height, self.width), np.int16)
        path = os.path.join(os.getcwd(), "test_gdal_merge.tif")
        empty = os.path.join(os.getcwd(), "empty.tif")

        ImageIO.write_geotiff(img, path, self.projection, self.coordinates)
        self.assertTrue(os.path.exists(path))
        ImageIO.gdal_merge(empty, path, init="0", createonly=True, q=True)
        img_read, driver = ImageIO.tiff_to_array(empty, array_only=False)
        np.testing.assert_almost_equal(img_read, 0)
        FileSystem.remove_file(path)
        FileSystem.remove_file(empty)
        self.assertFalse(os.path.exists(path))
        self.assertFalse(os.path.exists(empty))

    def test_gdal_buildvrt(self):
        from Common import FileSystem
        img = np.ones((self.height, self.width), np.int16)
        path = os.path.join(os.getcwd(), "test_gdal_buildvrt.tif")
        vrt = os.path.join(os.getcwd(), "test_vrt.vrt")

        ImageIO.write_geotiff(img, path, self.projection, self.coordinates)
        self.assertTrue(os.path.exists(path))
        ImageIO.gdal_buildvrt(vrt, path, q=True)
        img_read, driver = ImageIO.tiff_to_array(vrt, array_only=False)
        np.testing.assert_almost_equal(img_read, img)
        FileSystem.remove_file(path)
        FileSystem.remove_file(vrt)

    def test_gdal_translate(self):
        from Common import FileSystem
        img = np.ones((self.height, self.width), np.int16)
        path = os.path.join(os.getcwd(), "test_gdal_translate.tif")
        scaled = os.path.join(os.getcwd(), "scaled.tif")
        out_resolution = (20, -20)
        ImageIO.write_geotiff(img, path, self.projection, self.coordinates)
        self.assertTrue(os.path.exists(path))
        ImageIO.gdal_translate(path, scaled, tr=" ".join(str(e) for e in out_resolution), scale="0 1 0 255", q=True)
        img_read, driver = ImageIO.tiff_to_array(scaled, array_only=False)
        self.assertEqual(ImageIO.get_resolution(driver), out_resolution)
        np.testing.assert_almost_equal(img_read, 255)
        FileSystem.remove_file(path)
        FileSystem.remove_file(scaled)

    def test_gdal_warp(self):
        from Common import FileSystem
        img = np.ones((self.height, self.width), np.int16)
        img_rescaled = np.ones((int(self.height/2), int(self.width/2)), np.int16)
        out_resolution = (20, -20)
        path = os.path.join(os.getcwd(), "test_gdal_warp.tif")
        scaled = os.path.join(os.getcwd(), "res_changed.tif")
        ImageIO.write_geotiff(img, path, self.projection, self.coordinates)
        self.assertTrue(os.path.exists(path))
        ImageIO.gdal_warp(path, scaled,
                          tr=" ".join(str(e) for e in out_resolution),
                          r="max", q=True)
        img_read, driver = ImageIO.tiff_to_array(scaled, array_only=False)
        self.assertEqual(ImageIO.get_resolution(driver), out_resolution)
        np.testing.assert_almost_equal(img_read, img_rescaled)
        FileSystem.remove_file(path)
        FileSystem.remove_file(scaled)


if __name__ == '__main__':
    unittest.main()
