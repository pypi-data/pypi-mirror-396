from ..decorators import LogLevels as LogLevels, handle_error as handle_error
from ..io import clean_path as clean_path
from ..print import debug as debug, info as info, warning as warning
from .common import ask_install_type as ask_install_type, prompt_for_path as prompt_for_path

def add_to_path_windows(install_path: str) -> bool | None:
    """ Add install_path to the User PATH environment variable on Windows.

\tArgs:
\t\tinstall_path (str): The path to add to the User PATH environment variable.

\tReturns:
\t\tbool | None: True if the path was added to the User PATH environment variable, None otherwise.
\t"""
def check_admin_windows() -> bool:
    """ Check if the script is running with administrator privileges on Windows. """
def get_install_path_windows(program_name: str, ask_global: int = 0, add_path: bool = True, append_to_path: str = '', default_global: str = ...) -> str:
    ''' Get the installation path for the program

\tArgs:
\t\tprogram_name  (str):   The name of the program to install.
\t\task_global    (int):   0 = ask for anything, 1 = install globally, 2 = install locally
\t\tadd_path      (bool):  Whether to add the program to the PATH environment variable. (Only if installed globally)
\t\tappend_to_path (str):  String to append to the installation path when adding to PATH.
\t\t\t(ex: "bin" if executables are in the bin folder)
\t\tdefault_global (str):  The default global installation path.
\t\t\t(Default is "C:\\Program Files" which is the most common location for executables on Windows)

\tReturns:
\t\tstr: The installation path.
\t'''
