"""This file is used for logging all transactions"""
from collections import defaultdict
from  datetime import datetime
import logging
import json
import os


class Backup:
    """Creates a backup class to be used for undoing file moves
        
    Backup holds a default dictionary where the key will be the
    new file path and the old filepath will be the value. As long
    as there is a json file with those conventions you can use it to 
    undo file changes.

    Keyword Arguments:
    storage_directory -- directory where files will be moved to    
    """

    def __init__(self, storage_directory, backup_filepath=None):
        """Initilization function -- reference Backup DocString"""
        self.record = defaultdict(str)
        if storage_directory.endswith('\\') or storage_directory.endswith('/'):
            self.storage_directory = storage_directory
        else:
            self.storage_directory = storage_directory + '\\'
        if backup_filepath is None:
            self.backup = self.storage_directory + 'mover_backup.json'
        else:
            self.backup = backup_filepath
        if os.path.isfile(self.backup):
            self.load_backup()
        logging.info('Initialized Backup')

    def record_move(self, original_filepath, new_filepath):
        """This writes the move into the record default dictionary
        
        Using the record default dictionary setup in the initialize
        function every key will be the new filepath we are moving to
        and the value will be the original filepath

        Keyword Arguments:
        original_filepath -- filepath to the original file
        new_filepath -- filepath to where we are moving the file
        """
        self.record[new_filepath] = original_filepath
        logging.debug('Recorded move from {} to {}'.format(original_filepath, new_filepath))

    def write_to_json(self):
        """Writes the record dictionary to JSON
        
        Using the record dictionary we will write it to the
        backup filepath setup during initialization.
        """
        logging.info('Writing records to JSON')
        with open(self.backup, 'w') as fp:
            json.dump(self.record, fp)
        logging.info("Finished writing records to JSON")

    def load_backup(self):
        """Loads a dictionary from the backup JSON filepath
        
        Using the backup JSON filepath if there is a file at that
        path we will load the dictionary into our record class variable.
        If it is not there we will simply log that it did not show up.
        """
        logging.info("Checking for backup file at: {}".format(self.backup))
        if os.path.isfile(self.backup):
            backup_file = open(self.backup)
            self.record = json.load(backup_file)
            backup_file.close()
            logging.info('Loaded backup')
        else:
            logging.info('Backup File is not present.')

    def undo_moves(self):
        """Undoes all moves that are held in record
        
        Using our record dictionary we will scan all moves
        and for every move we will rename it back to its
        old filepath.
        """
        logging.info("Undoing all moves held in records")
        for move in self.record.keys():
            logging.debug('Moving {} to {}'.format(move, self.record[move]))
            try:
                os.rename(move, self.record[move])
                os.removedirs(os.path.dirname(move))
            except OSError as e:
                logging.error('There was an error moving the file {}'.format(move))
                logging.error('Error status: {}'.format(e))
        logging.info("Completed undoing moves")
        try:
            os.remove(self.backup)
        except OSError as e:
                logging.error('There was an error removing the file {}'.format(self.backup))
                logging.error('Error status: {}'.format(e))
            