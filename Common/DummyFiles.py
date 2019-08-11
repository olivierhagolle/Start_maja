# -*- coding: utf-8 -*-
"""
Created on Thu Jul  5 17:42:44 2018

@author: akynos
"""

import os


def random_tile(platform="S2"):
    """
    Create a random tile string for a given platform. For 'S2': T12ABC, for 'L8': 192820, for 'VE': ABCDE
    :param platform: Return a tile corresponding to the given platform
    :return: String compliant with the given platform
    """
    import string
    import random

    letters = string.ascii_uppercase
    tile = "T" + str(random.randint(0, 99)).zfill(2) + ''.join(random.choice(letters) for _ in range(3))
    if platform == "S2":
        return tile
    elif platform == "L8":
        number = str(random.randint(0, 999999)).zfill(6)
        return random.choice([number, tile])
    elif platform == "VE":
        return ''.join(random.choice(letters) for _ in range(5))


def random_platform(product_level=None):
    import random
    if product_level == "L1C":
        return "S2"
    return random.choice(["S2", "VE", "L8"])


def random_date():
    import random
    from datetime import datetime, timedelta
    date = datetime(2015, 1, 1) + timedelta(days=random.randint(0, 10000),
                                            hours=random.randint(10, 12),
                                            minutes=random.randint(0, 60),
                                            seconds=random.randint(0, 60))
    return date


class DummyGenerator(object):
    """
    Base class for all dummy generators
    """
    def __init__(self, root, date=None, tile=None, platform=random_platform()):
        self.root = root
        if not date:
            self.date = random_date()
        else:
            self.date = date
        if platform[:2].upper() == "S2":
            self.platform = "S2"
        elif platform[:2].upper() == "L8":
            self.platform = "L8"
        elif platform[:2].upper() == "VE":
            self.platform = "VE"
        else:
            raise ValueError("Unknown platform found: %s" % platform)
        if not tile:
            self.tile = random_tile(platform=platform)
        else:
            self.tile = tile

    def generate(self, **kwargs):
        raise NotImplementedError


class DummyEarthExplorer(DummyGenerator):
    """
    Base class for all EarthExplorer-like files
    """
    def __init__(self, root, date=None, tile=None, platform=random_platform()):
        super(DummyEarthExplorer, self).__init__(root, date, tile, platform)
        self.hdr = []
        self.dbl = []

    def get_mission(self):
        """
        Return a random Mission name
        :return:
        """
        import random
        mission_choices = {"tm": {"S2": "SENTINEL-2"},
                           "muscate": {"S2": "SENTINEL2", "L8": "LANDSAT8", "VE": "VENUS"},
                           "natif": {"S2": "SENTINEL-2", "L8": "LANDSAT_8", "VE": "VENuS"}
                           }
        mtype = random.choice(["muscate", "natif"])
        return mission_choices[mtype][self.platform]

    def create_dummy_hdr(self, file_path, mission=None):
        """
        Create a dummy HDR file with only the "Mission" field in it.
        :param file_path: The full path to the file that should be written
        :param mission: The content of the 'Mission' field to be set.
        """
        import random
        from xml.etree import ElementTree
        platform_hdr = {"S2": random.choice(["SENTINEL2_", "SENTINEL-2_"]),
                        "VE": random.choice(["VENUS", "VENuS"]),
                        "L8": random.choice(["LANDSAT8", "LANDSAT_8"])}
        mission = mission if mission else platform_hdr[self.platform]
        root = ElementTree.Element("Earth_Explorer_Header")
        sub = ElementTree.SubElement(root, "Fixed_Header")
        ElementTree.SubElement(sub, "Mission").text = mission
        ElementTree.SubElement(root, "Variable_Header")
        tree = ElementTree.ElementTree(root)
        tree.write(file_path)

    def generate(self, **kwargs):
        # Pass this on
        raise NotImplementedError


class MNTGenerator(DummyEarthExplorer):
    """
    Class to create a single dummy MNT.
    """
    def generate(self, **kwargs):
        import random
        from Common import FileSystem
        mission_param = kwargs.get("mission", self.get_mission())
        mission_specifier = "_" if self.platform == "S2" else ""
        basename = "_".join([self.platform + mission_specifier,
                             "TEST", "AUX", "REFDE2", self.tile,
                             str(random.randint(0, 1000)).zfill(4)])
        self.dbl.append(os.path.join(self.root, basename + ".DBL.DIR"))
        self.hdr.append(os.path.join(self.root, basename + ".HDR"))
        FileSystem.create_directory(self.dbl[-1])
        self.create_dummy_hdr(self.hdr[-1], mission=mission_param + mission_specifier)


class CAMSGenerator(DummyEarthExplorer):
    """
    Class to create a single dummy CAMS file.
    """
    def generate(self, **kwargs):
        from datetime import datetime
        from Common import FileSystem
        end_date = datetime(2099, 1, 1, 23, 59, 59)
        mission_param = kwargs.get("mission", self.get_mission())
        mission_specifier = "_" if self.platform == "S2" else ""
        basename = "_".join([self.platform + mission_specifier,
                             "TEST", "EXO", "CAMS",
                             self.date.strftime("%Y%m%dT%H%M%S"),
                             end_date.strftime("%Y%m%dT%H%M%S")])
        self.dbl.append(os.path.join(self.root, basename + ".DBL.DIR"))
        self.hdr.append(os.path.join(self.root, basename + ".HDR"))
        FileSystem.create_directory(self.dbl[-1])
        self.create_dummy_hdr(self.hdr[-1], mission=mission_param + mission_specifier)


class GippGenerator(DummyEarthExplorer):
    """
    Class to create a single dummy CAMS file.
    """
    def _create_hdr(self, sat, name, start_date, version, model, mission, file_type):
        """
        Create a single HDR or EEF file
        """
        prefix = "L2"
        mission_specifier = sat[-1] if sat in ["S2A", "S2B"] else ""
        if name == "SITE" and sat == "S2B":
            return ""
        if name == "SITE" and sat == "S2A":
            sat = "S2_"
            mission_specifier = "_"
        if name in ["EXTL", "QLTL"]:
            prefix = "CK"
        basename = "_".join([sat, "TEST", "GIP", prefix + name, "L",
                             "{s:_^8}".format(s=model),
                             version, start_date.strftime("%Y%m%dT%H%M%S"),
                             self.date.strftime("%Y%m%dT%H%M%S")])
        hdr_name = os.path.join(self.root, basename + file_type)
        self.hdr.append(hdr_name)
        self.create_dummy_hdr(hdr_name, mission=mission + mission_specifier)
        return basename

    def generate(self, **kwargs):
        from datetime import datetime
        import random
        from Common import FileSystem
        mission_choice = {"tm": {"S2": "SENTINEL-2"},
                          "muscate": {"S2": "SENTINEL2", "L8": "LANDSAT8", "VE": "VENUS"},
                          "natif": {"S2": "SENTINEL-2", "L8": "LANDSAT_8", "VE": "VENuS"}
                          }
        mission_param = kwargs.get("mission", random.choice(["muscate", "natif"]))
        if mission_param == "tm":
            self.platform = "S2"
        mission = mission_choice[mission_param][self.platform]
        satellites = [self.platform] if self.platform != "S2" else ["S2A", "S2B"]
        with_cams = kwargs.get("cams", True)
        if with_cams:
            models = ["CONTINEN"] + ["ORGANICM", "BLACKCAR", "DUST", "SEASALT", "SULPHATE"]
        else:
            models = ["CONTINEN"]
        allsites = "ALLSITES"
        hdr_types = ["ALBD", "DIFT", "DIRT", "TOCR", "WATV"]
        eef_types = ["COMM", "SITE", "SMAC", "EXTL", "QLTL"]
        tm_types = ["COMM", "EXTL", "QLTL"]
        version = random.randint(0, 9999)
        version_str = str(version).zfill(5)
        start_date = datetime(2014, 12, 30)
        for sat in satellites:
            for name in eef_types:
                self._create_hdr(sat, name, start_date, version_str, allsites, mission, ".EEF")
            for name in hdr_types:
                for model in models:
                    basename = self._create_hdr(sat, name, start_date, version_str, model, mission, ".HDR")
                    dbl_name = os.path.join(self.root, basename + ".DBL.DIR")
                    self.dbl.append(dbl_name)
                    FileSystem.create_directory(dbl_name)
            # For TM: Add an additional set of COMM, EXTL and QLTL files with muscate mission:
            for name in tm_types:
                if mission_param != "tm":
                    continue
                tm_mission = "SENTINEL2"
                tm_version_str = str(version + 10000).zfill(5)
                self._create_hdr(sat, name, start_date, tm_version_str, allsites, tm_mission, ".EEF")


class ProductGenerator(DummyGenerator):
    platform_options = {"L1C": {"S2": ["S2A", "S2B"]},
                        "L2A": {"S2": ["SENTINEL2B", "SENTINEL2A"],
                                "L8": ["LANDSAT8-OLITIRS"],
                                "VE": ["VENUS-XS"]}}

    def __init__(self, root, date=None, tile=None, platform=random_platform()):
        super(ProductGenerator, self).__init__(root, date, tile, platform)
        self.prod = None
        self.mtd = None

    def generate(self, **kwargs):
        raise NotImplementedError


class L1Generator(ProductGenerator):
    """
    Class to create a dummy L1C product
    """
    def __init__(self, root, date=None, tile=None, platform=random_platform(product_level="L1C")):
        super(L1Generator, self).__init__(root, date, tile, platform)

    def generate(self, **kwargs):
        import random
        from Common import TestFunctions, FileSystem
        platform_specifier = random.choice(self.platform_options["L1C"][self.platform])
        orbit = kwargs.get("orbit", random.randint(0, 999))
        version_orbit = kwargs.get("version", random.randint(0, 9))
        date_str = self.date.strftime("%Y%m%dT%H%M%S")
        product_name = "_".join([platform_specifier,
                                 "MSIL1C",
                                 date_str,
                                 "N" + str(orbit).zfill(4),
                                 "R" + str(version_orbit).zfill(3),
                                 self.tile,
                                 date_str + ".SAFE"])
        product_path = os.path.join(self.root, product_name)
        self.prod = product_path
        metadata_path = os.path.join(product_path, "MTD_MSIL1C.xml")
        self.mtd = metadata_path
        FileSystem.create_directory(product_path)
        TestFunctions.touch(metadata_path)


class L2Generator(ProductGenerator):
    """
    Class to create a dummy L2A product
    """
    def __init__(self, root, date=random_date(), tile=None, platform=random_platform(product_level="L2A")):
        super(L2Generator, self).__init__(root, date, tile, platform)

    def generate(self, **kwargs):
        import random
        from Common import TestFunctions, FileSystem
        platform_specifier = random.choice(self.platform_options["L2A"][self.platform])
        ms = kwargs.get("ms", random.randint(0, 999))
        version = kwargs.get("version", random.randint(0, 9))
        date_str = self.date.strftime("%Y%m%d-%H%M%S-") + str(ms)
        product_name = "_".join([platform_specifier,
                                 date_str,
                                 "L2A",
                                 self.tile,
                                 random.choice("DC"),
                                 "V" + str(version) + "-" + str(version)])
        product_path = os.path.join(self.root, product_name)
        self.prod = product_path
        metadata_path = os.path.join(product_path, product_name + "_MTD_ALL.xml")
        self.mtd = metadata_path
        FileSystem.create_directory(product_path)
        TestFunctions.touch(metadata_path)
