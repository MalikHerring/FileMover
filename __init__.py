from StationReportMover.Backup import Backup
from StationReportMover.Mover import Mover
from datetime import datetime
import logging
import os

def init_logging(filepath=os.path.dirname(os.path.abspath(__file__))):
    """Initializes the log file."""
    logfile = filepath
    logfile += '\\Logs\\'
    if not os.path.isdir(logfile):
        os.makedirs(logfile)
    logfile += datetime.now().strftime('%m-%d-%Y') + '_File_Moving.log'
    with open(logfile, 'w'):
        pass
    logging.basicConfig(filename=logfile, level=logging.DEBUG,
                        format='%(levelname)s: -- %(asctime)s -- %(message)s',
                        datefmt='%m/%d/%Y %H:%M:%S %p')

def close():
    """Wraps up all calls to close the program

    This will close all files that are in use to ensure
    there are no loose ends.
    """
    logging.info("Program has Finished")
    logging.shutdown()

def undo(backup):
    """Runs the backup to undo all file moves

    Using the passed in backup we will load and undo
    moves.

    Keyword Arguments:
    backup -- backup object used for undoing moves
    """
    backup.load_backup()
    backup.undo_moves()

def move(mover, backup, regular_expressions, capture_groups):
    """Runs the mover to move all files with given paramaters

    Keyword Arguments:
    mover -- mover object created in calling function
    backup -- backup object created in calling function
    regular_expressions -- a list of 2 regular expression [find, move]
    capture_groups -- a list of capture groups to order the files in folders
    """
    find, move = regular_expressions
    mover.find_files(find)
    mover.move_files(move, capture_groups)
    backup.write_to_json()


def run(base_directory, storage_directory, regular_expressions, capture_groups, undo_flag=False):
    """Creates a mover and backup to move files and also back them up or undo the moves.

    Given the following parameters this program will find files using a given regular
    expression. Once all files are found then the program will use a second regular
    expression with capture groups to sort all files. Based on the capture groups 
    ordering the files will be found in directories of contained capture groups.

    Keyword Arguments:
    base_directory -- directory where we will find the files
    storage_directory -- directory we are moving the files to
    regular_expressions -- a list of 2 regular expression [find, move]
    capture_groups -- a numbered list of how we will create folders based on
                      capture groups in the move regular expression
    undo_flag -- boolean value of if we are using a backup to undo the moves
    
    Example:
    Storage Directory: C:/test/
    Files: MHerring_2018W-2.pdf
           HPhothong_2018W-2.pdf
           CMunn_2018W-2.pdf
           MHerring_2019W-2.pdf
           HPhothong_2019W-2.pdf
           CMunn_2019W-2.pdf
    Find_regex: \w+_\d{4}W-2.pdf
    Move_regex: \w+_(\d{4})(W-2).pdf
    Capture_groups: 2, 1
    New File Structure: C:/test/W-2/2018
                        C:/text/W-2/2019
    """
    init_logging(storage_directory)
    backup = Backup(storage_directory)
    mover = Mover(base_directory, storage_directory, backup)
    if undo_flag:
        undo(backup)
    else:
        move(mover, backup, regular_expressions, capture_groups)
    close()

