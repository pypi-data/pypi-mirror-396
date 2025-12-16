import zipfile
from .decorators import handle_error as handle_error, measure_time as measure_time
from .io import clean_path as clean_path
from .print import CYAN as CYAN, GREEN as GREEN, RESET as RESET, colored_for_loop as colored_for_loop, info as info, warning as warning

CHUNK_SIZE: int
LARGE_CHUNK_SIZE: int

def backup_cli() -> None:
    ''' Main entry point for command line usage.

\tExamples:

\t.. code-block:: bash

\t\t# Create a delta backup, excluding libraries and cache folders
\t\tpython -m stouputils.backup delta /path/to/source /path/to/backups -x "libraries/*" "cache/*"

\t\t# Consolidate backups into a single file
\t\tpython -m stouputils.backup consolidate /path/to/backups/latest.zip /path/to/consolidated.zip

\t\t# Limit the number of delta backups to 5
\t\tpython -m stouputils.backup limit 5 /path/to/backups
\t'''
def create_delta_backup(source_path: str, destination_folder: str, exclude_patterns: list[str] | None = None) -> None:
    ''' Creates a ZIP delta backup, saving only modified or new files while tracking deleted files.

\tArgs:
\t\tsource_path (str): Path to the source file or directory to back up
\t\tdestination_folder (str): Path to the folder where the backup will be saved
\t\texclude_patterns (list[str] | None): List of glob patterns to exclude from backup
\tExamples:

\t.. code-block:: python

\t\t> create_delta_backup("/path/to/source", "/path/to/backups", exclude_patterns=["libraries/*", "cache/*"])
\t\t[INFO HH:MM:SS] Creating ZIP backup
\t\t[INFO HH:MM:SS] Backup created: \'/path/to/backups/backup_2025_02_18-10_00_00.zip\'
\t'''
def consolidate_backups(zip_path: str, destination_zip: str) -> None:
    ''' Consolidates the files from the given backup and all previous ones into a new ZIP file,
\tensuring that the most recent version of each file is kept and deleted files are not restored.

\tArgs:
\t\tzip_path (str): Path to the latest backup ZIP file (If endswith "/latest.zip" or "/", the latest backup will be used)
\t\tdestination_zip (str): Path to the destination ZIP file where the consolidated backup will be saved
\tExamples:

\t.. code-block:: python

\t\t> consolidate_backups("/path/to/backups/latest.zip", "/path/to/consolidated.zip")
\t\t[INFO HH:MM:SS] Consolidating backups
\t\t[INFO HH:MM:SS] Consolidated backup created: \'/path/to/consolidated.zip\'
\t'''
def limit_backups(max_backups: int, backup_folder: str, keep_oldest: bool = True) -> None:
    ''' Limits the number of delta backups by consolidating the oldest ones.

\tIf the number of backups exceeds max_backups, the oldest backups are consolidated
\tinto a single backup file, then deleted, until the count is within the limit.

\tArgs:
\t\tmax_backups (int): Maximum number of delta backups to keep
\t\tbackup_folder (str): Path to the folder containing backups
\t\tkeep_oldest (bool): If True, never delete the oldest backup (default: True)
\tExamples:

\t.. code-block:: python

\t\t> limit_backups(5, "/path/to/backups")
\t\t[INFO HH:MM:SS] Limiting backups
\t\t[INFO HH:MM:SS] Consolidated 3 oldest backups into \'/path/to/backups/consolidated_YYYY_MM_DD-HH_MM_SS.zip\'
\t\t[INFO HH:MM:SS] Deleted 3 old backups
\t'''
def get_file_hash(file_path: str) -> str | None:
    """ Computes the SHA-256 hash of a file.

\tArgs:
\t\tfile_path (str): Path to the file
\tReturns:
\t\tstr | None: SHA-256 hash as a hexadecimal string or None if an error occurs
\t"""
def extract_hash_from_zipinfo(zip_info: zipfile.ZipInfo) -> str | None:
    """ Extracts the stored hash from a ZipInfo object's comment.

\tArgs:
\t\tzip_info (zipfile.ZipInfo): The ZipInfo object representing a file in the ZIP
\tReturns:
\t\tstr | None: The stored hash if available, otherwise None
\t"""
def get_all_previous_backups(backup_folder: str, all_before: str | None = None) -> dict[str, dict[str, str]]:
    ''' Retrieves all previous backups in a folder and maps each backup to a dictionary of file paths and their hashes.

\tArgs:
\t\tbackup_folder (str): The folder containing previous backup zip files
\t\tall_before (str | None): Path to the latest backup ZIP file
\t\t\t(If endswith "/latest.zip" or "/", the latest backup will be used)
\tReturns:
\t\tdict[str, dict[str, str]]: Dictionary mapping backup file paths to dictionaries of {file_path: file_hash}
\t'''
def is_file_in_any_previous_backup(file_path: str, file_hash: str, previous_backups: dict[str, dict[str, str]]) -> bool:
    """ Checks if a file with the same hash exists in any previous backup.

\tArgs:
\t\tfile_path (str): The relative path of the file
\t\tfile_hash (str): The SHA-256 hash of the file
\t\tprevious_backups (dict[str, dict[str, str]]): Dictionary mapping backup zip paths to their stored file hashes
\tReturns:
\t\tbool: True if the file exists unchanged in any previous backup, False otherwise
\t"""
