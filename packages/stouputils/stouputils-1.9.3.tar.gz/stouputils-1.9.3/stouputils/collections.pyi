import polars as pl
import zarr
from numpy.typing import NDArray as NDArray
from typing import Any, Literal, TypeVar

T = TypeVar('T')

def unique_list(list_to_clean: list[Any], method: Literal['id', 'hash', 'str'] = 'str') -> list[Any]:
    ''' Remove duplicates from the list while keeping the order using ids (default) or hash or str

\tArgs:
\t\tlist_to_clean\t(list[Any]):\t\t\t\t\tThe list to clean
\t\tmethod\t\t\t(Literal["id", "hash", "str"]):\tThe method to use to identify duplicates
\tReturns:
\t\tlist[Any]: The cleaned list

\tExamples:
\t\t>>> unique_list([1, 2, 3, 2, 1], method="id")
\t\t[1, 2, 3]

\t\t>>> s1 = {1, 2, 3}
\t\t>>> s2 = {2, 3, 4}
\t\t>>> s3 = {1, 2, 3}
\t\t>>> unique_list([s1, s2, s1, s1, s3, s2, s3], method="id")
\t\t[{1, 2, 3}, {2, 3, 4}, {1, 2, 3}]

\t\t>>> s1 = {1, 2, 3}
\t\t>>> s2 = {2, 3, 4}
\t\t>>> s3 = {1, 2, 3}
\t\t>>> unique_list([s1, s2, s1, s1, s3, s2, s3], method="str")
\t\t[{1, 2, 3}, {2, 3, 4}]
\t'''
def sort_dict_keys(dictionary: dict[T, Any], order: list[T], reverse: bool = False) -> dict[T, Any]:
    ''' Sort dictionary keys using a given order list (reverse optional)

\tArgs:
\t\tdictionary\t(dict[T, Any]):\tThe dictionary to sort
\t\torder\t\t(list[T]):\t\tThe order list
\t\treverse\t\t(bool):\t\t\tWhether to sort in reverse order (given to sorted function which behaves differently than order.reverse())
\tReturns:
\t\tdict[T, Any]: The sorted dictionary

\tExamples:
\t\t>>> sort_dict_keys({\'b\': 2, \'a\': 1, \'c\': 3}, order=["a", "b", "c"])
\t\t{\'a\': 1, \'b\': 2, \'c\': 3}

\t\t>>> sort_dict_keys({\'b\': 2, \'a\': 1, \'c\': 3}, order=["a", "b", "c"], reverse=True)
\t\t{\'c\': 3, \'b\': 2, \'a\': 1}

\t\t>>> sort_dict_keys({\'b\': 2, \'a\': 1, \'c\': 3, \'d\': 4}, order=["c", "b"])
\t\t{\'c\': 3, \'b\': 2, \'a\': 1, \'d\': 4}
\t'''
def upsert_in_dataframe(df: pl.DataFrame, new_entry: dict[str, Any], primary_keys: dict[str, Any] | None = None) -> pl.DataFrame:
    """ Insert or update a row in the Polars DataFrame based on primary keys.

\tArgs:
\t\tdf\t\t\t\t(pl.DataFrame):\t\tThe Polars DataFrame to update.
\t\tnew_entry\t\t(dict[str, Any]):\tThe new entry to insert or update.
\t\tprimary_keys\t(dict[str, Any]):\tThe primary keys to identify the row (default: empty).
\tReturns:
\t\tpl.DataFrame: The updated Polars DataFrame.
\t"""
def array_to_disk(data: NDArray[Any] | zarr.Array, delete_input: bool = True, more_data: NDArray[Any] | zarr.Array | None = None) -> tuple['zarr.Array', str, int]:
    """ Easily handle large numpy arrays on disk using zarr for efficient storage and access.

\tZarr provides a simpler and more efficient alternative to np.memmap with better compression
\tand chunking capabilities.

\tArgs:
\t\tdata\t\t\t(NDArray | zarr.Array):\tThe data to save/load as a zarr array
\t\tdelete_input\t(bool):\tWhether to delete the input data after creating the zarr array
\t\tmore_data\t\t(NDArray | zarr.Array | None): Additional data to append to the zarr array
\tReturns:
\t\ttuple[zarr.Array, str, int]: The zarr array, the directory path, and the total size in bytes

\tExamples:
\t\t>>> import numpy as np
\t\t>>> data = np.random.rand(1000, 1000)
\t\t>>> zarr_array = array_to_disk(data)[0]
\t\t>>> zarr_array.shape
\t\t(1000, 1000)

\t\t>>> more_data = np.random.rand(500, 1000)
\t\t>>> longer_array, dir_path, total_size = array_to_disk(zarr_array, more_data=more_data)
\t"""
