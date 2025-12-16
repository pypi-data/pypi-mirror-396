from ..decorators import LogLevels as LogLevels, handle_error as handle_error
from ..io import clean_path as clean_path
from ..print import debug as debug, info as info, warning as warning
from .common import ask_install_type as ask_install_type, prompt_for_path as prompt_for_path

def add_to_path_linux(install_path: str) -> bool:
    """ Suggest how to add install_path to PATH on Linux.

\tChecks the current shell and provides instructions for adding the path
\tto the appropriate configuration file (e.g., .bashrc, .zshrc, config.fish).

\tArgs:
\t\tinstall_path (str): The path to add to the PATH environment variable.

\tReturns:
\t\tbool: True if instructions were provided, False otherwise (e.g., unknown shell).
\t"""
def check_admin_linux() -> bool:
    """ Check if the script is running with root privileges on Linux/macOS.

\tReturns:
\t\tbool: True if the effective user ID is 0 (root), False otherwise.
\t"""
def get_install_path_linux(program_name: str, ask_global: int = 0, add_path: bool = True, append_to_path: str = '', default_global: str = '/usr/local/bin') -> str:
    ''' Get the installation path for the program on Linux/macOS.

\tArgs:
\t\tprogram_name   (str):   The name of the program to install.
\t\task_global     (int):   0 = ask for anything, 1 = install globally, 2 = install locally
\t\tadd_path       (bool):  Whether to add the program to the PATH environment variable. (Only if installed globally)
\t\tappend_to_path (str):   String to append to the installation path when adding to PATH.
\t\t\t(ex: "bin" if executables are in the bin folder)
\t\tdefault_global (str):   The default global installation path.
\t\t\t(Default is "/usr/local/bin" which is the most common location for executables on Linux/macOS,
\t\t\tcould be "/opt" or any other directory)

\tReturns:
\t\tstr: The chosen installation path, or an empty string if installation is cancelled.
\t'''
