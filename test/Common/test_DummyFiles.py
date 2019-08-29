# -*- coding: utf-8 -*-


import unittest
from Common import DummyFiles
import os


class TestDummyFiles(unittest.TestCase):
    root = os.path.join(os.getcwd(), "DummyFiles")
    platforms = ["S2", "L8", "VE"]

    @classmethod
    def setUpClass(cls):
        from Common import FileSystem
        FileSystem.create_directory(cls.root)

    @classmethod
    def tearDownClass(cls):
        from Common import FileSystem
        FileSystem.remove_directory(cls.root)

    def test_mnt_generation(self):
        import shutil
        gen = DummyFiles.MNTGenerator(self.root)
        gen.generate()
        self.assertTrue(gen.platform in self.platforms)
        self.assertEqual(len(gen.hdr), 1)
        self.assertEqual(len(gen.dbl), 1)
        hdr = gen.hdr[0]
        dbl = gen.dbl[0]
        self.assertTrue(os.path.exists(hdr))
        self.assertTrue(os.path.exists(dbl))
        self.assertTrue("_TEST_AUX_REFDE2_" in hdr)
        self.assertTrue("_TEST_AUX_REFDE2_" in dbl)

        shutil.rmtree(dbl)
        os.remove(hdr)
        self.assertFalse(os.path.exists(hdr))
        self.assertFalse(os.path.exists(dbl))

    def test_cams_generation(self):
        import shutil
        gen = DummyFiles.CAMSGenerator(self.root)
        gen.generate()
        self.assertTrue(gen.platform in self.platforms)
        self.assertEqual(len(gen.hdr), 1)
        self.assertEqual(len(gen.dbl), 1)
        hdr = gen.hdr[0]
        dbl = gen.dbl[0]
        self.assertTrue(os.path.exists(hdr))
        self.assertTrue(os.path.exists(dbl))
        self.assertTrue("_TEST_EXO_CAMS_" in hdr)
        self.assertTrue("_TEST_EXO_CAMS_" in dbl)

        shutil.rmtree(dbl)
        os.remove(hdr)
        self.assertFalse(os.path.exists(hdr))
        self.assertFalse(os.path.exists(dbl))

    def test_gipp_generation_cams(self):
        import shutil
        from Common import FileSystem
        gen = DummyFiles.GippGenerator(self.root)
        gen.generate()
        self.assertTrue(gen.platform in self.platforms)

        lengths_hdr = {"VE": 35, "L8": 35, "S2": 69}
        lengths_dbl = {"VE": 30, "L8": 30, "S2": 60}

        self.assertEqual(len(gen.hdr), lengths_hdr[gen.platform])
        self.assertEqual(len(gen.dbl), lengths_dbl[gen.platform])

        hdr_types = ["ALBD", "DIFT", "DIRT", "TOCR", "WATV"]
        eef_types = ["COMM", "SITE", "SMAC", "EXTL", "QLTL"]
        base = os.path.dirname(gen.dbl[0])
        for ftype in hdr_types:
            hdr = FileSystem.get_file(root=base, filename="*" + ftype + r"*.HDR")
            self.assertIsNotNone(hdr)
            self.assertTrue("_TEST_GIP_" in hdr)
            dbl = FileSystem.get_file(root=base, filename="*" + ftype + r"*.DBL.DIR")
            self.assertIsNotNone(dbl)
            self.assertTrue("_TEST_GIP_" in dbl)
        for ftype in eef_types:
            eef = FileSystem.get_file(root=base, filename="*" + ftype + r"*.EEF")
            self.assertIsNotNone(eef)
            self.assertTrue("_TEST_GIP_" in eef)

        for dbl in gen.dbl:
            shutil.rmtree(dbl)
            self.assertFalse(os.path.exists(dbl))
        for hdr in gen.hdr:
            os.remove(hdr)
            self.assertFalse(os.path.exists(hdr))

    def test_gipp_generation_nocams(self):
        import shutil
        from Common import FileSystem
        gen = DummyFiles.GippGenerator(self.root)
        gen.generate(cams=False)
        self.assertTrue(gen.platform in self.platforms)

        lengths_hdr = {"VE": 10, "L8": 10, "S2": 19}
        lengths_dbl = {"VE": 5, "L8": 5, "S2": 10}

        self.assertEqual(len(gen.hdr), lengths_hdr[gen.platform])
        self.assertEqual(len(gen.dbl), lengths_dbl[gen.platform])

        hdr_types = ["ALBD", "DIFT", "DIRT", "TOCR", "WATV"]
        eef_types = ["COMM", "SITE", "SMAC", "EXTL", "QLTL"]
        base = os.path.dirname(gen.dbl[0])
        for ftype in hdr_types:
            hdr = FileSystem.get_file(root=base, filename="*" + ftype + r"*.HDR")
            self.assertIsNotNone(hdr)
            self.assertTrue("_TEST_GIP_" in hdr)
            dbl = FileSystem.get_file(root=base, filename="*" + ftype + r"*.DBL.DIR")
            self.assertIsNotNone(dbl)
            self.assertTrue("_TEST_GIP_" in dbl)
        for ftype in eef_types:
            eef = FileSystem.get_file(root=base, filename="*" + ftype + r"*.EEF")
            self.assertIsNotNone(eef)
            self.assertTrue("_TEST_GIP_" in eef)

        for dbl in gen.dbl:
            shutil.rmtree(dbl)
            self.assertFalse(os.path.exists(dbl))
        for hdr in gen.hdr:
            os.remove(hdr)
            self.assertFalse(os.path.exists(hdr))

    def test_gipp_generation_cams_tm(self):
        import shutil
        from Common import FileSystem
        gen = DummyFiles.GippGenerator(self.root)
        gen.generate(mission="tm")
        self.assertTrue(gen.platform in self.platforms)

        lengths_hdr = {"S2": 75}
        lengths_dbl = {"S2": 60}

        self.assertEqual(len(gen.hdr), lengths_hdr[gen.platform])
        self.assertEqual(len(gen.dbl), lengths_dbl[gen.platform])

        hdr_types = ["ALBD", "DIFT", "DIRT", "TOCR", "WATV"]
        eef_types = ["COMM", "SITE", "SMAC", "EXTL", "QLTL"]
        base = os.path.dirname(gen.dbl[0])
        for ftype in hdr_types:
            hdr = FileSystem.get_file(root=base, filename="*" + ftype + r"*.HDR")
            self.assertIsNotNone(hdr)
            self.assertTrue("_TEST_GIP_" in hdr)
            dbl = FileSystem.get_file(root=base, filename="*" + ftype + r"*.DBL.DIR")
            self.assertIsNotNone(dbl)
            self.assertTrue("_TEST_GIP_" in dbl)
        for ftype in eef_types:
            eef = FileSystem.get_file(root=base, filename="*" + ftype + r"*.EEF")
            self.assertIsNotNone(eef)
            self.assertTrue("_TEST_GIP_" in eef)

        n_l2comm = len(FileSystem.find("*L2COMM*", base))
        self.assertEqual(n_l2comm, 4)
        n_qltl = len(FileSystem.find("*CKQLTL*", base))
        self.assertEqual(n_qltl, 4)
        n_extl = len(FileSystem.find("*CKEXTL*", base))
        self.assertEqual(n_extl, 4)
        for dbl in gen.dbl:
            shutil.rmtree(dbl)
            self.assertFalse(os.path.exists(dbl))
        for hdr in gen.hdr:
            os.remove(hdr)
            self.assertFalse(os.path.exists(hdr))

    def test_s2_l1_generation(self):
        import shutil
        gen = DummyFiles.L1Generator(self.root, platform="S2")
        gen.generate()
        self.assertTrue(os.path.exists(gen.mtd))
        self.assertTrue(os.path.exists(gen.prod))
        self.assertTrue("MTD_MSIL1C.xml" in os.path.basename(gen.mtd))
        self.assertTrue("MSIL1C" in gen.prod)

        shutil.rmtree(gen.prod)
        self.assertFalse(os.path.exists(gen.prod))

    def test_spot4_l1_generation(self):
        import shutil
        gen = DummyFiles.L1Generator(self.root, platform="SPOT4")
        gen.generate()
        self.assertTrue(os.path.exists(gen.mtd))
        self.assertTrue(os.path.exists(gen.prod))
        self.assertTrue("MTD_MSIL1C.xml" in os.path.basename(gen.mtd))
        self.assertTrue("SPOT4" in gen.prod)

        shutil.rmtree(gen.prod)
        self.assertFalse(os.path.exists(gen.prod))

    def test_spot5_l1_generation(self):
        import shutil
        gen = DummyFiles.L1Generator(self.root, platform="SPOT5")
        gen.generate()
        self.assertTrue(os.path.exists(gen.mtd))
        self.assertTrue(os.path.exists(gen.prod))
        self.assertTrue("MTD_MSIL1C.xml" in os.path.basename(gen.mtd))
        self.assertTrue("SPOT5" in gen.prod)

        shutil.rmtree(gen.prod)
        self.assertFalse(os.path.exists(gen.prod))

    def test_l2_generation(self):
        import shutil
        gen = DummyFiles.L2Generator(self.root)
        gen.generate()
        self.assertTrue(os.path.exists(gen.mtd))
        self.assertTrue(os.path.exists(gen.prod))
        self.assertTrue("_MTD_ALL.xml" in os.path.basename(gen.mtd))
        self.assertTrue(os.path.dirname(gen.mtd), gen.prod)

        shutil.rmtree(gen.prod)
        self.assertFalse(os.path.exists(gen.prod))



if __name__ == '__main__':
    unittest.main()
