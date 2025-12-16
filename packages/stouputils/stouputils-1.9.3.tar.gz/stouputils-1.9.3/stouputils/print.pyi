from collections.abc import Callable as Callable, Iterable, Iterator
from typing import Any, IO, TextIO, TypeVar

RESET: str
RED: str
GREEN: str
YELLOW: str
BLUE: str
MAGENTA: str
CYAN: str
LINE_UP: str
BAR_FORMAT: str
T = TypeVar('T')
previous_args_kwards: tuple[Any, Any]
nb_values: int
import_time: float

def colored_for_loop(iterable: Iterable[T], desc: str = 'Processing', color: str = ..., bar_format: str = ..., ascii: bool = False, **kwargs: Any) -> Iterator[T]:
    ''' Function to iterate over a list with a colored TQDM progress bar like the other functions in this module.

\tArgs:
\t\titerable\t(Iterable):\t\t\tList to iterate over
\t\tdesc\t\t(str):\t\t\t\tDescription of the function execution displayed in the progress bar
\t\tcolor\t\t(str):\t\t\t\tColor of the progress bar (Defaults to MAGENTA)
\t\tbar_format\t(str):\t\t\t\tFormat of the progress bar (Defaults to BAR_FORMAT)
\t\tascii\t\t(bool):\t\t\t\tWhether to use ASCII or Unicode characters for the progress bar (Defaults to False)
\t\tverbose\t\t(int):\t\t\t\tLevel of verbosity, decrease by 1 for each depth (Defaults to 1)
\t\t**kwargs:\t\t\t\t\t\tAdditional arguments to pass to the TQDM progress bar

\tYields:
\t\tT:\t\tEach item of the iterable

\tExamples:
\t\t>>> for i in colored_for_loop(range(10), desc="Time sleeping loop"):
\t\t...     time.sleep(0.01)
\t\t>>> # Time sleeping loop: 100%|██████████████████| 10/10 [ 95.72it/s, 00:00<00:00]
\t'''
def info(*values: Any, color: str = ..., text: str = 'INFO ', prefix: str = '', file: TextIO | list[TextIO] | None = None, **print_kwargs: Any) -> None:
    ''' Print an information message looking like "[INFO HH:MM:SS] message" in green by default.

\tArgs:
\t\tvalues\t\t\t(Any):\t\t\t\t\tValues to print (like the print function)
\t\tcolor\t\t\t(str):\t\t\t\t\tColor of the message (default: GREEN)
\t\ttext\t\t\t(str):\t\t\t\t\tText of the message (default: "INFO ")
\t\tprefix\t\t\t(str):\t\t\t\t\tPrefix to add to the values
\t\tfile\t\t\t(TextIO|list[TextIO]):\tFile(s) to write the message to (default: sys.stdout)
\t\tprint_kwargs\t(dict):\t\t\t\t\tKeyword arguments to pass to the print function
\t'''
def debug(*values: Any, **print_kwargs: Any) -> None:
    ''' Print a debug message looking like "[DEBUG HH:MM:SS] message" in cyan by default. '''
def alt_debug(*values: Any, **print_kwargs: Any) -> None:
    ''' Print a debug message looking like "[DEBUG HH:MM:SS] message" in blue by default. '''
def suggestion(*values: Any, **print_kwargs: Any) -> None:
    ''' Print a suggestion message looking like "[SUGGESTION HH:MM:SS] message" in cyan by default. '''
def progress(*values: Any, **print_kwargs: Any) -> None:
    ''' Print a progress message looking like "[PROGRESS HH:MM:SS] message" in magenta by default. '''
def warning(*values: Any, **print_kwargs: Any) -> None:
    ''' Print a warning message looking like "[WARNING HH:MM:SS] message" in yellow by default and in sys.stderr. '''
def error(*values: Any, exit: bool = False, **print_kwargs: Any) -> None:
    """ Print an error message (in sys.stderr and in red by default)
\tand optionally ask the user to continue or stop the program.

\tArgs:
\t\tvalues\t\t\t(Any):\t\tValues to print (like the print function)
\t\texit\t\t\t(bool):\t\tWhether to ask the user to continue or stop the program,
\t\t\tfalse to ignore the error automatically and continue
\t\tprint_kwargs\t(dict):\t\tKeyword arguments to pass to the print function
\t"""
def whatisit(*values: Any, print_function: Callable[..., None] = ..., max_length: int = 250, color: str = ..., **print_kwargs: Any) -> None:
    ''' Print the type of each value and the value itself, with its id and length/shape.

\tThe output format is: "type, <id id_number>:\t(length/shape) value"

\tArgs:
\t\tvalues\t\t\t(Any):\t\tValues to print
\t\tprint_function\t(Callable):\tFunction to use to print the values (default: debug())
\t\tmax_length\t\t(int):\t\tMaximum length of the value string to print (default: 250)
\t\tcolor\t\t\t(str):\t\tColor of the message (default: CYAN)
\t\tprint_kwargs\t(dict):\t\tKeyword arguments to pass to the print function
\t'''
def breakpoint(*values: Any, print_function: Callable[..., None] = ..., **print_kwargs: Any) -> None:
    """ Breakpoint function, pause the program and print the values.

\tArgs:
\t\tvalues\t\t\t(Any):\t\tValues to print
\t\tprint_function\t(Callable):\tFunction to use to print the values (default: warning())
\t\tprint_kwargs\t(dict):\t\tKeyword arguments to pass to the print function
\t"""

class TeeMultiOutput:
    ''' File-like object that duplicates output to multiple file-like objects.

\tArgs:
\t\t*files         (IO[Any]):  One or more file-like objects that have write and flush methods
\t\tstrip_colors   (bool):     Strip ANSI color codes from output sent to non-stdout/stderr files
\t\tascii_only     (bool):     Replace non-ASCII characters with their ASCII equivalents for non-stdout/stderr files
\t\tignore_lineup  (bool):     Ignore lines containing LINE_UP escape sequence in non-terminal outputs

\tExamples:
\t\t>>> f = open("logfile.txt", "w")
\t\t>>> sys.stdout = TeeMultiOutput(sys.stdout, f)
\t\t>>> print("Hello World")  # Output goes to both console and file
\t\tHello World
\t\t>>> f.close()\t# TeeMultiOutput will handle any future writes to closed files gracefully
\t'''
    files: tuple[IO[Any], ...]
    strip_colors: bool
    ascii_only: bool
    ignore_lineup: bool
    def __init__(self, *files: IO[Any], strip_colors: bool = True, ascii_only: bool = True, ignore_lineup: bool = True) -> None: ...
    @property
    def encoding(self) -> str:
        ''' Get the encoding of the first file, or "utf-8" as fallback.

\t\tReturns:
\t\t\tstr: The encoding, ex: "utf-8", "ascii", "latin1", etc.
\t\t'''
    def write(self, obj: str) -> int:
        """ Write the object to all files while stripping colors if needed.

\t\tArgs:
\t\t\tobj (str): String to write
\t\tReturns:
\t\t\tint: Number of characters written to the first file
\t\t"""
    def flush(self) -> None:
        """ Flush all files. """
    def fileno(self) -> int:
        """ Return the file descriptor of the first file. """

def remove_colors(text: str) -> str:
    """ Remove the colors from a text """
def is_same_print(*args: Any, **kwargs: Any) -> bool:
    """ Checks if the current print call is the same as the previous one. """
def current_time() -> str:
    ''' Get the current time as "HH:MM:SS" if less than 24 hours since import, else "YYYY-MM-DD HH:MM:SS" '''
def show_version(main_package: str = 'stouputils', primary_color: str = ..., secondary_color: str = ...) -> None:
    ''' Print the version of the main package and its dependencies.

\tUsed by the "stouputils --version" command.

\tArgs:
\t\tmain_package\t\t\t(str):\t\t\tName of the main package to show version for
\t\tprimary_color\t\t\t(str):\t\t\tColor to use for the primary package name
\t\tsecondary_color\t\t\t(str):\t\t\tColor to use for the secondary package names
\t'''
