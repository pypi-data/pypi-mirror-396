# -*- coding: utf-8 -*-

"""
Git repository utility functions.

This module provides utility functions for working with local git repositories,
including locating the repository root directory, extracting remote origin URLs,
and determining the current branch.
"""

from pathlib import Path
from configparser import ConfigParser
from .exc import NotGitRepoError


def locate_git_repo_dir(
    p_file: Path,
) -> Path:
    """
    Locate the git repository root directory for a given path.

    Starting from the given file or directory path, this function traverses
    up the directory tree to find the git repository root. The root is identified
    by the presence of a ``.git/config`` file.

    :param p_file: The path to a file or directory within a git repository.

    :return: The path to the git repository root directory.

    :raises NotGitRepoError: If the given path is not within a git repository.
    """
    if p_file.is_dir():
        p_git_config = Path(p_file, ".git", "config")
        if p_git_config.exists():
            return p_file
    for p_dir in p_file.parents:
        p_git_config = Path(p_dir, ".git", "config")
        if p_git_config.exists():
            return p_dir
    raise NotGitRepoError(f"{p_file} is not in a git repository.")


def extract_remote_origin_url(
    p_git_config: Path,
) -> str:
    """
    Extract the remote origin URL from a git config file.

    Parses the ``.git/config`` file to retrieve the URL configured for
    the ``origin`` remote.

    :param p_git_config: The path to the ``.git/config`` file.

    :return: The URL of the remote origin.
    """
    config = ConfigParser()
    config.read(str(p_git_config))
    remote_origin_url = config['remote "origin"']["url"]
    return remote_origin_url


def extract_current_branch(
    p_git_head: Path,
) -> str:
    """
    Extract the current branch name from a git HEAD file.

    Reads the ``.git/HEAD`` file and parses it to determine the currently
    checked-out branch. The HEAD file typically contains a reference like
    ``ref: refs/heads/<branch_name>``.

    :param p_git_head: The path to the ``.git/HEAD`` file.

    :return: The name of the current branch.
    """
    current_branch = p_git_head.read_text().strip().replace("ref: refs/heads/", "")
    return current_branch
