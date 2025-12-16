from .io import super_open as super_open
from .print import TeeMultiOutput as TeeMultiOutput, debug as debug
from collections.abc import Callable as Callable
from typing import Any, IO, TextIO

class LogToFile:
    ''' Context manager to log to a file.

\tThis context manager allows you to temporarily log output to a file while still printing normally.
\tThe file will receive log messages without ANSI color codes.

\tArgs:
\t\tpath (str): Path to the log file
\t\tmode (str): Mode to open the file in (default: "w")
\t\tencoding (str): Encoding to use for the file (default: "utf-8")
\t\ttee_stdout (bool): Whether to redirect stdout to the file (default: True)
\t\ttee_stderr (bool): Whether to redirect stderr to the file (default: True)
\t\tignore_lineup (bool): Whether to ignore lines containing LINE_UP escape sequence in files (default: False)

\tExamples:
\t\t.. code-block:: python

\t\t\t> import stouputils as stp
\t\t\t> with stp.LogToFile("output.log"):
\t\t\t>     stp.info("This will be logged to output.log and printed normally")
\t\t\t>     print("This will also be logged")
\t'''
    path: str
    mode: str
    encoding: str
    tee_stdout: bool
    tee_stderr: bool
    ignore_lineup: bool
    file: IO[Any]
    original_stdout: TextIO
    original_stderr: TextIO
    def __init__(self, path: str, mode: str = 'w', encoding: str = 'utf-8', tee_stdout: bool = True, tee_stderr: bool = True, ignore_lineup: bool = True) -> None: ...
    def __enter__(self) -> LogToFile:
        """ Enter context manager which opens the log file and redirects stdout/stderr """
    def __exit__(self, exc_type: type[BaseException] | None, exc_val: BaseException | None, exc_tb: Any | None) -> None:
        """ Exit context manager which closes the log file and restores stdout/stderr """
    @staticmethod
    def common(logs_folder: str, filepath: str, func: Callable[..., Any], *args: Any, **kwargs: Any) -> Any:
        ''' Common code used at the beginning of a program to launch main function

\t\tArgs:
\t\t\tlogs_folder (str): Folder to store logs in
\t\t\tfilepath    (str): Path to the main function
\t\t\tfunc        (Callable[..., Any]): Main function to launch
\t\t\t*args       (tuple[Any, ...]): Arguments to pass to the main function
\t\t\t**kwargs    (dict[str, Any]): Keyword arguments to pass to the main function
\t\tReturns:
\t\t\tAny: Return value of the main function

\t\tExamples:
\t\t\t>>> if __name__ == "__main__":
\t\t\t...     LogToFile.common(f"{ROOT}/logs", __file__, main)
\t\t'''

class MeasureTime:
    ''' Context manager to measure execution time.

\tThis context manager measures the execution time of the code block it wraps
\tand prints the result using a specified print function.

\tArgs:
\t\tprint_func      (Callable): Function to use to print the execution time (e.g. debug, info, warning, error, etc.).
\t\tmessage         (str):      Message to display with the execution time. Defaults to "Execution time".
\t\tperf_counter    (bool):     Whether to use time.perf_counter_ns or time.time_ns. Defaults to True.

\tExamples:
\t\t.. code-block:: python

\t\t\t> import time
\t\t\t> import stouputils as stp
\t\t\t> with stp.MeasureTime(stp.info, message="My operation"):
\t\t\t...     time.sleep(0.5)
\t\t\t> # [INFO HH:MM:SS] My operation: 500.123ms (500123456ns)

\t\t\t> with stp.MeasureTime(): # Uses debug by default
\t\t\t...     time.sleep(0.1)
\t\t\t> # [DEBUG HH:MM:SS] Execution time: 100.456ms (100456789ns)
\t'''
    print_func: Callable[..., None]
    message: str
    perf_counter: bool
    ns: Callable[[], int]
    start_ns: int
    def __init__(self, print_func: Callable[..., None] = ..., message: str = 'Execution time', perf_counter: bool = True) -> None: ...
    def __enter__(self) -> MeasureTime:
        """ Enter context manager, record start time """
    def __exit__(self, exc_type: type[BaseException] | None, exc_val: BaseException | None, exc_tb: Any | None) -> None:
        """ Exit context manager, calculate duration and print """

class Muffle:
    ''' Context manager that temporarily silences output.

\tAlternative to stouputils.decorators.silent()

\tExamples:
\t\t>>> with Muffle():
\t\t...     print("This will not be printed")
\t'''
    mute_stderr: bool
    original_stdout: TextIO
    original_stderr: TextIO
    def __init__(self, mute_stderr: bool = False) -> None: ...
    def __enter__(self) -> Muffle:
        """ Enter context manager which redirects stdout and stderr to devnull """
    def __exit__(self, exc_type: type[BaseException] | None, exc_val: BaseException | None, exc_tb: Any | None) -> None:
        """ Exit context manager which restores original stdout and stderr """

class DoNothing:
    ''' Context manager that does nothing.

\tThis is a no-op context manager that can be used as a placeholder
\tor for conditional context management.

\tDifferent from contextlib.nullcontext because it handles args and kwargs,
\talong with **async** context management.

\tExamples:
\t\t>>> with DoNothing():
\t\t...     print("This will be printed normally")
\t\tThis will be printed normally

\t\t>>> # Conditional context management
\t\t>>> some_condition = True
\t\t>>> ctx = DoNothing() if some_condition else Muffle()
\t\t>>> with ctx:
\t\t...     print("May or may not be printed depending on condition")
\t\tMay or may not be printed depending on condition
\t'''
    def __init__(self, *args: Any, **kwargs: Any) -> None:
        """ No initialization needed, this is a no-op context manager """
    def __enter__(self) -> Any:
        """ Enter context manager (does nothing) """
    def __exit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        """ Exit context manager (does nothing) """
    async def __aenter__(self) -> Any:
        """ Enter async context manager (does nothing) """
    async def __aexit__(self, *excinfo: Any) -> None:
        """ Exit async context manager (does nothing) """

class SetMPStartMethod:
    ''' Context manager to temporarily set multiprocessing start method.

\tThis context manager allows you to temporarily change the multiprocessing start method
\tand automatically restores the original method when exiting the context.

\tArgs:
\t\tstart_method (str): The start method to use: "spawn", "fork", or "forkserver"

\tExamples:
\t\t.. code-block:: python

\t\t\t> import multiprocessing as mp
\t\t\t> import stouputils as stp
\t\t\t> # Temporarily use spawn method
\t\t\t> with stp.SetMPStartMethod("spawn"):
\t\t\t> ...     # Your multiprocessing code here
\t\t\t> ...     pass

\t\t\t> # Original method is automatically restored
\t'''
    start_method: str | None
    old_method: str | None
    def __init__(self, start_method: str | None) -> None: ...
    def __enter__(self) -> SetMPStartMethod:
        """ Enter context manager which sets the start method """
    def __exit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        """ Exit context manager which restores the original start method """
