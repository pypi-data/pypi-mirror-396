# -*- coding: utf-8 -*-

"""
Git CLI related utilities.
"""

import typing as T
import os
import subprocess
import contextlib
from pathlib import Path


@contextlib.contextmanager
def temp_cwd(path: T.Union[str, Path]):  # pragma: no cover
    """
    Temporarily set the current working directory (CWD) and automatically
    switch back when it's done.

    Example:

    .. code-block:: python

        with temp_cwd(Path("/path/to/target/working/directory")):
            # do something
    """
    path = Path(path).absolute()
    if not path.is_dir():
        raise NotADirectoryError(f"{path} is not a dir!")
    cwd = os.getcwd()
    os.chdir(str(path))
    try:
        yield path
    finally:
        os.chdir(cwd)


class GitCLIError(Exception):
    pass


def locate_dir_repo(path: Path) -> Path:
    """
    Locate the directory of the git repository. Similar to the effect of
    ``git rev-parse --show-toplevel``.
    """
    if path.joinpath(".git").exists():
        return path
    if path.parent == path:
        raise FileNotFoundError("Cannot find the .git folder!")
    return locate_dir_repo(path.parent)


def get_git_branch_from_git_cli(dir_repo: T.Union[str, Path]) -> str:
    """
    Use ``git`` CLI to get the current git branch.

    Run:

    .. code-block:: bash

        cd $dir_repo
        git branch --show-current
    """
    try:
        with temp_cwd(dir_repo):
            args = ["git", "branch", "--show-current"]
            res = subprocess.run(args, capture_output=True, check=True)
            branch = res.stdout.decode("utf-8").strip()
            return branch
    except Exception as e:  # pragma: no cover
        raise GitCLIError(str(e))


def get_git_commit_id_from_git_cli(dir_repo: T.Union[str, Path]) -> str:
    """
    Use ``git`` CIL to get current git commit id.

    Run:

    .. code-block:: bash

        cd $dir_repo
        git rev-parse HEAD
    """
    try:
        with temp_cwd(dir_repo):
            args = ["git", "rev-parse", "HEAD"]
            res = subprocess.run(
                args,
                capture_output=True,
                check=True,
            )
            commit_id = res.stdout.decode("utf-8").strip()
            return commit_id
    except Exception as e:  # pragma: no cover
        raise GitCLIError(str(e))


def get_commit_message_by_commit_id(
    dir_repo: T.Union[str, Path],
    commit_id: str,
) -> str:
    """
    Get the first line of commit message.

    Run:

    .. code-block:: bash

        cd $dir_repo
        git log --format=%B -n 1 ${commit_id}
    """
    try:
        with temp_cwd(dir_repo):
            args = ["git", "log", "--format=%B", "-n", "1", commit_id]
            response = subprocess.run(args, capture_output=True, check=True)
    except Exception as e:  # pragma: no cover
        raise GitCLIError(str(e))
    message = response.stdout.decode("utf-8")
    message = message.strip().split("\n")[0].replace("'", "").replace('"', "").strip()
    return message
