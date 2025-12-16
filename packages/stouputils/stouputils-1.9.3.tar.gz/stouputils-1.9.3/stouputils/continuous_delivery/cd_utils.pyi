import requests
from ..decorators import handle_error as handle_error
from ..io import clean_path as clean_path, json_load as json_load
from ..print import warning as warning
from typing import Any

def load_credentials(credentials_path: str) -> dict[str, Any]:
    ''' Load credentials from a JSON or YAML file into a dictionary.

\tLoads credentials from either a JSON or YAML file and returns them as a dictionary.
\tThe file must contain the required credentials in the appropriate format.

\tArgs:
\t\tcredentials_path (str): Path to the credentials file (.json or .yml)
\tReturns:
\t\tdict[str, Any]: Dictionary containing the credentials

\tExample JSON format:

\t.. code-block:: json

\t\t{
\t\t\t"github": {
\t\t\t\t"username": "Stoupy51",
\t\t\t\t"api_key": "ghp_XXXXXXXXXXXXXXXXXXXXXXXXXX"
\t\t\t}
\t\t}

\tExample YAML format:

\t.. code-block:: yaml

\t\tgithub:
\t\t\tusername: "Stoupy51"
\t\t\tapi_key: "ghp_XXXXXXXXXXXXXXXXXXXXXXXXXX"
\t'''
def handle_response(response: requests.Response, error_message: str) -> None:
    """ Handle a response from the API by raising an error if the response is not successful (status code not in 200-299).

\tArgs:
\t\tresponse\t\t(requests.Response): The response from the API
\t\terror_message\t(str): The error message to raise if the response is not successful
\t"""
def clean_version(version: str, keep: str = '') -> str:
    ''' Clean a version string

\tArgs:
\t\tversion\t(str): The version string to clean
\t\tkeep\t(str): The characters to keep in the version string
\tReturns:
\t\tstr: The cleaned version string

\t>>> clean_version("v1.e0.zfezf0.1.2.3zefz")
\t\'1.0.0.1.2.3\'
\t>>> clean_version("v1.e0.zfezf0.1.2.3zefz", keep="v")
\t\'v1.0.0.1.2.3\'
\t>>> clean_version("v1.2.3b", keep="ab")
\t\'1.2.3b\'
\t'''
def version_to_float(version: str) -> float:
    ''' Converts a version string into a float for comparison purposes.
\tThe version string is expected to follow the format of major.minor.patch.something_else....,
\twhere each part is separated by a dot and can be extended indefinitely.
\tSupports pre-release suffixes with numbers: devN/dN (dev), aN (alpha), bN (beta), rcN/cN (release candidate).
\tOrdering: 1.0.0 > 1.0.0rc2 > 1.0.0rc1 > 1.0.0b2 > 1.0.0b1 > 1.0.0a2 > 1.0.0a1 > 1.0.0dev1

\tArgs:
\t\tversion (str): The version string to convert. (e.g. "v1.0.0.1.2.3", "v2.0.0b2", "v1.0.0rc1")
\tReturns:
\t\tfloat: The float representation of the version. (e.g. 0)

\t>>> version_to_float("v1.0.0")
\t1.0
\t>>> version_to_float("v1.0.0.1")
\t1.000000001
\t>>> version_to_float("v2.3.7")
\t2.003007
\t>>> version_to_float("v1.0.0.1.2.3")
\t1.0000000010020031
\t>>> version_to_float("v2.0") > version_to_float("v1.0.0.1")
\tTrue
\t>>> version_to_float("v2.0.0") > version_to_float("v2.0.0rc") > version_to_float("v2.0.0b") > version_to_float("v2.0.0a") > version_to_float("v2.0.0dev")
\tTrue
\t>>> version_to_float("v1.0.0b") > version_to_float("v1.0.0a")
\tTrue
\t>>> version_to_float("v1.0.0") > version_to_float("v1.0.0b")
\tTrue
\t>>> version_to_float("v3.0.0a") > version_to_float("v2.9.9")
\tTrue
\t>>> version_to_float("v1.2.3b") < version_to_float("v1.2.3")
\tTrue
\t>>> version_to_float("1.0.0") == version_to_float("v1.0.0")
\tTrue
\t>>> version_to_float("2.0.0.0.0.0.1b") > version_to_float("2.0.0.0.0.0.1a")
\tTrue
\t>>> version_to_float("2.0.0.0.0.0.1") > version_to_float("2.0.0.0.0.0.1b")
\tTrue
\t>>> version_to_float("v1.0.0rc") == version_to_float("v1.0.0c")
\tTrue
\t>>> version_to_float("v1.0.0c") > version_to_float("v1.0.0b")
\tTrue
\t>>> version_to_float("v1.0.0d") < version_to_float("v1.0.0a")
\tTrue
\t>>> version_to_float("v1.0.0dev") < version_to_float("v1.0.0a")
\tTrue
\t>>> version_to_float("v1.0.0dev") == version_to_float("v1.0.0d")
\tTrue
\t>>> version_to_float("v1.0.0rc2") > version_to_float("v1.0.0rc1")
\tTrue
\t>>> version_to_float("v1.0.0b2") > version_to_float("v1.0.0b1")
\tTrue
\t>>> version_to_float("v1.0.0a2") > version_to_float("v1.0.0a1")
\tTrue
\t>>> version_to_float("v1.0.0dev2") > version_to_float("v1.0.0dev1")
\tTrue
\t>>> version_to_float("v1.0.0") > version_to_float("v1.0.0rc2") > version_to_float("v1.0.0rc1")
\tTrue
\t>>> version_to_float("v1.0.0rc1") > version_to_float("v1.0.0b2")
\tTrue
\t>>> version_to_float("v1.0.0b1") > version_to_float("v1.0.0a2")
\tTrue
\t>>> version_to_float("v1.0.0a1") > version_to_float("v1.0.0dev2")
\tTrue
\t>>> versions = ["v1.0.0", "v1.0.0rc2", "v1.0.0rc1", "v1.0.0b2", "v1.0.0b1", "v1.0.0a2", "v1.0.0a1", "v1.0.0dev2", "v1.0.0dev1"]
\t>>> sorted_versions = sorted(versions, key=version_to_float, reverse=True)
\t>>> sorted_versions == versions
\tTrue
\t'''
