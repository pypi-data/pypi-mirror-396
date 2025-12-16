from .decorators import LogLevels as LogLevels, deprecated as deprecated
from .io import csv_dump as csv_dump, csv_load as csv_load, json_dump as json_dump, json_load as json_load
from typing import Any

def super_csv_dump(*args: Any, **kwargs: Any) -> Any:
    ''' Deprecated function, use "csv_dump" instead. '''
def super_csv_load(*args: Any, **kwargs: Any) -> Any:
    ''' Deprecated function, use "csv_load" instead. '''
def super_json_dump(*args: Any, **kwargs: Any) -> Any:
    ''' Deprecated function, use "json_dump" instead. '''
def super_json_load(*args: Any, **kwargs: Any) -> Any:
    ''' Deprecated function, use "json_load" instead. '''
