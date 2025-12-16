from ..io import super_open as super_open
from typing import Any

def read_pyproject(pyproject_path: str) -> dict[str, Any]:
    """ Read the pyproject.toml file.

\tArgs:
\t\tpyproject_path: Path to the pyproject.toml file.

\tReturns:
\t\tdict[str, Any]: The content of the pyproject.toml file.
\t"""
def format_toml_lists(content: str) -> str:
    """ Format TOML lists with indentation.

\tArgs:
\t\tcontent (str): The content of the pyproject.toml file.

\tReturns:
\t\tstr: The formatted content with properly indented lists.
\t"""
def write_pyproject(pyproject_path: str, pyproject_content: dict[str, Any]) -> None:
    """ Write to the pyproject.toml file with properly indented lists. """
def increment_version_from_input(version: str) -> str:
    ''' Increment the version.

\tArgs:
\t\tversion: The version to increment. (ex: "0.1.0")

\tReturns:
\t\tstr: The incremented version. (ex: "0.1.1")
\t'''
def increment_version_from_pyproject(pyproject_path: str) -> None:
    """ Increment the version in the pyproject.toml file.

\tArgs:
\t\tpyproject_path: Path to the pyproject.toml file.
\t"""
def get_version_from_pyproject(pyproject_path: str) -> str:
    ''' Get the version from the pyproject.toml file.

\tArgs:
\t\tpyproject_path: Path to the pyproject.toml file.

\tReturns:
\t\tstr: The version. (ex: "0.1.0")
\t'''
