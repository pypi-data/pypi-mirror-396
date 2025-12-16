from typing import Any, IO

def get_root_path(relative_path: str, go_up: int = 0) -> str:
    """ Get the absolute path of the directory.
\tUsually used to get the root path of the project using the __file__ variable.

\tArgs:
\t\trelative_path   (str): The path to get the absolute directory path from
\t\tgo_up           (int): Number of parent directories to go up (default: 0)
\tReturns:
\t\tstr: The absolute path of the directory

\tExamples:

\t\t.. code-block:: python

\t\t\t> get_root_path(__file__)
\t\t\t'C:/Users/Alexandre-PC/AppData/Local/Programs/Python/Python310/lib/site-packages/stouputils'

\t\t\t> get_root_path(__file__, 3)
\t\t\t'C:/Users/Alexandre-PC/AppData/Local/Programs/Python/Python310'
\t"""
def relative_path(file_path: str, relative_to: str = '') -> str:
    ''' Get the relative path of a file relative to a given directory.

\tArgs:
\t\tfile_path     (str): The path to get the relative path from
\t\trelative_to   (str): The path to get the relative path to (default: current working directory -> os.getcwd())
\tReturns:
\t\tstr: The relative path of the file
\tExamples:

\t\t>>> relative_path("D:/some/random/path/stouputils/io.py", "D:\\\\some")
\t\t\'random/path/stouputils/io.py\'
\t\t>>> relative_path("D:/some/random/path/stouputils/io.py", "D:\\\\some\\\\")
\t\t\'random/path/stouputils/io.py\'
\t'''
def json_dump(data: Any, file: IO[Any] | str | None = None, max_level: int | None = 2, indent: str | int = '\t', suffix: str = '\n') -> str:
    ''' Writes the provided data to a JSON file with a specified indentation depth.
\tFor instance, setting max_level to 2 will limit the indentation to 2 levels.

\tArgs:
\t\tdata\t\t(Any): \t\t\t\tThe data to dump (usually a dict or a list)
\t\tfile\t\t(IO[Any] | str): \tThe file object or path to dump the data to
\t\tmax_level\t(int | None):\t\tThe depth of indentation to stop at (-1 for infinite), None will default to 2
\t\tindent\t\t(str | int):\t\tThe indentation character (default: \'\\t\')
\t\tsuffix\t\t(str):\t\t\t\tThe suffix to add at the end of the string (default: \'\\n\')
\tReturns:
\t\tstr: The content of the file in every case

\t>>> json_dump({"a": [[1,2,3]], "b": 2}, max_level = 0)
\t\'{"a": [[1,2,3]],"b": 2}\\n\'
\t>>> json_dump({"a": [[1,2,3]], "b": 2}, max_level = 1)
\t\'{\\n\\t"a": [[1,2,3]],\\n\\t"b": 2\\n}\\n\'
\t>>> json_dump({"a": [[1,2,3]], "b": 2}, max_level = 2)
\t\'{\\n\\t"a": [\\n\\t\\t[1,2,3]\\n\\t],\\n\\t"b": 2\\n}\\n\'
\t>>> json_dump({"a": [[1,2,3]], "b": 2}, max_level = 3)
\t\'{\\n\\t"a": [\\n\\t\\t[\\n\\t\\t\\t1,\\n\\t\\t\\t2,\\n\\t\\t\\t3\\n\\t\\t]\\n\\t],\\n\\t"b": 2\\n}\\n\'
\t'''
def json_load(file_path: str) -> Any:
    """ Load a JSON file from the given path

\tArgs:
\t\tfile_path (str): The path to the JSON file
\tReturns:
\t\tAny: The content of the JSON file
\t"""
def csv_dump(data: Any, file: IO[Any] | str | None = None, delimiter: str = ',', has_header: bool = True, index: bool = False, *args: Any, **kwargs: Any) -> str:
    ''' Writes data to a CSV file with customizable options and returns the CSV content as a string.

\tArgs:
\t\tdata\t\t(list[list[Any]] | list[dict[str, Any]] | pd.DataFrame | pl.DataFrame):
\t\t\t\t\t\tThe data to write, either a list of lists, list of dicts, pandas DataFrame, or Polars DataFrame
\t\tfile\t\t(IO[Any] | str): The file object or path to dump the data to
\t\tdelimiter\t(str): The delimiter to use (default: \',\')
\t\thas_header\t(bool): Whether to include headers (default: True, applies to dict and DataFrame data)
\t\tindex\t\t(bool): Whether to include the index (default: False, only applies to pandas DataFrame)
\t\t*args\t\t(Any): Additional positional arguments to pass to the underlying CSV writer or DataFrame method
\t\t**kwargs\t(Any): Additional keyword arguments to pass to the underlying CSV writer or DataFrame method
\tReturns:
\t\tstr: The CSV content as a string

\tExamples:

\t\t>>> csv_dump([["a", "b", "c"], [1, 2, 3], [4, 5, 6]])
\t\t\'a,b,c\\r\\n1,2,3\\r\\n4,5,6\\r\\n\'

\t\t>>> csv_dump([{"name": "Alice", "age": 30}, {"name": "Bob", "age": 25}])
\t\t\'name,age\\r\\nAlice,30\\r\\nBob,25\\r\\n\'
\t'''
def csv_load(file_path: str, delimiter: str = ',', has_header: bool = True, as_dict: bool = False, as_dataframe: bool = False, use_polars: bool = False, *args: Any, **kwargs: Any) -> Any:
    ''' Load a CSV file from the given path

\tArgs:
\t\tfile_path (str): The path to the CSV file
\t\tdelimiter (str): The delimiter used in the CSV (default: \',\')
\t\thas_header (bool): Whether the CSV has a header row (default: True)
\t\tas_dict (bool): Whether to return data as list of dicts (default: False)
\t\tas_dataframe (bool): Whether to return data as a DataFrame (default: False)
\t\tuse_polars (bool): Whether to use Polars instead of pandas for DataFrame (default: False, requires polars)
\t\t*args: Additional positional arguments to pass to the underlying CSV reader or DataFrame method
\t\t**kwargs: Additional keyword arguments to pass to the underlying CSV reader or DataFrame method
\tReturns:
\t\tlist[list[str]] | list[dict[str, str]] | pd.DataFrame | pl.DataFrame: The content of the CSV file

\tExamples:

\t\t.. code-block:: python

\t\t\t> Assuming "test.csv" contains: a,b,c\\n1,2,3\\n4,5,6
\t\t\t> csv_load("test.csv")
\t\t\t[[\'1\', \'2\', \'3\'], [\'4\', \'5\', \'6\']]

\t\t\t> csv_load("test.csv", as_dict=True)
\t\t\t[{\'a\': \'1\', \'b\': \'2\', \'c\': \'3\'}, {\'a\': \'4\', \'b\': \'5\', \'c\': \'6\'}]

\t\t\t> csv_load("test.csv", as_dataframe=True)
\t\t\t   a  b  c
\t\t\t0  1  2  3
\t\t\t1  4  5  6

\t\t.. code-block:: console

\t\t\t> csv_load("test.csv", as_dataframe=True, use_polars=True)
\t\t\tshape: (2, 3)
\t\t\t┌─────┬─────┬─────┐
\t\t\t│ a   ┆ b   ┆ c   │
\t\t\t│ --- ┆ --- ┆ --- │
\t\t\t│ i64 ┆ i64 ┆ i64 │
\t\t\t╞═════╪═════╪═════╡
\t\t\t│ 1   ┆ 2   ┆ 3   │
\t\t\t│ 4   ┆ 5   ┆ 6   │
\t\t\t└─────┴─────┴─────┘
\t'''
def super_copy(src: str, dst: str, create_dir: bool = True, symlink: bool = False) -> str:
    """ Copy a file (or a folder) from the source to the destination

\tArgs:
\t\tsrc         (str):  The source path
\t\tdst         (str):  The destination path
\t\tcreate_dir  (bool): Whether to create the directory if it doesn't exist (default: True)
\t\tsymlink     (bool): Whether to create a symlink instead of copying (Linux only, default: True)
\tReturns:
\t\tstr: The destination path
\t"""
def super_open(file_path: str, mode: str, encoding: str = 'utf-8') -> IO[Any]:
    ''' Open a file with the given mode, creating the directory if it doesn\'t exist (only if writing)

\tArgs:
\t\tfile_path\t(str): The path to the file
\t\tmode\t\t(str): The mode to open the file with, ex: "w", "r", "a", "wb", "rb", "ab"
\t\tencoding\t(str): The encoding to use when opening the file (default: "utf-8")
\tReturns:
\t\topen: The file object, ready to be used
\t'''
def read_file(file_path: str, encoding: str = 'utf-8') -> str:
    ''' Read the content of a file and return it as a string

\tArgs:
\t\tfile_path (str): The path to the file
\t\tencoding  (str): The encoding to use when opening the file (default: "utf-8")
\tReturns:
\t\tstr: The content of the file
\t'''
def replace_tilde(path: str) -> str:
    ''' Replace the "~" by the user\'s home directory

\tArgs:
\t\tpath (str): The path to replace the "~" by the user\'s home directory
\tReturns:
\t\tstr: The path with the "~" replaced by the user\'s home directory
\tExamples:

\t\t.. code-block:: python

\t\t\t> replace_tilde("~/Documents/test.txt")
\t\t\t\'/home/user/Documents/test.txt\'
\t'''
def clean_path(file_path: str, trailing_slash: bool = True) -> str:
    ''' Clean the path by replacing backslashes with forward slashes and simplifying the path

\tArgs:
\t\tfile_path (str): The path to clean
\t\ttrailing_slash (bool): Whether to keep the trailing slash, ex: "test/" -> "test/"
\tReturns:
\t\tstr: The cleaned path
\tExamples:
\t\t>>> clean_path("C:\\\\Users\\\\Stoupy\\\\Documents\\\\test.txt")
\t\t\'C:/Users/Stoupy/Documents/test.txt\'

\t\t>>> clean_path("Some Folder////")
\t\t\'Some Folder/\'

\t\t>>> clean_path("test/uwu/1/../../")
\t\t\'test/\'

\t\t>>> clean_path("some/./folder/../")
\t\t\'some/\'

\t\t>>> clean_path("folder1/folder2/../../folder3")
\t\t\'folder3\'

\t\t>>> clean_path("./test/./folder/")
\t\t\'test/folder/\'

\t\t>>> clean_path("C:/folder1\\\\folder2")
\t\t\'C:/folder1/folder2\'
\t'''
