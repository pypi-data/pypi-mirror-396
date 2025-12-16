from ..print import info as info, warning as warning
from .main import install_program as install_program

def download_executable(download_urls: dict[str, str], program_name: str, append_to_path: str = '') -> bool:
    """ Ask the user if they want to download the program (ex: waifu2x-ncnn-vulkan).
\tIf yes, try to download the program from the GitHub releases page.

\tArgs:
\t\tdownload_urls  (dict[str, str]):  The URLs to download the program from.
\t\tprogram_name   (str):             The name of the program to download.

\tReturns:
\t\tbool: True if the program is now ready to use, False otherwise.
\t"""
def check_executable(executable: str, executable_help_text: str, download_urls: dict[str, str], append_to_path: str = '') -> None:
    ''' Check if the executable exists, optionally download it if it doesn\'t.

\tArgs:
\t\texecutable            (str):             The path to the executable.
\t\texecutable_help_text  (str):             The help text to check for in the executable\'s output.
\t\tdownload_urls         (dict[str, str]):  The URLs to download the executable from.
\t\tappend_to_path        (str):             The path to append to the executable\'s path.
\t\t\t(ex: "bin" if executables are in the bin folder)
\t'''
