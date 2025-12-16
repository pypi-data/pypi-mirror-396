# -*- coding: utf-8 -*-

"""
Parse the remote origin url in the ``.git/config`` file.
"""

import typing as T
import re
import enum
import dataclasses


class ProtocolEnum(str, enum.Enum):
    """
    Supported protocols.
    """

    https = "https"
    ssh = "ssh"
    aws_codecommit = "aws_codecommit"


class PlatformEnum(str, enum.Enum):
    """
    Supported git platforms.
    """

    aws_codecommit = "aws_codecommit"
    bitbucket = "bitbucket"
    github = "github"
    gitlab = "gitlab"
    unknown = "unknown"


domain_patterns = {
    PlatformEnum.aws_codecommit: [
        "git-codecommit.[a-z]{2}-[a-z]+-[0-9].amazonaws.com$",
    ],
    PlatformEnum.bitbucket: [
        "bitbucket.org",
        "bitbucket.[a-zA-Z0-9-]+(.[a-zA-Z0-9-]+)*",
    ],
    PlatformEnum.github: [
        "github.com",
        "github.[a-zA-Z0-9-]+(.[a-zA-Z0-9-]+)*",
    ],
    PlatformEnum.gitlab: [
        "gitlab.com",
        "gitlab.[a-zA-Z0-9-]+(.[a-zA-Z0-9-]+)*",
    ],
}
for k, v in domain_patterns.items():
    domain_patterns[k] = [re.compile(p) for p in v]


@dataclasses.dataclass
class ParseResult:
    """
    The result of the :func:`parse`.
    """

    protocol: ProtocolEnum = dataclasses.field()
    platform: PlatformEnum = dataclasses.field()
    domain: str = dataclasses.field()
    owner: str = dataclasses.field()
    repo: str = dataclasses.field()


def parse(
    remote_origin_url: str,
    debug: bool = False,
) -> ParseResult:
    """
    Parse the remote origin url in the ``.git/config`` file.
    """
    # --- protocol
    git_at_ssh = False
    if remote_origin_url.startswith("https://"):
        protocol = ProtocolEnum.https
    elif remote_origin_url.startswith("ssh://"):
        protocol = ProtocolEnum.ssh
    elif remote_origin_url.startswith("git@"):
        protocol = ProtocolEnum.ssh
        git_at_ssh = True
    elif remote_origin_url.startswith("codecommit::"):
        protocol = ProtocolEnum.aws_codecommit
    else:
        raise NotImplementedError(f"unsupported protocol for {remote_origin_url}")

    if debug:  # pragma: no cover
        print(f"detect protocol: {protocol.value}")

    # --- domain
    parts = remote_origin_url.split("/")
    if protocol is ProtocolEnum.aws_codecommit:
        domain = ""
    else:
        if git_at_ssh:  # git@${domain}:${user}/${repo}.git
            domain = parts[0]
        else:  # common case
            domain = parts[2]
        if "@" in domain:
            domain = domain.split("@", 1)[1]
        if ":" in domain:
            domain = domain.split(":", 1)[0]

    if debug:  # pragma: no cover
        print(f"detect domain: {domain}")

    # --- platform
    platform = PlatformEnum.unknown
    if protocol is ProtocolEnum.aws_codecommit:
        platform = PlatformEnum.aws_codecommit
    else:
        for platform_candidate, patterns in domain_patterns.items():
            pattern: re.Pattern
            for pattern in patterns:
                if pattern.match(domain):
                    platform = platform_candidate
                    break

    if debug:  # pragma: no cover
        print(f"detect platform: {platform.value}")

    # --- owner and repo
    def extract_repo(repo_part: str) -> str:
        if repo_part.endswith(".git"):
            return repo_part[:-4]
        else:
            return repo_part

    def extract_owner_and_repo_for_github(
        owner_part: str,
        repo_part: str,
    ) -> T.Tuple[str, str]:
        """
        Extract owner and repo from the parts of the url.

        :param owner_part: could be "${owner}", "${domain}:${owner}"
        :param repo_part: could be "${repo}", "${repo}.git"
        """
        if protocol == ProtocolEnum.ssh:
            owner = owner_part.split(":")[-1]
            repo = extract_repo(repo_part)
        else:
            owner = owner_part
            repo = extract_repo(repo_part)
        return owner, repo

    if platform is PlatformEnum.aws_codecommit:
        owner = ""
        repo = extract_repo(parts[-1])
    elif platform in [
        PlatformEnum.github,
        PlatformEnum.gitlab,
    ]:
        if protocol is ProtocolEnum.ssh:
            owner, repo = extract_owner_and_repo_for_github(parts[2], parts[3])
        else:
            owner, repo = extract_owner_and_repo_for_github(parts[3], parts[4])
    elif platform is PlatformEnum.bitbucket:
        if protocol is ProtocolEnum.ssh:
            if git_at_ssh:
                owner, repo = extract_owner_and_repo_for_github(parts[0], parts[1])
            else:
                owner, repo = extract_owner_and_repo_for_github(parts[3], parts[4])
        else:
            owner, repo = extract_owner_and_repo_for_github(parts[3], parts[4])
    elif platform is PlatformEnum.unknown:
        owner, repo = None, None
        for owner_index, repo_index in [
            (3, 4),
            (2, 3),
        ]:
            try:
                owner, repo = extract_owner_and_repo_for_github(
                    parts[owner_index], parts[repo_index]
                )
                if debug:  # pragma: no cover
                    print(
                        f"found owner repo at index {(owner_index, repo_index)} in {parts}"
                    )
                break
            except Exception as e:
                # print(e)
                pass
        if repo is None:
            raise ValueError(
                "Cannot parse the remote origin url: {}".format(remote_origin_url)
            )
    else:
        raise NotImplementedError

    if debug:  # pragma: no cover
        print(f"detect owner: {owner}")
        print(f"detect repo: {repo}")

    result = ParseResult(
        protocol=protocol,
        platform=platform,
        domain=domain,
        owner=owner,
        repo=repo,
    )
    return result
