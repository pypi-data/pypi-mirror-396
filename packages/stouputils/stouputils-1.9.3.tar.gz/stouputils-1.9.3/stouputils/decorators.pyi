from .ctx import MeasureTime as MeasureTime, Muffle as Muffle
from .print import error as error, progress as progress, warning as warning
from collections.abc import Callable as Callable
from enum import Enum
from typing import Any, Literal

def measure_time(func: Callable[..., Any] | None = None, *, printer: Callable[..., None] = ..., message: str = '', perf_counter: bool = True, is_generator: bool = False) -> Callable[..., Any]:
    ''' Decorator that will measure the execution time of a function and print it with the given print function

\tArgs:
\t\tfunc\t\t\t(Callable[..., Any] | None): Function to decorate
\t\tprinter\t\t\t(Callable):\tFunction to use to print the execution time (e.g. debug, info, warning, error, etc.)
\t\tmessage\t\t\t(str):\t\tMessage to display with the execution time (e.g. "Execution time of Something"),
\t\t\tdefaults to "Execution time of {func.__name__}"
\t\tperf_counter\t(bool):\t\tWhether to use time.perf_counter_ns or time.time_ns
\t\t\tdefaults to True (use time.perf_counter_ns)
\t\tis_generator\t(bool):\t\tWhether the function is a generator or not (default: False)
\t\t\tWhen True, the decorator will yield from the function instead of returning it.

\tReturns:
\t\tCallable: Decorator to measure the time of the function.

\tExamples:
\t\t.. code-block:: python

\t\t\t> @measure_time(printer=info)
\t\t\t> def test():
\t\t\t>     pass
\t\t\t> test()  # [INFO HH:MM:SS] Execution time of test: 0.000ms (400ns)
\t'''

class LogLevels(Enum):
    """ Log level for the errors in the decorator handle_error() """
    NONE = 0
    WARNING = 1
    WARNING_TRACEBACK = 2
    ERROR_TRACEBACK = 3
    RAISE_EXCEPTION = 4

force_raise_exception: bool

def handle_error(func: Callable[..., Any] | None = None, *, exceptions: tuple[type[BaseException], ...] | type[BaseException] = ..., message: str = '', error_log: LogLevels = ..., sleep_time: float = 0.0) -> Callable[..., Any]:
    ''' Decorator that handle an error with different log levels.

\tArgs:
\t\tfunc        (Callable[..., Any] | None):    \tFunction to decorate
\t\texceptions\t(tuple[type[BaseException]], ...):\tExceptions to handle
\t\tmessage\t\t(str):\t\t\t\t\t\t\t\tMessage to display with the error. (e.g. "Error during something")
\t\terror_log\t(LogLevels):\t\t\t\t\t\tLog level for the errors
\t\t\tLogLevels.NONE:\t\t\t\t\tNone
\t\t\tLogLevels.WARNING:\t\t\t\tShow as warning
\t\t\tLogLevels.WARNING_TRACEBACK:\tShow as warning with traceback
\t\t\tLogLevels.ERROR_TRACEBACK:\t\tShow as error with traceback
\t\t\tLogLevels.RAISE_EXCEPTION:\t\tRaise exception
\t\tsleep_time\t(float):\t\t\t\t\t\t\tTime to sleep after the error (e.g. 0.0 to not sleep, 1.0 to sleep for 1 second)

\tExamples:
\t\t>>> @handle_error
\t\t... def might_fail():
\t\t...     raise ValueError("Let\'s fail")

\t\t>>> @handle_error(error_log=LogLevels.WARNING)
\t\t... def test():
\t\t...     raise ValueError("Let\'s fail")
\t\t>>> # test()\t# [WARNING HH:MM:SS] Error during test: (ValueError) Let\'s fail
\t'''
def timeout(func: Callable[..., Any] | None = None, *, seconds: float = 60.0, message: str = '') -> Callable[..., Any]:
    ''' Decorator that raises a TimeoutError if the function runs longer than the specified timeout.

\tNote: This decorator uses SIGALRM on Unix systems, which only works in the main thread.
\tOn Windows or in non-main threads, it will fall back to a polling-based approach.

\tArgs:
\t\tfunc\t\t(Callable[..., Any] | None):\tFunction to apply timeout to
\t\tseconds\t\t(float):\t\t\t\t\t\tTimeout duration in seconds (default: 60.0)
\t\tmessage\t\t(str):\t\t\t\t\t\t\tCustom timeout message (default: "Function \'{func_name}\' timed out after {seconds} seconds")

\tReturns:
\t\tCallable[..., Any]: Decorator that enforces timeout on the function

\tRaises:
\t\tTimeoutError: If the function execution exceeds the timeout duration

\tExamples:
\t\t>>> @timeout(seconds=2.0)
\t\t... def slow_function():
\t\t...     time.sleep(5)
\t\t>>> slow_function()  # Raises TimeoutError after 2 seconds
\t\tTraceback (most recent call last):
\t\t\t...
\t\tTimeoutError: Function \'slow_function\' timed out after 2.0 seconds

\t\t>>> @timeout(seconds=1.0, message="Custom timeout message")
\t\t... def another_slow_function():
\t\t...     time.sleep(3)
\t\t>>> another_slow_function()  # Raises TimeoutError after 1 second
\t\tTraceback (most recent call last):
\t\t\t...
\t\tTimeoutError: Custom timeout message
\t'''
def retry(func: Callable[..., Any] | None = None, *, exceptions: tuple[type[BaseException], ...] | type[BaseException] = ..., max_attempts: int = 10, delay: float = 1.0, backoff: float = 1.0, message: str = '') -> Callable[..., Any]:
    ''' Decorator that retries a function when specific exceptions are raised.

\tArgs:
\t\tfunc\t\t\t(Callable[..., Any] | None):\t\tFunction to retry
\t\texceptions\t\t(tuple[type[BaseException], ...]):\tExceptions to catch and retry on
\t\tmax_attempts\t(int | None):\t\t\t\t\t\tMaximum number of attempts (None for infinite retries)
\t\tdelay\t\t\t(float):\t\t\t\t\t\t\tInitial delay in seconds between retries (default: 1.0)
\t\tbackoff\t\t\t(float):\t\t\t\t\t\t\tMultiplier for delay after each retry (default: 1.0 for constant delay)
\t\tmessage\t\t\t(str):\t\t\t\t\t\t\t\tCustom message to display before ", retrying" (default: "{ExceptionName} encountered while running {func_name}")

\tReturns:
\t\tCallable[..., Any]: Decorator that retries the function on specified exceptions

\tExamples:
\t\t>>> import os
\t\t>>> @retry(exceptions=PermissionError, max_attempts=3, delay=0.1)
\t\t... def write_file():
\t\t...     with open("test.txt", "w") as f:
\t\t...         f.write("test")

\t\t>>> @retry(exceptions=(OSError, IOError), delay=0.5, backoff=2.0)
\t\t... def network_call():
\t\t...     pass

\t\t>>> @retry(max_attempts=5, delay=1.0)
\t\t... def might_fail():
\t\t...     pass
\t'''
def simple_cache(func: Callable[..., Any] | None = None, *, method: Literal['str', 'pickle'] = 'str') -> Callable[..., Any]:
    ''' Decorator that caches the result of a function based on its arguments.

\tThe str method is often faster than the pickle method (by a little) but not as accurate with complex objects.

\tArgs:
\t\tfunc   (Callable[..., Any] | None): Function to cache
\t\tmethod (Literal["str", "pickle"]):  The method to use for caching.
\tReturns:
\t\tCallable[..., Any]: A decorator that caches the result of a function.
\tExamples:
\t\t>>> @simple_cache
\t\t... def test1(a: int, b: int) -> int:
\t\t...     return a + b

\t\t>>> @simple_cache(method="str")
\t\t... def test2(a: int, b: int) -> int:
\t\t...     return a + b
\t\t>>> test2(1, 2)
\t\t3
\t\t>>> test2(1, 2)
\t\t3
\t\t>>> test2(3, 4)
\t\t7
\t'''
def abstract(func: Callable[..., Any] | None = None, *, error_log: LogLevels = ...) -> Callable[..., Any]:
    """ Decorator that marks a function as abstract.

\tContrary to the abstractmethod decorator from the abc module that raises a TypeError
\twhen you try to instantiate a class that has abstract methods, this decorator raises
\ta NotImplementedError ONLY when the decorated function is called, indicating that the function
\tmust be implemented by a subclass.

\tArgs:
\t\tfunc                (Callable[..., Any] | None): The function to mark as abstract
\t\terror_log           (LogLevels):                 Log level for the error handling
\t\t\tLogLevels.NONE:              None
\t\t\tLogLevels.WARNING:           Show as warning
\t\t\tLogLevels.WARNING_TRACEBACK: Show as warning with traceback
\t\t\tLogLevels.ERROR_TRACEBACK:   Show as error with traceback
\t\t\tLogLevels.RAISE_EXCEPTION:   Raise exception

\tReturns:
\t\tCallable[..., Any]: Decorator that raises NotImplementedError when called

\tExamples:
\t\t>>> class Base:
\t\t...     @abstract
\t\t...     def method(self):
\t\t...         pass
\t\t>>> Base().method()
\t\tTraceback (most recent call last):
\t\t\t...
\t\tNotImplementedError: Function 'method' is abstract and must be implemented by a subclass
\t"""
def deprecated(func: Callable[..., Any] | None = None, *, message: str = '', version: str = '', error_log: LogLevels = ...) -> Callable[..., Any]:
    ''' Decorator that marks a function as deprecated.

\tArgs:
\t\tfunc        (Callable[..., Any] | None): Function to mark as deprecated
\t\tmessage     (str):                       Additional message to display with the deprecation warning
\t\tversion     (str):                       Version since when the function is deprecated (e.g. "v1.2.0")
\t\terror_log   (LogLevels):                 Log level for the deprecation warning
\t\t\tLogLevels.NONE:              None
\t\t\tLogLevels.WARNING:           Show as warning
\t\t\tLogLevels.WARNING_TRACEBACK: Show as warning with traceback
\t\t\tLogLevels.ERROR_TRACEBACK:   Show as error with traceback
\t\t\tLogLevels.RAISE_EXCEPTION:   Raise exception
\tReturns:
\t\tCallable[..., Any]: Decorator that marks a function as deprecated

\tExamples:
\t\t>>> @deprecated
\t\t... def old_function():
\t\t...     pass

\t\t>>> @deprecated(message="Use \'new_function()\' instead", error_log=LogLevels.WARNING)
\t\t... def another_old_function():
\t\t...     pass
\t'''
def silent(func: Callable[..., Any] | None = None, *, mute_stderr: bool = False) -> Callable[..., Any]:
    ''' Decorator that makes a function silent (disable stdout, and stderr if specified).

\tAlternative to stouputils.ctx.Muffle.

\tArgs:
\t\tfunc\t\t\t(Callable[..., Any] | None):\tFunction to make silent
\t\tmute_stderr\t\t(bool):\t\t\t\t\t\t\tWhether to mute stderr or not

\tExamples:
\t\t>>> @silent
\t\t... def test():
\t\t...     print("Hello, world!")
\t\t>>> test()

\t\t>>> @silent(mute_stderr=True)
\t\t... def test2():
\t\t...     print("Hello, world!")
\t\t>>> test2()

\t\t>>> silent(print)("Hello, world!")
\t'''
def _get_func_name(func: Callable[..., Any]) -> str:
    ''' Get the name of a function, returns "<unknown>" if the name cannot be retrieved. '''
def _get_wrapper_name(decorator_name: str, func: Callable[..., Any]) -> str:
    ''' Get a descriptive name for a wrapper function.

\tArgs:
\t\tdecorator_name\t(str):\t\t\t\t\tName of the decorator
\t\tfunc\t\t\t(Callable[..., Any]):\tFunction being decorated
\tReturns:
\t\tstr: Combined name for the wrapper function (e.g., "stouputils.decorators.handle_error@function_name")
\t'''
