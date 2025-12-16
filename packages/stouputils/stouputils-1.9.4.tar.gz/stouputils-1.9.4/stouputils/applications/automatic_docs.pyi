from ..continuous_delivery import version_to_float as version_to_float
from ..decorators import LogLevels as LogLevels, handle_error as handle_error, simple_cache as simple_cache
from ..io import clean_path as clean_path, json_dump as json_dump, super_open as super_open
from ..print import info as info
from collections.abc import Callable as Callable

REQUIREMENTS: list[str]

def check_dependencies(html_theme: str) -> None:
    ''' Check for each requirement if it is installed.

\tArgs:
\t\thtml_theme (str): HTML theme to use for the documentation, to check if it is installed (e.g. "breeze", "pydata_sphinx_theme", "furo", etc.)
\t'''
def get_sphinx_conf_content(project: str, project_dir: str, author: str, current_version: str, copyright: str, html_logo: str, html_favicon: str, html_theme: str = 'breeze', github_user: str = '', github_repo: str = '', version_list: list[str] | None = None, skip_undocumented: bool = True) -> str:
    """ Get the content of the Sphinx configuration file.

\tArgs:
\t\tproject           (str):              Name of the project
\t\tproject_dir       (str):              Path to the project directory
\t\tauthor            (str):              Author of the project
\t\tcurrent_version   (str):              Current version
\t\tcopyright         (str):              Copyright information
\t\thtml_logo         (str):              URL to the logo
\t\thtml_favicon      (str):              URL to the favicon
\t\tgithub_user       (str):              GitHub username
\t\tgithub_repo       (str):              GitHub repository name
\t\tversion_list      (list[str] | None): List of versions. Defaults to None
\t\tskip_undocumented (bool):             Whether to skip undocumented members. Defaults to True

\tReturns:
\t\tstr: Content of the Sphinx configuration file
\t"""
def get_versions_from_github(github_user: str, github_repo: str, recent_minor_versions: int = 2) -> list[str]:
    """ Get list of versions from GitHub gh-pages branch.
\tOnly shows detailed versions for the last N minor versions, and keeps only
\tthe latest patch version for older minor versions.

\tArgs:
\t\tgithub_user             (str): GitHub username
\t\tgithub_repo             (str): GitHub repository name
\t\trecent_minor_versions   (int): Number of recent minor versions to show all patches for (-1 for all).

\tReturns:
\t\tlist[str]: List of versions, with 'latest' as first element
\t"""
def markdown_to_rst(markdown_content: str) -> str:
    """ Convert markdown content to RST format.

\tArgs:
\t\tmarkdown_content (str): Markdown content

\tReturns:
\t\tstr: RST content
\t"""
def generate_index_rst(readme_path: str, index_path: str, project: str, github_user: str, github_repo: str, get_versions_function: Callable[[str, str, int], list[str]] = ..., recent_minor_versions: int = 2) -> None:
    """ Generate index.rst from README.md content.

\tArgs:
\t\treadme_path            (str): Path to the README.md file
\t\tindex_path             (str): Path where index.rst should be created
\t\tproject                (str): Name of the project
\t\tgithub_user            (str): GitHub username
\t\tgithub_repo            (str): GitHub repository name
\t\tget_versions_function  (Callable[[str, str, int], list[str]]): Function to get versions from GitHub
\t\trecent_minor_versions  (int): Number of recent minor versions to show all patches for. Defaults to 2
\t"""
def generate_documentation(source_dir: str, modules_dir: str, project_dir: str, build_dir: str) -> None:
    """ Generate documentation using Sphinx.

\tArgs:
\t\tsource_dir        (str): Source directory
\t\tmodules_dir       (str): Modules directory
\t\tproject_dir       (str): Project directory
\t\tbuild_dir         (str): Build directory
\t"""
def generate_redirect_html(filepath: str) -> None:
    """ Generate HTML content for redirect page.

\tArgs:
\t\tfilepath (str): Path to the file where the HTML content should be written
\t"""
def update_documentation(root_path: str, project: str, project_dir: str = '', author: str = 'Author', copyright: str = '2025, Author', html_logo: str = '', html_favicon: str = '', html_theme: str = 'breeze', github_user: str = '', github_repo: str = '', version: str | None = None, skip_undocumented: bool = True, recent_minor_versions: int = 2, get_versions_function: Callable[[str, str, int], list[str]] = ..., generate_index_function: Callable[..., None] = ..., generate_docs_function: Callable[..., None] = ..., generate_redirect_function: Callable[[str], None] = ..., get_conf_content_function: Callable[..., str] = ...) -> None:
    ''' Update the Sphinx documentation.

\tArgs:
\t\troot_path                  (str): Root path of the project
\t\tproject                    (str): Name of the project
\t\tproject_dir                (str): Path to the project directory (to be used with generate_docs_function)
\t\tauthor                     (str): Author of the project
\t\tcopyright                  (str): Copyright information
\t\thtml_logo                  (str): URL to the logo
\t\thtml_favicon               (str): URL to the favicon
\t\thtml_theme                 (str): Theme to use for the documentation. Defaults to "breeze"
\t\tgithub_user                (str): GitHub username
\t\tgithub_repo                (str): GitHub repository name
\t\tversion                    (str | None): Version to build documentation for (e.g. "1.0.0", defaults to "latest")
\t\tskip_undocumented          (bool): Whether to skip undocumented members. Defaults to True
\t\trecent_minor_versions      (int): Number of recent minor versions to show all patches for. Defaults to 2

\t\tget_versions_function      (Callable[[str, str, int], list[str]]): Function to get versions from GitHub
\t\tgenerate_index_function    (Callable[..., None]): Function to generate index.rst
\t\tgenerate_docs_function     (Callable[..., None]): Function to generate documentation
\t\tgenerate_redirect_function (Callable[[str], None]): Function to create redirect file
\t\tget_conf_content_function  (Callable[..., str]): Function to get Sphinx conf.py content
\t'''
