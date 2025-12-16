# -*- coding: utf-8 -*-

import os
import fire
from pathlib import Path

from .find_web_url import get_web_url, CURRENT_BRANCH, DEFAULT_BRANCH
from .utils import locate_git_repo_dir


DEFAULT = "default"


class Command:
    """
    git_web_url CLI - Utilities for working with local git repositories.

    Usage: gwu <subcommand> [options]

    Subcommands:
        url      Print the web URL for a file or folder in the git repository.
        relpath  Print the relative path from the git repository root.
    """

    def url(
        self,
        path: str | None = None,
        branch: str | None = None,
    ):
        """
        Print the URL you can one-click to open it in web browser.

        :param path: the absolute path of the file or folder in your local git repo,
            if not given, use the current directory.
        :param branch: the branch to use in the URL.
            - None: use the current branch (default)
            - "default": use the default branch (main/master)
            - other string: use the specified branch name
        """
        if path is None:
            p = Path.cwd()
        else:
            p = Path(path)

        # Convert string branch to sentinel objects
        if branch is None:
            branch_arg = CURRENT_BRANCH
        elif branch == DEFAULT:
            branch_arg = DEFAULT_BRANCH
        else:
            branch_arg = branch

        web_url = get_web_url(p, branch=branch_arg)
        print(web_url)

    def relpath(
        self,
        path: str | None = None,
    ):
        """
        Print the relative path from the git repository root to the given path.

        :param path: the absolute path of the file or folder in your local git repo,
            if not given, use the current directory.
        """
        if path is None:
            p = Path.cwd()
        else:
            p = Path(path)

        p = p.resolve()
        repo_root = locate_git_repo_dir(p)

        if p == repo_root:
            print(".")
        else:
            rel = p.relative_to(repo_root)
            # Use OS-appropriate separator (backslash on Windows)
            print(str(rel).replace("/", os.sep))


def run():
    fire.Fire(Command)
