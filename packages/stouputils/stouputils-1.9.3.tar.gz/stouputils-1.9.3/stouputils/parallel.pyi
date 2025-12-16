from .ctx import SetMPStartMethod as SetMPStartMethod
from .print import BAR_FORMAT as BAR_FORMAT, MAGENTA as MAGENTA
from collections.abc import Callable
from typing import Any, TypeVar

def doctest_square(x: int) -> int: ...
def doctest_slow(x: int) -> int: ...

CPU_COUNT: int
T = TypeVar('T')
R = TypeVar('R')

def multiprocessing(func: Callable[..., R] | list[Callable[..., R]], args: list[T], use_starmap: bool = False, chunksize: int = 1, desc: str = '', max_workers: int = ..., delay_first_calls: float = 0, color: str = ..., bar_format: str = ..., ascii: bool = False) -> list[R]:
    ''' Method to execute a function in parallel using multiprocessing

\t- For CPU-bound operations where the GIL (Global Interpreter Lock) is a bottleneck.
\t- When the task can be divided into smaller, independent sub-tasks that can be executed concurrently.
\t- For computationally intensive tasks like scientific simulations, data analysis, or machine learning workloads.

\tArgs:
\t\tfunc\t\t\t\t(Callable | list[Callable]):\tFunction to execute, or list of functions (one per argument)
\t\targs\t\t\t\t(list):\t\t\t\tList of arguments to pass to the function(s)
\t\tuse_starmap\t\t\t(bool):\t\t\t\tWhether to use starmap or not (Defaults to False):
\t\t\tTrue means the function will be called like func(\\*args[i]) instead of func(args[i])
\t\tchunksize\t\t\t(int):\t\t\t\tNumber of arguments to process at a time
\t\t\t(Defaults to 1 for proper progress bar display)
\t\tdesc\t\t\t\t(str):\t\t\t\tDescription displayed in the progress bar
\t\t\t(if not provided no progress bar will be displayed)
\t\tmax_workers\t\t\t(int):\t\t\t\tNumber of workers to use (Defaults to CPU_COUNT), -1 means CPU_COUNT
\t\tdelay_first_calls\t(float):\t\t\tApply i*delay_first_calls seconds delay to the first "max_workers" calls.
\t\t\tFor instance, the first process will be delayed by 0 seconds, the second by 1 second, etc.
\t\t\t(Defaults to 0): This can be useful to avoid functions being called in the same second.
\t\tcolor\t\t\t\t(str):\t\t\t\tColor of the progress bar (Defaults to MAGENTA)
\t\tbar_format\t\t\t(str):\t\t\t\tFormat of the progress bar (Defaults to BAR_FORMAT)
\t\tascii\t\t\t\t(bool):\t\t\t\tWhether to use ASCII or Unicode characters for the progress bar

\tReturns:
\t\tlist[object]:\tResults of the function execution

\tExamples:
\t\t.. code-block:: python

\t\t\t> multiprocessing(doctest_square, args=[1, 2, 3])
\t\t\t[1, 4, 9]

\t\t\t> multiprocessing(int.__mul__, [(1,2), (3,4), (5,6)], use_starmap=True)
\t\t\t[2, 12, 30]

\t\t\t> # Using a list of functions (one per argument)
\t\t\t> multiprocessing([doctest_square, doctest_square, doctest_square], [1, 2, 3])
\t\t\t[1, 4, 9]

\t\t\t> # Will process in parallel with progress bar
\t\t\t> multiprocessing(doctest_slow, range(10), desc="Processing")
\t\t\t[0, 1, 2, 3, 4, 5, 6, 7, 8, 9]

\t\t\t> # Will process in parallel with progress bar and delay the first threads
\t\t\t> multiprocessing(
\t\t\t.     doctest_slow,
\t\t\t.     range(10),
\t\t\t.     desc="Processing with delay",
\t\t\t.     max_workers=2,
\t\t\t.     delay_first_calls=0.6
\t\t\t. )
\t\t\t[0, 1, 2, 3, 4, 5, 6, 7, 8, 9]
\t'''
def multithreading(func: Callable[..., R] | list[Callable[..., R]], args: list[T], use_starmap: bool = False, desc: str = '', max_workers: int = ..., delay_first_calls: float = 0, color: str = ..., bar_format: str = ..., ascii: bool = False) -> list[R]:
    ''' Method to execute a function in parallel using multithreading, you should use it:

\t- For I/O-bound operations where the GIL is not a bottleneck, such as network requests or disk operations.
\t- When the task involves waiting for external resources, such as network responses or user input.
\t- For operations that involve a lot of waiting, such as GUI event handling or handling user input.

\tArgs:
\t\tfunc\t\t\t\t(Callable | list[Callable]):\tFunction to execute, or list of functions (one per argument)
\t\targs\t\t\t\t(list):\t\t\t\tList of arguments to pass to the function(s)
\t\tuse_starmap\t\t\t(bool):\t\t\t\tWhether to use starmap or not (Defaults to False):
\t\t\tTrue means the function will be called like func(\\*args[i]) instead of func(args[i])
\t\tdesc\t\t\t\t(str):\t\t\t\tDescription displayed in the progress bar
\t\t\t(if not provided no progress bar will be displayed)
\t\tmax_workers\t\t\t(int):\t\t\t\tNumber of workers to use (Defaults to CPU_COUNT), -1 means CPU_COUNT
\t\tdelay_first_calls\t(float):\t\t\tApply i*delay_first_calls seconds delay to the first "max_workers" calls.
\t\t\tFor instance with value to 1, the first thread will be delayed by 0 seconds, the second by 1 second, etc.
\t\t\t(Defaults to 0): This can be useful to avoid functions being called in the same second.
\t\tcolor\t\t\t\t(str):\t\t\t\tColor of the progress bar (Defaults to MAGENTA)
\t\tbar_format\t\t\t(str):\t\t\t\tFormat of the progress bar (Defaults to BAR_FORMAT)
\t\tascii\t\t\t\t(bool):\t\t\t\tWhether to use ASCII or Unicode characters for the progress bar

\tReturns:
\t\tlist[object]:\tResults of the function execution

\tExamples:
\t\t.. code-block:: python

\t\t\t> multithreading(doctest_square, args=[1, 2, 3])
\t\t\t[1, 4, 9]

\t\t\t> multithreading(int.__mul__, [(1,2), (3,4), (5,6)], use_starmap=True)
\t\t\t[2, 12, 30]

\t\t\t> # Using a list of functions (one per argument)
\t\t\t> multithreading([doctest_square, doctest_square, doctest_square], [1, 2, 3])
\t\t\t[1, 4, 9]

\t\t\t> # Will process in parallel with progress bar
\t\t\t> multithreading(doctest_slow, range(10), desc="Threading")
\t\t\t[0, 1, 2, 3, 4, 5, 6, 7, 8, 9]

\t\t\t> # Will process in parallel with progress bar and delay the first threads
\t\t\t> multithreading(
\t\t\t.     doctest_slow,
\t\t\t.     range(10),
\t\t\t.     desc="Threading with delay",
\t\t\t.     max_workers=2,
\t\t\t.     delay_first_calls=0.6
\t\t\t. )
\t\t\t[0, 1, 2, 3, 4, 5, 6, 7, 8, 9]
\t'''
def run_in_subprocess(func: Callable[..., R], *args: Any, timeout: float | None = None, **kwargs: Any) -> R:
    ''' Execute a function in a subprocess with positional and keyword arguments.

\tThis is useful when you need to run a function in isolation to avoid memory leaks,
\tresource conflicts, or to ensure a clean execution environment. The subprocess will
\tbe created, run the function with the provided arguments, and return the result.

\tArgs:
\t\tfunc         (Callable):     The function to execute in a subprocess.
\t\t\t(SHOULD BE A TOP-LEVEL FUNCTION TO BE PICKLABLE)
\t\t*args        (Any):          Positional arguments to pass to the function.
\t\ttimeout      (float | None): Maximum time in seconds to wait for the subprocess.
\t\t\tIf None, wait indefinitely. If the subprocess exceeds this time, it will be terminated.
\t\t**kwargs     (Any):          Keyword arguments to pass to the function.

\tReturns:
\t\tR: The return value of the function.

\tRaises:
\t\tRuntimeError: If the subprocess exits with a non-zero exit code or times out.
\t\tTimeoutError: If the subprocess exceeds the specified timeout.

\tExamples:
\t\t.. code-block:: python

\t\t\t> # Simple function execution
\t\t\t> run_in_subprocess(doctest_square, 5)
\t\t\t25

\t\t\t> # Function with multiple arguments
\t\t\t> def add(a: int, b: int) -> int:
\t\t\t.     return a + b
\t\t\t> run_in_subprocess(add, 10, 20)
\t\t\t30

\t\t\t> # Function with keyword arguments
\t\t\t> def greet(name: str, greeting: str = "Hello") -> str:
\t\t\t.     return f"{greeting}, {name}!"
\t\t\t> run_in_subprocess(greet, "World", greeting="Hi")
\t\t\t\'Hi, World!\'

\t\t\t> # With timeout to prevent hanging
\t\t\t> run_in_subprocess(some_gpu_func, data, timeout=300.0)
\t'''
def _subprocess_wrapper(result_queue: Any, func: Callable[..., R], args: tuple[Any, ...], kwargs: dict[str, Any]) -> None:
    """ Wrapper function to execute the target function and store the result in the queue.

\tMust be at module level to be pickable on Windows (spawn context).

\tArgs:
\t\tresult_queue (multiprocessing.Queue):  Queue to store the result or exception.
\t\tfunc         (Callable):               The target function to execute.
\t\targs         (tuple):                  Positional arguments for the function.
\t\tkwargs       (dict):                   Keyword arguments for the function.
\t"""
def _starmap(args: tuple[Callable[[T], R], list[T]]) -> R:
    """ Private function to use starmap using args[0](\\*args[1])

\tArgs:
\t\targs (tuple): Tuple containing the function and the arguments list to pass to the function
\tReturns:
\t\tobject: Result of the function execution
\t"""
def _delayed_call(args: tuple[Callable[[T], R], float, T]) -> R:
    """ Private function to apply delay before calling the target function

\tArgs:
\t\targs (tuple): Tuple containing the function, delay in seconds, and the argument to pass to the function
\tReturns:
\t\tobject: Result of the function execution
\t"""
def _handle_parameters(func: Callable[[T], R] | list[Callable[[T], R]], args: list[T], use_starmap: bool, delay_first_calls: float, max_workers: int, desc: str, color: str) -> tuple[str, Callable[[T], R], list[T]]:
    ''' Private function to handle the parameters for multiprocessing or multithreading functions

\tArgs:
\t\tfunc\t\t\t\t(Callable | list[Callable]):\tFunction to execute, or list of functions (one per argument)
\t\targs\t\t\t\t(list):\t\t\t\tList of arguments to pass to the function(s)
\t\tuse_starmap\t\t\t(bool):\t\t\t\tWhether to use starmap or not (Defaults to False):
\t\t\tTrue means the function will be called like func(\\*args[i]) instead of func(args[i])
\t\tdelay_first_calls\t(int):\t\t\t\tApply i*delay_first_calls seconds delay to the first "max_workers" calls.
\t\t\tFor instance, the first process will be delayed by 0 seconds, the second by 1 second, etc. (Defaults to 0):
\t\t\tThis can be useful to avoid functions being called in the same second.
\t\tmax_workers\t\t\t(int):\t\t\t\tNumber of workers to use (Defaults to CPU_COUNT)
\t\tdesc\t\t\t\t(str):\t\t\t\tDescription of the function execution displayed in the progress bar
\t\tcolor\t\t\t\t(str):\t\t\t\tColor of the progress bar

\tReturns:
\t\ttuple[str, Callable[[T], R], list[T]]:\tTuple containing the description, function, and arguments
\t'''
