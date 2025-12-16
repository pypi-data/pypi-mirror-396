from .common import *
from .linux import *
from .windows import *
from ..decorators import LogLevels as LogLevels, handle_error as handle_error
from ..print import info as info, warning as warning
from collections.abc import Callable as Callable

def extract_archive(extraction_path: str, temp_dir: str, extract_func: Callable[[str], None], get_file_list_func: Callable[[], list[str]]) -> None:
    """ Helper function to extract archive files with consistent handling.

\tArgs:
\t\textraction_path     (str): Path where files should be extracted
\t\ttemp_dir            (str): Temporary directory for intermediate extraction
\t\textract_func        (Callable[[str], None]): Function to extract the archive
\t\tget_file_list_func  (Callable[[], list[str]]): Function to get the list of files in the archive
\t"""
def get_install_path(program_name: str, platform_str: str = ..., ask_global: int = 0, add_path: bool = True, append_to_path: str = '') -> str:
    ''' Get the installation path for the program on the current platform.

\tArgs:
\t\tprogram_name  (str):  The name of the program to install.
\t\tplatform_str  (str):  The platform to get the installation path for.
\t\task_global    (int):  Whether to ask the user for a path, 0 = ask, 1 = install globally, 2 = install locally.
\t\tadd_path      (bool): Whether to add the program to the PATH environment variable.
\t\tappend_to_path (str):  String to append to the installation path when adding to PATH.
\t\t\t(ex: "bin" if executables are in the bin folder)

\tReturns:
\t\tstr: The installation path for the program.
\t'''
def add_to_path(install_path: str, platform_str: str = ...) -> bool:
    ''' Add the program to the PATH environment variable.

\tArgs:
\t\tinstall_path  (str):  The path to the program to add to the PATH environment variable.
\t\tplatform_str  (str):  The platform you are running on (ex: "Windows", "Linux", "Darwin", ...),
\t\t\twe use this to determine the installation path if not provided.

\tReturns:
\t\tbool: True if add to PATH was successful, False otherwise.
\t'''
def install_program(input_path: str, install_path: str = '', platform_str: str = ..., program_name: str = '', add_path: bool = True, append_to_path: str = '') -> bool:
    ''' Install a program to a specific path from a local zip file or URL.

\tArgs:
\t\tinput_path     (str):  Path to a zip file or a download URL.
\t\tinstall_path   (str):  The directory to extract the program into, we ask user for a path if not provided.
\t\tplatform_str   (str):  The platform you are running on (ex: "Windows", "Linux", "Darwin", ...),
\t\t\twe use this to determine the installation path if not provided.
\t\tadd_path       (bool): Whether to add the program to the PATH environment variable.
\t\tprogram_name   (str):  Override the program name, we get it from the input path if not provided.
\t\tappend_to_path (str):  String to append to the installation path when adding to PATH.
\t\t\t(ex: "bin" if executables are in the bin folder)

\tReturns:
\t\tbool: True if installation was successful, False otherwise.
\t'''
