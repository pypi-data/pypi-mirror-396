from ..decorators import LogLevels as LogLevels, handle_error as handle_error
from collections.abc import Callable as Callable

def generate_stubs(package_name: str, extra_args: str = '--include-docstrings --include-private') -> int:
    ''' Generate stub files for a Python package using stubgen.

\tNote: stubgen generates stubs in the \'out\' directory by default in the current working directory.

\tArgs:
\t\tpackage_name  (str): Name of the package to generate stubs for.
\t\textra_args    (str): Extra arguments to pass to stubgen. Defaults to "--include-docstrings --include-private".
\tReturns:
\t\tint: Return code of the os.system call.
\t'''
def clean_stubs_directory(output_directory: str, package_name: str) -> None:
    """ Clean the stubs directory by deleting all .pyi files.

\tArgs:
\t\toutput_directory  (str): Directory to clean.
\t\tpackage_name      (str): Package name subdirectory. Only cleans output_directory/package_name.
\t"""
def stubs_full_routine(package_name: str, output_directory: str = 'typings', extra_args: str = '--include-docstrings --include-private', clean_before: bool = False, generate_stubs_function: Callable[[str, str], int] = ..., clean_stubs_function: Callable[[str, str], None] = ...) -> None:
    ''' Generate stub files for a Python package using stubgen.

\tNote: stubgen generates stubs in the \'out\' directory by default in the current working directory.

\tArgs:
\t\tpackage_name              (str):                       Name of the package to generate stubs for.
\t\toutput_directory          (str):                       Directory to clean before generating stubs. Defaults to "typings".
\t\t\tThis parameter is used for cleaning the directory before stub generation.
\t\textra_args                (str):                       Extra arguments to pass to stubgen. Defaults to "--include-docstrings --include-private".
\t\tclean_before              (bool):                      Whether to clean the output directory before generating stubs. Defaults to False.
\t\tgenerate_stubs_function   (Callable[[str, str], int]): Function to generate stubs.
\t\t\tDefaults to :func:`generate_stubs`.
\t\tclean_stubs_function      (Callable[[str], None]):     Function to clean the stubs directory.
\t\t\tDefaults to :func:`clean_stubs_directory`.
\tRaises:
\t\tException: If stub generation fails.
\t'''
