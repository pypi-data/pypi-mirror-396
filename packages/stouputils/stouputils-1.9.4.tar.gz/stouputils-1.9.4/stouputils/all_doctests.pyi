from . import decorators as decorators
from .decorators import measure_time as measure_time
from .io import clean_path as clean_path, relative_path as relative_path
from .print import error as error, info as info, progress as progress, warning as warning
from doctest import TestResults as TestResults
from types import ModuleType

def launch_tests(root_dir: str, strict: bool = True) -> int:
    ''' Main function to launch tests for all modules in the given directory.

\tArgs:
\t\troot_dir\t\t\t\t(str):\t\t\tRoot directory to search for modules
\t\tstrict\t\t\t\t\t(bool):\t\t\tModify the force_raise_exception variable to True in the decorators module

\tReturns:
\t\tint: The number of failed tests

\tExamples:
\t\t>>> launch_tests("unknown_dir")
\t\tTraceback (most recent call last):
\t\t\t...
\t\tValueError: No modules found in \'unknown_dir\'

\t.. code-block:: python

\t\t> if launch_tests("/path/to/source") > 0:
\t\t\tsys.exit(1)
\t\t[PROGRESS HH:MM:SS] Importing module \'module1\'\ttook 0.001s
\t\t[PROGRESS HH:MM:SS] Importing module \'module2\'\ttook 0.002s
\t\t[PROGRESS HH:MM:SS] Importing module \'module3\'\ttook 0.003s
\t\t[PROGRESS HH:MM:SS] Importing module \'module4\'\ttook 0.004s
\t\t[INFO HH:MM:SS] Testing 4 modules...
\t\t[PROGRESS HH:MM:SS] Testing module \'module1\'\ttook 0.005s
\t\t[PROGRESS HH:MM:SS] Testing module \'module2\'\ttook 0.006s
\t\t[PROGRESS HH:MM:SS] Testing module \'module3\'\ttook 0.007s
\t\t[PROGRESS HH:MM:SS] Testing module \'module4\'\ttook 0.008s
\t'''
def test_module_with_progress(module: ModuleType, separator: str) -> TestResults:
    """ Test a module with testmod and measure the time taken with progress printing.

\tArgs:
\t\tmodule\t\t(ModuleType):\tModule to test
\t\tseparator\t(str):\t\t\tSeparator string for alignment in output
\tReturns:
\t\tTestResults: The results of the tests
\t"""
