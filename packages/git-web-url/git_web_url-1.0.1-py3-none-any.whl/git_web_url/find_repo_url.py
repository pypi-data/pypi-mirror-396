# -*- coding: utf-8 -*-

"""
This module implements the logic to convert a remote origin url from the
``.git/config`` to a web url that you can use to open the repo in web browser.
Note that the url is the landing page of the repo, not the url of any folder
and file.
"""

from .parser import (
    PlatformEnum,
    ParseResult,
    parse,
)


def parse_aws_codecommit_remote_origin_url(remote_origin_url: str) -> str:
    """
    Extract the region from the remote origin url of AWS CodeCommit.

    :param remote_origin_url:
    :return: region
    """

    flag1 = remote_origin_url.startswith("https://git-codecommit")
    flag2 = remote_origin_url.startswith("ssh://git-codecommit")
    if flag1 or flag2:
        region = remote_origin_url.split("/")[2].split(".")[1]
    elif remote_origin_url.startswith("codecommit::"):
        region = remote_origin_url.split(":")[2]
    else:
        raise NotImplementedError
    return region


def get_aws_codecommit_repo_url(
    region: str,
    repo_name: str,
) -> str:
    return f"https://{region}.console.aws.amazon.com/codesuite/codecommit/repositories/{repo_name}"


def get_repo_url(
    remote_origin_url: str,
) -> tuple[str, ParseResult]:
    res = parse(remote_origin_url)
    # handler AWS Code Commit
    if res.platform is PlatformEnum.aws_codecommit:
        aws_region = parse_aws_codecommit_remote_origin_url(remote_origin_url)
        return get_aws_codecommit_repo_url(aws_region, res.repo), res
    if res.domain.startswith("bitbucket.") and (
        not res.domain.startswith("bitbucket.org")
    ):
        return f"https://{res.domain}/projects/{res.owner}/repos/{res.repo}", res
    else:
        return f"https://{res.domain}/{res.owner}/{res.repo}", res
