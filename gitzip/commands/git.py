
import logging
import os
import shutil
import subprocess
import sys
from pathlib import Path
from subprocess import DEVNULL, STDOUT
from typing import Optional

from gitzip.lib.gitutil import git_get_gitzip_file
from gitzip.lib.testutil import chdir2tmp, create_files, shell, lstree

logger = logging.getLogger("git-zip-wrapper")


def main():
    """
    Script for wrapping around git to enable regular git commands in gitzip directories.

    Let us consider an example repository:

        >>> chdir2tmp()
        >>> create_files("main.c", "lib/string.h", "lib/string.c")

    Lacking a repository, the regular git executable will be invoked.

        >>> shell('git init')
        Initialized ...
        >>> shell('git branch -m main')

    When correctly installed -- the PATH entry with the wrapper script must
    come before the PATH entry with the actual git executable -- it will be
    invoked instead of the raw git command.

        >>> shell('git --verify-that-this-is-the-gitzip-wrapper')
        I verify, that I am the gitzip wrapper.
        >>> None

    Being not packed, the regular git commands work.

        >>> shell('git add .')
        >>> shell('git commit -m "initial commit"')
        [main ...] initial commit
         3 files changed, ...

    After packing, they work still, but now through implicitly invoking
    git zip do.

        >>> shell('git zip pack', stdout=DEVNULL)
        >>> shell('git commit --allow-empty -m "another commit"')
        [main ...] another commit

    """

    if len(sys.argv) == 2 and sys.argv[1] == '--verify-that-this-is-the-gitzip-wrapper':
        print("I verify, that I am the gitzip wrapper.", end="")
        # ^ end="" needed for the doctest to pass for some reason.
        return

    gitzip_file: Optional[Path] = git_get_gitzip_file()

    wrapper_path = Path(sys.argv[0]).absolute()
    original_path_list = [
        path for path in os.environ.get("PATH").split(os.pathsep)
        if Path(path).is_dir()]
    new_path_list = [
        path for path in original_path_list
        if not Path(path).samefile(wrapper_path.parent)]

    try:
        os.environ["PATH"] = os.pathsep.join(new_path_list)
        wrapped_git_executable: Optional[str] = shutil.which("git")
    finally:
        os.environ["PATH"] = os.pathsep.join(original_path_list)

    if wrapped_git_executable is None:
        logging.error("Cannot find git executable in:")
        for path in new_path_list:
            logging.error("  * %s", path)
        exit(1)

    if gitzip_file is None or not gitzip_file.exists():
        command = [wrapped_git_executable, *sys.argv[1:]]
    else:
        command = [wrapped_git_executable, "zip", "do", "--", *sys.argv[1:]]

    exit_code: int = subprocess.call(command)
    if exit_code != 0:
        exit(exit_code)
