from ..print import warning as warning
from typing import Literal

def prompt_for_path(prompt_message: str, default_path: str) -> str:
    """ Prompt the user to override a default path.

\tArgs:
\t\tprompt_message (str): The message to display to the user.
\t\tdefault_path   (str): The default path to suggest.

\tReturns:
\t\tstr: The path entered by the user, or the default path if they pressed Enter.
\t"""
def ask_install_type(ask_global: int, default_local_path: str, default_global_path: str | None) -> Literal['g', 'l']:
    ''' Determine the installation type (global \'g\' or local \'l\') based on user input.

\tArgs:
\t\task_global          (int):           0 = ask, 1 = force global, 2 = force local.
\t\tdefault_local_path  (str):           The default local path.
\t\tdefault_global_path (str | None):    The default global path (if applicable).

\tReturns:
\t\tLiteral["g", "l"]: \'g\' for global install, \'l\' for local install.

\tExamples:
\t\t.. code-block:: python

\t\t\t> # Ask the user while providing default paths
\t\t\t> install_choice: str = ask_install_type(0, f"{os.getcwd()}/MyProgram", "C:\\Program Files\\MyProgram")
\t\t\tg

\t\t\t> # Don\'t ask, force global
\t\t\t> install_choice: str = ask_install_type(1, ...)
\t\t\tg

\t\t\t> # Don\'t ask, force local
\t\t\t> install_choice: str = ask_install_type(2, ...)
\t\t\tl
\t'''
