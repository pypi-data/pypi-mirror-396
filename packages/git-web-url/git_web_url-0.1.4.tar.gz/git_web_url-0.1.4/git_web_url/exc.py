# -*- coding: utf-8 -*-

class NotGitRepoError(FileNotFoundError):
    """
    Raises when the given path is not in a git repository.
    """
