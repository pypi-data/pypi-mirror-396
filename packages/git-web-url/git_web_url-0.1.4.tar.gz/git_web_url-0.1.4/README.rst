
.. image:: https://readthedocs.org/projects/git-web-url/badge/?version=latest
    :target: https://git-web-url.readthedocs.io/en/latest/
    :alt: Documentation Status

.. image:: https://github.com/MacHu-GWU/git_web_url-project/actions/workflows/main.yml/badge.svg
    :target: https://github.com/MacHu-GWU/git_web_url-project/actions?query=workflow:CI

.. image:: https://codecov.io/gh/MacHu-GWU/git_web_url-project/branch/main/graph/badge.svg
    :target: https://codecov.io/gh/MacHu-GWU/git_web_url-project

.. image:: https://img.shields.io/pypi/v/git-web-url.svg
    :target: https://pypi.python.org/pypi/git-web-url

.. image:: https://img.shields.io/pypi/l/git-web-url.svg
    :target: https://pypi.python.org/pypi/git-web-url

.. image:: https://img.shields.io/pypi/pyversions/git-web-url.svg
    :target: https://pypi.python.org/pypi/git-web-url

.. image:: https://img.shields.io/badge/✍️_Release_History!--None.svg?style=social&logo=github
    :target: https://github.com/MacHu-GWU/git_web_url-project/blob/main/release-history.rst

.. image:: https://img.shields.io/badge/⭐_Star_me_on_GitHub!--None.svg?style=social&logo=github
    :target: https://github.com/MacHu-GWU/git_web_url-project

------

.. image:: https://img.shields.io/badge/Link-API-blue.svg
    :target: https://git-web-url.readthedocs.io/en/latest/py-modindex.html

.. image:: https://img.shields.io/badge/Link-Install-blue.svg
    :target: `install`_

.. image:: https://img.shields.io/badge/Link-GitHub-blue.svg
    :target: https://github.com/MacHu-GWU/git_web_url-project

.. image:: https://img.shields.io/badge/Link-Submit_Issue-blue.svg
    :target: https://github.com/MacHu-GWU/git_web_url-project/issues

.. image:: https://img.shields.io/badge/Link-Request_Feature-blue.svg
    :target: https://github.com/MacHu-GWU/git_web_url-project/issues

.. image:: https://img.shields.io/badge/Link-Download-blue.svg
    :target: https://pypi.org/pypi/git-web-url#files


Welcome to ``git_web_url`` Documentation
==============================================================================
.. image:: https://git-web-url.readthedocs.io/en/latest/_static/git_web_url-logo.png
    :target: https://git-web-url.readthedocs.io/en/latest/

``git_web_url`` is a CLI tool and also a Python library that prints the URL of a local file in a git repo so you can one-click to open it in web browser.

**Currently it supports**:

Git Hosting Services:

- GitHub
- GitHub Enterprise
- GitLab
- GitLab Enterprise
- BitBucket
- BitBucket Enterprise
- AWS CodeCommit

Git Clone Protocols:

- https
- ssh
- aws_codecommit (`git-remote-codecommit <https://docs.aws.amazon.com/codecommit/latest/userguide/setting-up-git-remote-codecommit.html>`_)


CLI Usage
------------------------------------------------------------------------------
**Basic Usage**

cd into your git repo directory, or any folder inside, then run ``gwu`` (or ``gitweburl``). It prints the URL for the current branch and current directory:

.. code-block:: bash

    $ gwu
    https://github.com/your_account/your_repo/tree/your_branch/path/to/current_directory

**Specify a File or Folder**

Provide the absolute path of the file or folder in your local git repo:

.. code-block:: bash

    $ gwu /path/to/your_repo/path/to/your_file.py
    https://github.com/your_account/your_repo/blob/your_branch/path/to/your_file.py

**Branch Options**

Use the ``--branch`` (or ``-b``) flag to control which branch appears in the URL:

.. code-block:: bash

    # Use current branch (default behavior)
    $ gwu
    https://github.com/your_account/your_repo/tree/feature-branch/

    # Use default branch (main/master) - URL without explicit branch
    $ gwu --branch=default
    https://github.com/your_account/your_repo

    # Use a specific branch
    $ gwu --branch=main
    https://github.com/your_account/your_repo/tree/main/

    # Short form
    $ gwu -b develop
    https://github.com/your_account/your_repo/tree/develop/


Python API Usage
------------------------------------------------------------------------------
You can also use ``git_web_url`` as a Python library:

.. code-block:: python

    from pathlib import Path
    import git_web_url.api as gwu

    # Get URL for a file using current branch
    url = gwu.get_web_url(Path("/path/to/your_repo/file.py"))

    # Get URL using default branch (main/master)
    url = gwu.get_web_url(
        Path("/path/to/your_repo/file.py"),
        branch=gwu.DEFAULT_BRANCH,
    )

    # Get URL using a specific branch
    url = gwu.get_web_url(
        Path("/path/to/your_repo/file.py"),
        branch="feature-branch",
    )


.. _install:

Install
------------------------------------------------------------------------------
``git_web_url`` is released on PyPI, so all you need is to:

.. code-block:: console

    $ pip install git-web-url

To upgrade to latest version:

.. code-block:: console

    $ pip install --upgrade git-web-url
