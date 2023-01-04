import pathlib
import sys
import tempfile
from os import chdir, makedirs
from pathlib import Path
from subprocess import check_call, check_output
from typing import Optional


def git_get_root_directory(relative_to: Optional[Path] = None) -> Path:
    """
    :param relative_to:
        Path, for which the relevant git root should be obtained.
    :return:
        Root directory of a git repository, i.e. the parent directory of the
        .git directory.

    >>> tmpdir_obj = tempfile.TemporaryDirectory()
    >>> tmpdir = Path(tmpdir_obj.name)
    >>> repo_root = tmpdir / "root/git_repo"
    >>> subdir = repo_root / "some/sub/directory"
    >>> subdir.mkdir(parents=True)
    >>> check_call(["git", "init"], cwd=repo_root)
    0
    >>> git_get_root_directory(relative_to=subdir) == repo_root
    True
    >>> chdir(subdir)
    >>> git_get_root_directory() == repo_root
    True
    """
    output: str = check_output(
        ["git","rev-parse","--show-toplevel"],
        cwd=relative_to or Path.cwd(),
        encoding=sys.getdefaultencoding())
    return Path(output.strip())
