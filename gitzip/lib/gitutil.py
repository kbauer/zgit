import tempfile
from os import chdir
from pathlib import Path
from subprocess import DEVNULL
from typing import Optional
from unittest import TestCase

from gitzip.lib.testutil import shell, create_files, using_cwd, make_temporary_directory


def git_get_root_directory(relative_to: Optional[Path] = None) -> Optional[Path]:
    """
    :param relative_to:
        Path, for which the relevant git root should be obtained.
    :return:
        Root directory of a git repository, i.e. the parent directory of the
        .git directory. None, if not in a git tree.

    Consider some example repository,

        >>> repo_path = make_temporary_directory(prefix="git_get_root_directory.")
        >>> shell("git init", cwd=repo_path, stdout=DEVNULL)
        >>> create_files("some/sub/directory/file.txt", cwd=repo_path)

    Then for each directory and file, the .git directory is detected.

        >>> t = TestCase()
        >>> t.assertEqual(repo_path, git_get_root_directory(repo_path))
        >>> t.assertEqual(repo_path, git_get_root_directory(repo_path/"some/sub/directory"))
        >>> t.assertEqual(repo_path, git_get_root_directory(repo_path/"some/sub/directory/file.txt"))

    Without argument, the current working directory is used.

        >>> with using_cwd(repo_path):
        ...     t.assertEqual(repo_path, git_get_root_directory())
        >>> with using_cwd(repo_path/"some/sub/directory"):
        ...     t.assertEqual(repo_path, git_get_root_directory())

    """
    current: Path = (
        Path.cwd() if relative_to is None else
        relative_to)

    if current.joinpath(".git").exists():
        return current
    elif current.parent == current:  # reached root directory
        return None
    else:
        return git_get_root_directory(current.parent)


def git_get_gitzip_file(relative_to: Optional[Path] = None) -> Optional[Path]:
    f"""
    :param relative_to: As with C{git_get_root_directory()} 
    :return: Path where the git-zip archive file is expected.
    """
    root: Optional[Path] = git_get_root_directory(relative_to=relative_to)
    if root is None:
        return None
    return root / ".git/gitzip.tgz"
