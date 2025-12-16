from ..decorators import LogLevels as LogLevels, handle_error as handle_error
from collections.abc import Callable as Callable

def update_pip_and_required_packages() -> int:
    """ Update pip and required packages.

\tReturns:
\t\tint: Return code of the os.system call.
\t"""
def build_package() -> int:
    """ Build the package.

\tReturns:
\t\tint: Return code of the os.system call.
\t"""
def upload_package(repository: str, filepath: str) -> int:
    """ Upload the package to PyPI.

\tArgs:
\t\trepository  (str): Repository to upload to.
\t\tfilepath    (str): Path to the file to upload.

\tReturns:
\t\tint: Return code of the os.system call.
\t"""
def pypi_full_routine(repository: str, dist_directory: str, last_files: int = 1, endswith: str = '.tar.gz', update_all_function: Callable[[], int] = ..., build_package_function: Callable[[], int] = ..., upload_package_function: Callable[[str, str], int] = ...) -> None:
    ''' Upload the most recent file(s) to PyPI after updating pip and required packages and building the package.

\tArgs:
\t\trepository               (str):                        Repository to upload to.
\t\tdist_directory           (str):                        Directory to upload from.
\t\tlast_files               (int):                        Number of most recent files to upload. Defaults to 1.
\t\tendswith                 (str):                        End of the file name to upload. Defaults to ".tar.gz".
\t\tupdate_all_function      (Callable[[], int]):          Function to update pip and required packages.
\t\t\tDefaults to :func:`update_pip_and_required_packages`.
\t\tbuild_package_function   (Callable[[], int]):          Function to build the package.
\t\t\tDefaults to :func:`build_package`.
\t\tupload_package_function  (Callable[[str, str], int]):  Function to upload the package.
\t\t\tDefaults to :func:`upload_package`.

\tReturns:
\t\tint: Return code of the command.
\t'''
