# -*- coding: utf-8 -*-

import fire
import typing as T
from pathlib import Path

from .find_web_url import get_web_url, CURRENT_BRANCH, DEFAULT_BRANCH


DEFAULT = "default"


def main(
    path: str | None = None,
    branch: str | None = None,
):
    """
    Print the url you can one-click to open it in web browser.

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


def run():
    fire.Fire(main)
