from .decorators import LogLevels as LogLevels, handle_error as handle_error
from .io import clean_path as clean_path, super_copy as super_copy
from .print import CYAN as CYAN, GREEN as GREEN, RESET as RESET, debug as debug, error as error, info as info

def repair_zip_file(file_path: str, destination: str) -> bool:
    ''' Try to repair a corrupted zip file by ignoring some of the errors

\tThis function manually parses the ZIP file structure to extract files
\teven when the ZIP file is corrupted. It reads the central directory
\tentries and attempts to decompress each file individually.

\tArgs:
\t\tfile_path\t\t(str):\tPath of the zip file to repair
\t\tdestination\t\t(str):\tDestination of the new file
\tReturns:
\t\tbool: Always returns True unless any strong error

\tExamples:

\t.. code-block:: python

\t\t> repair_zip_file("/path/to/source.zip", "/path/to/destination.zip")
\t'''
def make_archive(source: str, destinations: list[str] | str | None = None, override_time: None | tuple[int, int, int, int, int, int] = None, create_dir: bool = False, ignore_patterns: str | None = None) -> bool:
    ''' Create a zip archive from a source directory with consistent file timestamps.
\t(Meaning deterministic zip file each time)

\tCreates a zip archive from the source directory and copies it to one or more destinations.
\tThe archive will have consistent file timestamps across runs if override_time is specified.
\tUses maximum compression level (9) with ZIP_DEFLATED algorithm.

\tArgs:
\t\tsource\t\t\t\t(str):\t\t\t\t\t\tThe source folder to archive
\t\tdestinations\t\t(list[str]|str):\t\t\tThe destination folder(s) or file(s) to copy the archive to
\t\toverride_time\t\t(None | tuple[int, ...]):\tThe constant time to use for the archive
\t\t\t(e.g. (2024, 1, 1, 0, 0, 0) for 2024-01-01 00:00:00)
\t\tcreate_dir\t\t\t(bool):\t\t\t\t\t\tWhether to create the destination directory if it doesn\'t exist
\t\tignore_patterns\t\t(str | None):\t\t\t\tGlob pattern(s) to ignore files. Can be a single pattern or comma-separated patterns (e.g. "*.pyc" or "*.pyc,__pycache__,*.log")
\tReturns:
\t\tbool: Always returns True unless any strong error
\tExamples:

\t.. code-block:: python

\t\t> make_archive("/path/to/source", "/path/to/destination.zip")
\t\t> make_archive("/path/to/source", ["/path/to/destination.zip", "/path/to/destination2.zip"])
\t\t> make_archive("src", "hello_from_year_2085.zip", override_time=(2085,1,1,0,0,0))
\t\t> make_archive("src", "output.zip", ignore_patterns="*.pyc")
\t\t> make_archive("src", "output.zip", ignore_patterns="__pycache__")
\t\t> make_archive("src", "output.zip", ignore_patterns="*.pyc,__pycache__,*.log")
\t'''
def archive_cli() -> None:
    ''' Main entry point for command line usage.

\tExamples:

\t.. code-block:: bash

\t\t# Repair a corrupted zip file
\t\tpython -m stouputils.archive repair /path/to/corrupted.zip /path/to/repaired.zip

\t\t# Create a zip archive
\t\tpython -m stouputils.archive make /path/to/source /path/to/destination.zip

\t\t# Create a zip archive with ignore patterns
\t\tpython -m stouputils.archive make /path/to/source /path/to/destination.zip --ignore "*.pyc,__pycache__"
\t'''
