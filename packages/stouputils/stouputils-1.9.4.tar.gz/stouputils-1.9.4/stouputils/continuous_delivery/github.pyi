from ..decorators import handle_error as handle_error, measure_time as measure_time
from ..io import clean_path as clean_path
from ..print import info as info, progress as progress, warning as warning
from .cd_utils import clean_version as clean_version, handle_response as handle_response, version_to_float as version_to_float
from typing import Any

GITHUB_API_URL: str
PROJECT_ENDPOINT: str
COMMIT_TYPES: dict[str, str]

def validate_credentials(credentials: dict[str, dict[str, str]]) -> tuple[str, dict[str, str]]:
    """ Get and validate GitHub credentials

\tArgs:
\t\tcredentials (dict[str, dict[str, str]]):\tCredentials for the GitHub API
\tReturns:
\t\ttuple[str, dict[str, str]]:
\t\t\tstr:\t\t\tOwner (the username of the account to use)

\t\t\tdict[str, str]:\tHeaders (for the requests to the GitHub API)
\t"""
def validate_config(github_config: dict[str, Any]) -> tuple[str, str, str, list[str]]:
    """ Validate GitHub configuration

\tArgs:
\t\tgithub_config (dict[str, str]):\tConfiguration for the GitHub project
\tReturns:
\t\ttuple[str, str, str, list[str]]:
\t\t\tstr: Project name on GitHub

\t\t\tstr: Version of the project

\t\t\tstr: Build folder path containing zip files to upload to the release

\t\t\tlist[str]: List of zip files to upload to the release
\t"""
def handle_existing_tag(owner: str, project_name: str, version: str, headers: dict[str, str]) -> bool:
    """ Check if tag exists and handle deletion if needed

\tArgs:
\t\towner\t\t\t(str):\t\t\t\tGitHub username
\t\tproject_name\t(str):\t\t\t\tName of the GitHub repository
\t\tversion\t\t\t(str):\t\t\t\tVersion to check for existing tag
\t\theaders\t\t\t(dict[str, str]):\tHeaders for GitHub API requests
\tReturns:
\t\tbool: True if the tag was deleted or if it was not found, False otherwise
\t"""
def delete_existing_release(owner: str, project_name: str, version: str, headers: dict[str, str]) -> None:
    """ Delete existing release for a version

\tArgs:
\t\towner\t\t\t(str):\t\t\t\tGitHub username
\t\tproject_name\t(str):\t\t\t\tName of the GitHub repository
\t\tversion\t\t\t(str):\t\t\t\tVersion of the release to delete
\t\theaders\t\t\t(dict[str, str]):\tHeaders for GitHub API requests
\t"""
def delete_existing_tag(tag_url: str, headers: dict[str, str]) -> None:
    """ Delete existing tag

\tArgs:
\t\ttag_url\t(str):\t\t\t\tURL of the tag to delete
\t\theaders\t(dict[str, str]):\tHeaders for GitHub API requests
\t"""
def get_latest_tag(owner: str, project_name: str, version: str, headers: dict[str, str]) -> tuple[str, str] | tuple[None, None]:
    """ Get latest tag information

\tArgs:
\t\towner\t\t\t(str):\t\t\t\tGitHub username
\t\tproject_name\t(str):\t\t\t\tName of the GitHub repository
\t\tversion\t\t\t(str):\t\t\t\tVersion to remove from the list of tags
\t\theaders\t\t\t(dict[str, str]):\tHeaders for GitHub API requests
\tReturns:
\t\tstr|None: SHA of the latest tag commit, None if no tags exist
\t\tstr|None: Version number of the latest tag, None if no tags exist
\t"""
def get_commits_since_tag(owner: str, project_name: str, latest_tag_sha: str | None, headers: dict[str, str]) -> list[dict[str, Any]]:
    """ Get commits since last tag

\tArgs:
\t\towner\t\t\t(str):\t\t\t\tGitHub username
\t\tproject_name\t(str):\t\t\t\tName of the GitHub repository
\t\tlatest_tag_sha\t(str|None):\t\t\tSHA of the latest tag commit
\t\theaders\t\t\t(dict[str, str]):\tHeaders for GitHub API requests
\tReturns:
\t\tlist[dict]: List of commits since the last tag
\t"""
def generate_changelog(commits: list[dict[str, Any]], owner: str, project_name: str, latest_tag_version: str | None, version: str) -> str:
    """ Generate changelog from commits. They must follow the conventional commits convention.

\tConvention format: <type>: <description> or <type>(<sub-category>): <description>

\tArgs:
\t\tcommits\t\t\t\t(list[dict]):\tList of commits to generate changelog from
\t\towner\t\t\t\t(str):\t\t\tGitHub username
\t\tproject_name\t\t(str):\t\t\tName of the GitHub repository
\t\tlatest_tag_version\t(str|None):\t\tVersion number of the latest tag
\t\tversion\t\t\t\t(str):\t\t\tCurrent version being released
\tReturns:
\t\tstr: Generated changelog text
\tSource:
\t\thttps://www.conventionalcommits.org/en/v1.0.0/
\t"""
def create_tag(owner: str, project_name: str, version: str, headers: dict[str, str]) -> None:
    """ Create a new tag

\tArgs:
\t\towner\t\t\t(str):\t\t\t\tGitHub username
\t\tproject_name\t(str):\t\t\t\tName of the GitHub repository
\t\tversion\t\t\t(str):\t\t\t\tVersion for the new tag
\t\theaders\t\t\t(dict[str, str]):\tHeaders for GitHub API requests
\t"""
def create_release(owner: str, project_name: str, version: str, changelog: str, headers: dict[str, str]) -> int:
    """ Create a new release

\tArgs:
\t\towner\t\t\t(str):\t\t\t\tGitHub username
\t\tproject_name\t(str):\t\t\t\tName of the GitHub repository
\t\tversion\t\t\t(str):\t\t\t\tVersion for the new release
\t\tchangelog\t\t(str):\t\t\t\tChangelog text for the release
\t\theaders\t\t\t(dict[str, str]):\tHeaders for GitHub API requests
\tReturns:
\t\tint: ID of the created release
\t"""
def upload_assets(owner: str, project_name: str, release_id: int, build_folder: str, headers: dict[str, str], endswith: list[str]) -> None:
    """ Upload release assets

\tArgs:
\t\towner\t\t\t(str):\t\t\t\tGitHub username
\t\tproject_name\t(str):\t\t\t\tName of the GitHub repository
\t\trelease_id\t\t(int):\t\t\t\tID of the release to upload assets to
\t\tbuild_folder\t(str):\t\t\t\tFolder containing assets to upload
\t\theaders\t\t\t(dict[str, str]):\tHeaders for GitHub API requests
\t\tendswith\t\t(list[str]):\t\tList of files to upload to the release
\t\t\t(every file ending with one of these strings will be uploaded)
\t"""
def upload_to_github(credentials: dict[str, Any], github_config: dict[str, Any]) -> str:
    ''' Upload the project to GitHub using the credentials and the configuration

\tArgs:
\t\tcredentials\t\t(dict[str, Any]):\tCredentials for the GitHub API
\t\tgithub_config\t(dict[str, Any]):\tConfiguration for the GitHub project
\tReturns:
\t\tstr: Generated changelog text
\tExamples:

\t.. code-block:: python

\t\t> upload_to_github(
\t\t\tcredentials={
\t\t\t\t"github": {
\t\t\t\t\t"api_key": "ghp_...",
\t\t\t\t\t"username": "Stoupy"
\t\t\t\t}
\t\t\t},
\t\t\tgithub_config={
\t\t\t\t"project_name": "stouputils",
\t\t\t\t"version": "1.0.0",
\t\t\t\t"build_folder": "build",
\t\t\t\t"endswith": [".zip"]
\t\t\t}
\t\t)
\t'''
