"""This file is used for the Mover Object to move files"""
from collections import defaultdict
from StationReportMover.Backup import Backup
import logging
import re
import os


class Mover:
    """Initialize function for creating a Mover
        
    This function creates the class instance for Mover.
    Mover will create a default dictionary of type dict
    which will hold each level of new directories to be 
    established later.
    
    Keyword Arguments:
    base_directory -- directory holding all the current files
    storage_directory -- directory we will store all current files in
    backup -- Backup class created from Backup.py"""

    def __init__(self, base_directory, storage_directory, backup=None):
        """Initilization function -- reference Mover DocString"""
        logging.info("Mover initializing")
        if backup is None:
            self.backup = Backup(storage_directory)
        else:
            self.backup = backup
        self.base_directory = base_directory
        if storage_directory.endswith('\\') or storage_directory.endswith('/'):
            self.storage_directory = storage_directory
        else:
            self.storage_directory = storage_directory + '\\'
        self.file_list = []
        self.directory_levels = defaultdict(list)
        self.directory_levels[0].append(base_directory)
        logging.info("Mover initialization finished")

    def find_files(self, regex, depth=9999):
        """Search each level from base directories for files
        
        This function will take in a number of levels and search
        for files up to that level. With every level it will scan 
        for all files that the regex matches on and add them to
        the file list.
        
        Keyword Arguments:
        depth -- integer value for how many levels to search for 
                  files from base directory
        regex -- regular expression to match the files.""" 
        logging.info("Beginning file searching")
        level = 0
        loop = True
        regex = re.compile(regex)
        while loop and level <= depth:
            # Gets a list of directories found at the given level
            directories = self.directory_levels[level]
            if directories == []:
                logging.debug("We have found all files")
                loop = False
            level += 1
            logging.debug("Beginning search for files on level {}".format(level))
            for base_directory in directories:
                logging.debug("In directory {}".format(base_directory))
                for name in os.listdir(base_directory):
                    filepath = '\\'.join([base_directory, name])
                    if os.path.isdir(filepath):
                        logging.debug("Adding directory {}".format(name))
                        self.directory_levels[level].append(filepath)
                    else:
                        match = regex.match(name)
                        if match is not None:
                            logging.debug("Adding file {}".format(name))
                            self.file_list.append(filepath)
        logging.info("Comleted searching for files")

    def move_files(self, regex, capture_group_list):
        """Moves files to the storage directory based on capture groups

        Given a regular expression and a list of capture group orderings,
        this function will take all files found in the file_list of this
        object and move them to the storage directory with the directory
        ordering of the given capture group.

        Keyword Arguments:
        regex -- regular expression to finding the capture groups - capture groups
                 are made by putting () around the areas you want to preserve.
        capture_group_list -- list or tuple for the order of capture directories

        Example:
        move_files([1, 2], "([0-9]{5})-([0-9]{5})-([0-9]{8}).pdf")
        - If a file matches the regular expression then it should be placed in
          a directory under the storage directory of the first capture group.
        i. e. 
            storage directory = C:/test/
            file = C:/different_diredctory/00000-01200-20170524.pdf
            new location = C:/test/00000/01200/00000-01200-20170524.pdf
        """
        logging.info("Beginning File Moves")
        existing_directories = defaultdict(bool)
        regex = re.compile(regex)
        # for every file in the file list
        for f in self.file_list:
            # get the base filename
            f_name = os.path.basename(f)
            # obtain capture groups based on regex
            match = regex.match(f_name)
            if match is None:
                logging.error("No match found for {}".format(f))
                continue
            # create a list of the groups given from capture_group_list
            storage = [match.group(x) for x in capture_group_list]
            sub_directories = '\\'.join(storage)
            dir_path = os.path.join(self.storage_directory, sub_directories)
            # Check if sub directories have been made already
            if not existing_directories[sub_directories]:
                try:
                    if os.path.isdir(dir_path):
                        existing_directories[sub_directories] = True
                    else:
                        os.makedirs(dir_path)
                        existing_directories[sub_directories] = True
                except OSError:
                    logging.error("Error creating the directory {}".format(dir_path))
            new_path = os.path.join(dir_path, f_name)
            try:
                if f == new_path:
                    logging.debug("File {} is already in correct spot".format(f_name))
                else:
                    os.rename(f, new_path)
                    self.backup.record_move(f, new_path)
            except OSError:
                logging.error("Attempted move failed on: {}".format(f))
        logging.info("Successfully Finished File Moving")
        