# -*- coding: utf-8 -*-

import os
import shutil

import logging

log = logging.getLogger(__name__)


def create_directory(path):
    """
    Creates a Directory with the given path. Throws a warning if it's already existing and an error if
    a file with the same name already exists.
    :param path: The full path to the new directory
    """
    if os.path.exists(path):
        if not os.path.isdir(path):
            raise IOError("Cannot create the output directory. There is a file with the same name: %s" % path)
        else:
            logging.info("Directory already existing: %s" % path)
    else:
        try:
            os.makedirs(path)
        except OSError:
            raise IOError("Cannot create directory %s" % path)
    return 0


def remove_file(filename):
    """
    Removes File of given path
    :param filename: Path to File
    """
    try:
        os.remove(filename)
    except OSError:
        log.debug("Cannot remove file %s" % filename)
    return


def remove_directory(directory):
    """
    Removes Directory of given path
    :param directory: Path to Directory
    """
    try:
        shutil.rmtree(directory)
    except OSError:
        log.debug("Cannot remove directory {0}".format(directory))


def __get_item(path, reg):
    """
    Find a specific file/folder within a directory
    :param path: The full path to the directory
    :param reg: The regex to be searched for
    :return: The full path to the file/folder
    """
    import re
    import os
    available_dirs = [f for f in os.listdir(path) if re.search(reg, f)]
    if not available_dirs:
        raise IOError("Cannot find %s in %s" % (reg, path))
    return os.path.abspath(os.path.join(path, available_dirs[0]))


def find(pattern, path):
    """
    Find a file or dir in a directory-tree.
    :param pattern: The filename to be searched for
    :param path: The path to the root directory
    :return: The file/directory if found. AssertionError if not.
    """
    import re
    result = []
    parameter = pattern.replace("*", ".*")
    for root, dirs, files in os.walk(path):
        for name in files + dirs:
            if re.search(parameter, name):
                result.append(os.path.join(root, name))
    if not result:
        raise ValueError("Cannot find %s in %s" % (parameter, path))
    return result


def find_single(pattern, path):
    """
    Find a file or dir in a directory-tree.
    :param pattern: The filename to be searched for
    :param path: The path to the root directory
    :return: The file/directory if found. AssertionError if not.
    """
    return find(pattern, path)[0]


def get_file(**kwargs):
    """
    Get a single file from inside the root directory by glob or regex.
    The necessary arguments:
    - root: The root folder to start the search from.
    The file can have one or multiple of the following characteristics:
    - folders: Inside a (sub-)folder
    - filename: Filename with specific pattern
    :param kwargs: The folders and filename arguments
    :return: The full path to the file if found or OSError if not.
    """
    import os

    search_folder = kwargs["root"]
    # The function supports globbing, so replace the globs for regex-like ones
    folders = kwargs.get("folders", ".")
    parameter = os.path.normpath(folders).replace("*", ".*")
    subdirs = parameter.split(os.sep)
    # Recursively update the search folder for each sub folder
    for sub in subdirs:
        if sub == ".":
            continue
        if sub == "..":
            search_folder = os.path.dirname(search_folder)
            continue
        search_folder = __get_item(search_folder, sub)
    # Now that we are in the right directory, search for the file:
    try:
        filename = kwargs["filename"]
    except KeyError:
        return search_folder
    parameter = os.path.normpath(filename).replace("*", ".*")
    return __get_item(search_folder, parameter)


def symlink(src, dst):
    """
    Create symlink from src to dst and raise Exception if it didnt work
    :param src: The full path to the source file or folder
    :param dst: The destination folder
    :return: None. OSError if symlink cannot be created.
    """
    if os.path.exists(dst) and os.path.islink(dst):
        logging.debug("File already existing: %s" % dst)
        return

    try:
        os.symlink(src, dst)
    except OSError:
        raise OSError("Cannot create symlink for %s at %s. Does your plaform support symlinks?" % (src, dst))
