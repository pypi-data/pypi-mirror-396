# -*- coding: utf-8 -*-

"""
This module implements the logic to find the corresponding web url
of a local file in a local git repo.

Basically, it locate the ``.git/config`` file, extract the remote origin url,
parse it, and then generate the web url.
"""

import typing as T
from pathlib import Path

from .vendor.git_cli import get_git_commit_id_from_git_cli
from .utils import (
    locate_git_repo_dir,
    extract_remote_origin_url,
    extract_current_branch,
)
from .parser import PlatformEnum
from .find_repo_url import parse_aws_codecommit_remote_origin_url, get_repo_url


class _CurrentBranch:
    """Sentinel class representing the current git branch."""

    pass


class _DefaultBranch:
    """Sentinel class representing the default branch (main/master)."""

    pass


CURRENT_BRANCH: _CurrentBranch = _CurrentBranch()
DEFAULT_BRANCH: _DefaultBranch = _DefaultBranch()


def get_web_url(
    path: Path,
    branch: T.Union[str, _CurrentBranch, _DefaultBranch] = CURRENT_BRANCH,
):  # pragma: no cover
    """
    This module implements the logic to find the corresponding web url
    of a local file in a local git repo.

    :param path: The local file or directory path.
    :param branch: The branch to use in the URL.
        - CURRENT_BRANCH: use current branch (default behavior)
        - DEFAULT_BRANCH: use the default branch (URL without explicit branch)
        - str: use the specified branch name
    """
    p_git_repo_dir = locate_git_repo_dir(path)
    remote_origin_url = extract_remote_origin_url(
        p_git_repo_dir.joinpath(".git", "config")
    )
    repo_url, res = get_repo_url(remote_origin_url)

    # Determine git_branch based on branch parameter
    if isinstance(branch, _CurrentBranch):
        git_branch = extract_current_branch(p_git_repo_dir.joinpath(".git", "HEAD"))
    elif isinstance(branch, _DefaultBranch):
        git_branch = None  # Will generate URL without branch (default branch)
    else:
        git_branch = branch

    relative_path = str(path.relative_to(p_git_repo_dir))
    if relative_path == ".":  # if the path is already the root of the repo
        relative_path = ""

    if res.platform is PlatformEnum.aws_codecommit:
        aws_region = parse_aws_codecommit_remote_origin_url(remote_origin_url)
        if git_branch is None:
            return f"{repo_url}?region={aws_region}"
        else:
            return f"{repo_url}/browse/refs/heads/{git_branch}/--/{relative_path}?region={aws_region}"
    elif res.platform is PlatformEnum.bitbucket:  # bitbucket saas
        if res.domain == "bitbucket.org":
            if git_branch is None:
                if relative_path:
                    return f"{repo_url}/src/{relative_path}"
                else:
                    return f"{repo_url}"
            else:
                commit_id = get_git_commit_id_from_git_cli(p_git_repo_dir)
                return f"{repo_url}/src/{commit_id}/{relative_path}?at={git_branch}"
        else:  # bitbucket server
            if git_branch is None:
                if relative_path:
                    return f"{repo_url}/browse/{relative_path}"
                else:
                    return f"{repo_url}"
            else:
                return f"{repo_url}/browse/{relative_path}?at=refs/heads/{git_branch}"
    else:
        if git_branch is None:
            if relative_path:
                if path.is_file():
                    return f"{repo_url}/blob/{relative_path}"
                else:
                    return f"{repo_url}/tree/{relative_path}"
            else:
                return f"{repo_url}"
        else:
            if path.is_file():
                return f"{repo_url}/blob/{git_branch}/{relative_path}"
            else:
                return f"{repo_url}/tree/{git_branch}/{relative_path}"
