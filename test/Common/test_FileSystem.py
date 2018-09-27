# -*- coding: utf-8 -*-

from Unittest import LoggedTestCase
from Unittest import testFunction

from Common import FileSystem
import os

class testFileSystem(LoggedTestCase.LoggedTestCase):

    @testFunction.test_function
    def testCreateDirectory(self):
       path = os.path.join(os.getcwd(), "testCreateDirectory")
       self.assertEqual(FileSystem.createDirectory(os.getcwd()), 1) #Return code 1
       
       self.assertEqual(FileSystem.createDirectory(path), 0) #Return code 0
       self.assertTrue(os.path.isdir(path))
       self.assertEqual(FileSystem.removeDirectory(path), 0) #Return code 0
       self.assertFalse(os.path.exists(path))
